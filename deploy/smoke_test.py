"""Synthetic local Docker/OIDC qualification. No tunnel, external accounts or real data.

Build both images first (see README). This script removes only its randomly named
Compose project, test volumes and temporary files. Requires optional OAuth deps.
"""
from __future__ import annotations
import base64
import hashlib
import http.cookiejar
from html.parser import HTMLParser
import ipaddress
import json
import os
from pathlib import Path
import secrets
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from refactoredmemory.store import Store
from refactoredmemory.mcp import PROTOCOL_VERSION, META_PREFIX
from refactoredmemory.sync import sync_once
from render_realm import CLIENTS, realm


def port():
    with socket.socket() as stream:
        stream.bind(("127.0.0.1", 0))
        return stream.getsockname()[1]


def write(path, data, mode=0o600):
    path.write_text(data)
    path.chmod(mode)


class Form(HTMLParser):
    action = None
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "form" and values.get("id") == "kc-form-login":
            self.action = values["action"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def main():
    if os.getuid() != 1000:
        raise SystemExit("This disposable Linux fixture requires UID 1000 for its Keycloak bind-mounted secrets.")
    env = os.environ.copy()
    for name in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
        env.pop(name, None)
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    def run(args, *, timeout=180):
        result = subprocess.run(args, env=env, text=True, capture_output=True, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f"Command failed ({args[0]}): {result.stderr[-3000:]}")
        return result.stdout
    project = "refmemtest" + secrets.token_hex(4)
    results = {"environment": "local Linux Docker; synthetic data only", "checks": []}
    with tempfile.TemporaryDirectory(prefix="refmem-docker-") as temp:
        private = Path(temp)
        for directory in ("data", "config/secrets", "tls", "auth"):
            (private / directory).mkdir(parents=True, mode=0o700)
        auth_port, mcp_port, sync_port = port(), port(), port()
        issuer = f"https://localhost:{auth_port}/realms/refactoredmemory"
        resource = f"https://localhost:{mcp_port}/mcp"
        subject, password = str(uuid.uuid4()), secrets.token_urlsafe(32)
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        now = datetime.now(timezone.utc)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "synthetic-local-only")])
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=1)).add_extension(x509.BasicConstraints(ca=True, path_length=0), True)
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(n) for n in ("localhost", "memory", "keycloak")]
                + [x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), False).sign(key, hashes.SHA256()))
        for service in ("memory", "keycloak"):
            write(private / f"tls/{service}.crt", cert.public_bytes(serialization.Encoding.PEM).decode(), 0o644)
            write(private / f"tls/{service}.key", key.private_bytes(serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode())
        write(private / "tls/ca.crt", cert.public_bytes(serialization.Encoding.PEM).decode(), 0o644)
        db_password = secrets.token_urlsafe(32)
        write(private / "auth/postgres-password", db_password, 0o444)
        write(private / "auth/keycloak-password", db_password)
        write(private / "auth/admin-password", secrets.token_urlsafe(32))
        callbacks = {c: ["https://localhost/callback"] for c in CLIENTS}
        synthetic_realm = realm(resource, callbacks)
        synthetic_realm["users"] = [{"id": subject, "username": "synthetic-owner", "enabled": True,
            "emailVerified": True, "firstName": "Synthetic", "lastName": "Owner",
            "email": "synthetic@example.invalid", "credentials": [{"type": "password", "value": password, "temporary": False}]}]
        write(private / "auth/realm.json", json.dumps(synthetic_realm))
        with Store(private / "data/memory.sqlite3", store_id="synthetic-docker", peer_id="synthetic-nas") as store, Store(private / "mac.sqlite3", store_id="synthetic-docker", peer_id="synthetic-mac") as mac:
            grant = store.create_grant("synthetic OAuth client", ["read", "write"], kind="agent")
            store.admit_peer(mac.peer_id, mac.identity()["key_hex"])
            mac.admit_peer(store.peer_id, store.identity()["key_hex"])
            peer_grant = store.create_grant("synthetic Mac", ["sync"], kind="peer", peer_id=mac.peer_id)
            mac.submit([{"type": "entity", "id": "offline", "entity_type": "note", "label": "Synthetic offline Mac note"}])
        write(private / "config/secrets/client.token", grant)
        write(private / "config/oauth.json", json.dumps({"issuer": issuer, "resource": resource,
            "jwks_file": "jwks.json", "bindings": [{"subject": subject, "client_id": CLIENTS[0], "grant_token_file": "secrets/client.token"}]}))
        write(private / "config.env", "\n".join([
            f"REFMEM_PRIVATE_DIR={private}", f"REFMEM_UID={os.getuid()}", f"REFMEM_GID={os.getgid()}",
            "REFMEM_MCP_HOST=localhost", "REFMEM_SYNC_HOST=localhost", f"REFMEM_SYNC_PORT={sync_port}",
            f"REFMEM_AUTH_HOST=localhost:{auth_port}", f"REFMEM_AUTH_ADMIN_HOST=localhost:{auth_port}",
            f"REFMEM_AUTH_ADMIN_PORT={auth_port}", "REFMEM_MIN_FREE_BYTES=0"]) + "\n")
        write(private / "mcp-ingress.cfg", (ROOT / "deploy/sync-ingress.cfg").read_text().replace("8766", "8765"), 0o644)
        write(private / "override.yaml", f"""services:
  test-mcp:
    image: haproxy:3.2.26-alpine@sha256:96ec3c75a9264ba94e733eeacb44051ed6e7b79bb77a73c2c36f236b6423f1f0
    user: '10001:10001'
    read_only: true
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
    pids_limit: 32
    mem_limit: 64m
    cpus: 0.25
    volumes:
      - {private}/mcp-ingress.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    ports:
      - '127.0.0.1:{mcp_port}:8765'
    networks: [backend, private_ingress]
""")
        compose = docker + ["compose", "-p", project, "--env-file", str(private / "config.env"),
            "-f", str(ROOT / "deploy/compose.yaml"), "-f", str(ROOT / "deploy/compose.oidc.yaml"), "-f", str(private / "override.yaml")]
        context = ssl.create_default_context(cafile=str(private / "tls/ca.crt"))
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=context),
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect())
        def request(url, body=None, headers=None):
            req = urllib.request.Request(url, data=body, headers=headers or {})
            try:
                response = opener.open(req, timeout=10)
            except urllib.error.HTTPError as error:
                response = error
            return response.status, dict(response.headers), response.read()
        def ready(url, expected=200):
            deadline = time.monotonic() + 180
            while time.monotonic() < deadline:
                try:
                    status, _, body = request(url)
                    if status == expected:
                        return body
                except (OSError, urllib.error.URLError):
                    pass
                time.sleep(1)
            raise RuntimeError("Local service failed readiness check")
        try:
            run(compose + ["config", "--quiet"])
            run(compose + ["up", "--no-build", "-d", "postgres", "keycloak", "auth-admin-ingress"])
            discovery = json.loads(ready(issuer + "/.well-known/openid-configuration"))
            status, _, jwks = request(discovery["jwks_uri"])
            assert status == 200
            signing_keys = [k for k in json.loads(jwks)["keys"] if k.get("use") == "sig" and k.get("alg") == "RS256"]
            write(private / "config/jwks.json", json.dumps({"keys": signing_keys}), 0o644)
            verifier, state = secrets.token_urlsafe(48), secrets.token_urlsafe(24)
            challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
            auth_query = urllib.parse.urlencode({"client_id": CLIENTS[0], "response_type": "code",
                "redirect_uri": callbacks[CLIENTS[0]][0], "scope": "openid memory:read memory:write",
                "code_challenge": challenge, "code_challenge_method": "S256", "state": state})
            without_pkce = urllib.parse.urlencode({"client_id": CLIENTS[0], "response_type": "code",
                "redirect_uri": callbacks[CLIENTS[0]][0], "scope": "openid", "state": state})
            missing_status, missing_headers, _ = request(discovery["authorization_endpoint"] + "?" + without_pkce)
            assert missing_status in (302, 400)
            if missing_status == 302:
                missing_result = urllib.parse.parse_qs(urllib.parse.urlparse(missing_headers["Location"]).query)
                assert "error" in missing_result and "code" not in missing_result, "Authorization accepted without PKCE"
            status, _, body = request(discovery["authorization_endpoint"] + "?" + auth_query)
            assert status == 200, "OIDC authorization page unavailable"
            form = Form(); form.feed(body.decode())
            assert form.action, "OIDC owner login form unavailable"
            status, headers, _ = request(form.action, urllib.parse.urlencode({"username": "synthetic-owner", "password": password}).encode(),
                {"Content-Type": "application/x-www-form-urlencoded"})
            assert status == 302, "Synthetic owner login failed"
            returned = urllib.parse.parse_qs(urllib.parse.urlparse(headers["Location"]).query)
            assert returned.get("state") == [state] and "code" in returned
            def exchange(code_verifier):
                return request(discovery["token_endpoint"], urllib.parse.urlencode({"grant_type": "authorization_code",
                    "code": returned["code"][0], "client_id": CLIENTS[0], "redirect_uri": callbacks[CLIENTS[0]][0],
                    "code_verifier": code_verifier}).encode(), {"Content-Type": "application/x-www-form-urlencoded"})
            status, _, body = exchange(verifier)
            assert status == 200, "PKCE code exchange failed"
            token_result = json.loads(body); token = token_result["access_token"]
            assert exchange(verifier)[0] == 400, "Authorization code replay accepted"
            results["checks"].extend(["real Keycloak/Postgres TLS authorization-code + S256 PKCE", "missing PKCE and authorization-code replay rejected"])
            run(compose + ["up", "--no-build", "-d", "memory", "sync-ingress", "test-mcp"])
            ready(f"https://localhost:{mcp_port}/.well-known/oauth-protected-resource/mcp")
            def mcp(access_token, method="server/discover", params=None, path="/mcp", endpoint=mcp_port):
                payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": {**(params or {}), "_meta": {
                    META_PREFIX + "protocolVersion": PROTOCOL_VERSION, META_PREFIX + "clientCapabilities": {}}}}
                headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                    "MCP-Protocol-Version": PROTOCOL_VERSION, "Mcp-Method": method}
                if method == "tools/call":
                    headers["Mcp-Name"] = params["name"]
                return request(f"https://localhost:{endpoint}{path}", json.dumps(payload).encode(), headers)
            assert mcp(token)[0] == 200, "Real access token rejected by MCP resource"
            assert mcp(token_result["id_token"])[0] == 401, "ID token accepted"
            assert mcp(grant)[0] == 401, "Raw local grant accepted on public OAuth listener"
            assert mcp(peer_grant)[0] == 401, "Peer grant accepted on public OAuth listener"
            assert mcp(token, path="/sync")[0] == 404, "Public listener exposes sync"
            assert mcp(token, endpoint=sync_port)[0] == 404, "Private sync listener exposes MCP"
            results["checks"].extend(["real OAuth access token accepted at MCP", "ID token and raw local grant rejected", "MCP/sync listener separation"])
            status, _, body = mcp(token, "tools/call", {"name": "memory_submit", "arguments": {"request_id": "synthetic-docker-capture", "actions": [
                {"type": "entity", "id": "note", "entity_type": "note", "label": "Synthetic container note"},
                {"type": "source", "id": "source", "uri": "synthetic://docker", "content": "Synthetic test evidence"},
                {"type": "assertion", "id": "fact", "subject": "note", "predicate": "content", "value": "Synthetic retained value", "source_ids": ["source"]}
            ]}})
            assert status == 200 and not json.loads(body)["result"].get("isError"), "OAuth capture failed"
            def query():
                status, _, body = mcp(token, "tools/call", {"name": "memory_query", "arguments": {"subject": "note"}})
                assert status == 200 and not json.loads(body)["result"].get("isError")
                assert "Synthetic retained value" in body.decode()
            query()
            previous_ca = os.environ.get("SSL_CERT_FILE")
            os.environ["SSL_CERT_FILE"] = str(private / "tls/ca.crt")
            try:
                with Store(private / "mac.sqlite3") as mac:
                    synchronized = sync_once(mac, f"https://localhost:{sync_port}/sync", peer_grant, expected_peer="synthetic-nas")
                    assert synchronized["complete"], "Private TLS sync did not converge"
                    assert mac.query(subject="note"), "Mac did not receive NAS assertion"
            finally:
                if previous_ca is None:
                    os.environ.pop("SSL_CERT_FILE", None)
                else:
                    os.environ["SSL_CERT_FILE"] = previous_ca
            with Store(private / "data/memory.sqlite3") as store:
                assert store.status()["frontier"].get("synthetic-mac"), "NAS did not receive offline Mac write"
            results["checks"].extend(["OAuth sourced capture and query", "private TLS bidirectional offline sync converges"])
            cid = run(compose + ["ps", "-q", "memory"]).strip()
            config = json.loads(run(docker + ["inspect", cid]))[0]
            assert config["Config"]["User"] == f"{os.getuid()}:{os.getgid()}"
            assert config["HostConfig"]["ReadonlyRootfs"] and "ALL" in config["HostConfig"]["CapDrop"]
            assert "no-new-privileges:true" in config["HostConfig"]["SecurityOpt"]
            assert len(config["NetworkSettings"]["Networks"]) == 1
            assert all(m["Destination"] in ("/data", "/config", "/tls") for m in config["Mounts"])
            run(docker + ["exec", cid, "python", "-c", "import os; assert os.geteuid()!=0; assert open('/proc/self/status').read().split('CapEff:')[1].split()[0]=='0000000000000000'"])
            keycloak_cid = run(compose + ["ps", "-q", "keycloak"]).strip()
            keycloak_info = json.loads(run(docker + ["inspect", keycloak_cid]))[0]
            forbidden_ip = next(iter(keycloak_info["NetworkSettings"]["Networks"].values()))["IPAddress"]
            probe = "import socket,sys\ns=socket.socket();s.settimeout(2)\ntry:s.connect((sys.argv[1],8443))\nexcept OSError:sys.exit(0)\nsys.exit('Unexpected connection to isolated authorization network')"
            run(docker + ["exec", cid, "python", "-c", probe, forbidden_ip])
            results["checks"].extend(["nonroot/read-only/capability/mount hardening inspected", "memory cannot initiate connection into separate authorization network"])
            run(compose + ["restart", "memory"])
            ready(f"https://localhost:{mcp_port}/.well-known/oauth-protected-resource/mcp")
            assert mcp(token)[0] == 200
            query()
            with Store(private / "data/memory.sqlite3") as store:
                store.revoke_grant(grant)
            assert mcp(token)[0] == 401, "Grant revocation did not take effect immediately"
            results["checks"].extend(["acknowledged assertion queried after container restart", "live grant revocation rejects existing OAuth access token"])
            results["limitations"] = ["No actual NAS/VLAN/router/firewall qualification", "No external tunnel or provider-app login", "Synthetic owner bypasses production MFA enrollment only in disposable test realm"]
            print(json.dumps(results, indent=2))
        except BaseException:
            print(run(compose + ["logs", "--tail", "40", "keycloak", "postgres", "memory"]), file=sys.stderr)
            raise
        finally:
            run(compose + ["down", "--volumes", "--remove-orphans"])


if __name__ == "__main__":
    main()
