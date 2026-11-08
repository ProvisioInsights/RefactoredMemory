"""Bounded, private HTTP audit records without request or credential content."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
import sys
import threading

from .service import TOOLS
from .store import ValidationError, utcnow

_FIELDS = {"time", "event", "request_id", "route", "method", "tool", "grant_id", "status"}
_METHODS = {"server/discover", "initialize", "notifications/initialized", "ping", "tools/list",
            "tools/call", "resources/list", "resources/read", "prompts/list", "unknown"}
_TOOLS = {tool["name"] for tool in TOOLS} | {"unknown"}


class AuditLog:
    """Two-file log; startup fails closed, runtime sink failures are observable.

    The parent directory is an administrator-owned runtime path. Each record is
    reconstructed from an allowlist rather than serializing an arbitrary event.
    """

    def __init__(self, path, *, max_bytes=1024 * 1024):
        self.path = Path(path).absolute()
        self.backup = self.path.with_name(self.path.name + ".1")
        self.max_bytes = max_bytes
        self.failures = 0
        self._lock = threading.Lock()
        self._closed = False
        self._descriptor = None
        if type(max_bytes) is not int or not 1024 <= max_bytes <= 64 * 1024 * 1024:
            raise ValidationError("Invalid audit file size limit")
        try:
            parent = self.path.parent.stat()
            if parent.st_uid != os.geteuid() or parent.st_mode & 0o022:
                raise ValueError("Untrusted audit directory")
            self._check_file(self.backup, missing_ok=True)
            if self.backup.exists():
                backup_fd = os.open(self.backup, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                try:
                    self._validate_content(backup_fd)
                finally:
                    os.close(backup_fd)
            self._descriptor = self._open()
        except (OSError, ValueError, TypeError):
            raise ValidationError("Audit path must be a private regular runtime file") from None

    def _check_file(self, path, *, missing_ok=False):
        try:
            info = path.lstat()
        except FileNotFoundError:
            if missing_ok:
                return
            raise
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or info.st_mode & 0o077 or info.st_nlink != 1):
            raise ValueError("Unsafe audit file")

    def _open(self):
        self._check_file(self.path, missing_ok=True)
        descriptor = os.open(self.path, os.O_RDWR | os.O_APPEND | os.O_CREAT
                             | getattr(os, "O_NOFOLLOW", 0), 0o600)
        info = os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or info.st_mode & 0o077 or info.st_nlink != 1):
            os.close(descriptor)
            raise ValueError("Unsafe audit file")
        try:
            self._validate_content(descriptor)
        except (OSError, ValueError, TypeError):
            os.close(descriptor)
            raise
        return descriptor

    def _validate_content(self, descriptor):
        """Never append to or rotate an unrelated private file."""
        data = os.pread(descriptor, self.max_bytes + 1, 0)
        if len(data) > self.max_bytes or data and not data.endswith(b"\n"):
            raise ValueError("Not a bounded complete audit log")
        for line in data.splitlines():
            record = json.loads(line)
            if (not isinstance(record, dict) or set(record) != _FIELDS
                    or record.get("event") != "mcp_http"
                    or not isinstance(record.get("time"), str)
                    or not re.fullmatch(r"[0-9T:.+Z-]{20,40}", record["time"])
                    or record.get("route") not in ("mcp", "metadata", "unknown")
                    or record.get("method") is not None and record["method"] not in _METHODS
                    or record.get("tool") is not None and record["tool"] not in _TOOLS
                    or record.get("request_id") is not None and (not isinstance(record["request_id"], str) or not re.fullmatch(r"[a-f0-9]{32}", record["request_id"]))
                    or record.get("grant_id") is not None and (not isinstance(record["grant_id"], str) or not re.fullmatch(r"[a-f0-9-]{1,64}", record["grant_id"]))
                    or record.get("status") is not None and (type(record["status"]) is not int or not 100 <= record["status"] <= 599)):
                raise ValueError("Not a recognized audit record")

    def __call__(self, event):
        # Never accept a timestamp, URL, source label, IP address or raw payload.
        if not isinstance(event, dict):
            return
        identifier = event.get("request_id")
        grant_id = event.get("grant_id")
        method = event.get("method")
        tool = event.get("tool")
        record = {
            "time": utcnow(), "event": "mcp_http",
            "request_id": identifier if isinstance(identifier, str) and re.fullmatch(r"[a-f0-9]{32}", identifier) else None,
            "route": event.get("route") if isinstance(event.get("route"), str) and event["route"] in {"mcp", "metadata", "unknown"} else "unknown",
            "method": method if method is None or isinstance(method, str) and method in _METHODS else "unknown",
            "tool": tool if tool is None or isinstance(tool, str) and tool in _TOOLS else "unknown",
            "grant_id": grant_id if isinstance(grant_id, str) and re.fullmatch(r"[a-f0-9-]{1,64}", grant_id) else None,
            "status": event.get("status") if type(event.get("status")) is int and 100 <= event["status"] <= 599 else None,
        }
        encoded = (json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n").encode()
        with self._lock:
            if self._closed:
                return
            try:
                if self._descriptor is None:
                    self._descriptor = self._open()
                if os.fstat(self._descriptor).st_size + len(encoded) > self.max_bytes:
                    self._check_file(self.path)
                    self._check_file(self.backup, missing_ok=True)
                    os.close(self._descriptor)
                    self._descriptor = None
                    os.replace(self.path, self.backup)
                    self._descriptor = self._open()
                # Handle an unusual partial regular-file write without writing
                # a second event over an incomplete record.
                remaining = memoryview(encoded)
                while remaining:
                    count = os.write(self._descriptor, remaining)
                    if count <= 0:
                        raise OSError("Audit write made no progress")
                    remaining = remaining[count:]
            except (OSError, ValueError, TypeError):
                self.failures += 1
                if self.failures == 1:
                    print("RefactoredMemory: audit sink unavailable; inspect private runtime storage", file=sys.stderr)

    def close(self):
        with self._lock:
            self._closed = True
            if self._descriptor is not None:
                os.close(self._descriptor)
                self._descriptor = None

