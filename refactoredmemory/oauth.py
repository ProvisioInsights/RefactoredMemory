"""Optional OAuth resource authentication; token issuance belongs to the IdP.

The core package remains standard-library only. PyJWT and its cryptographic
backend are loaded only when this resource-server profile is configured.
All trust and grant files are administrator-selected local paths. A token can
never choose a key URL, discover a different issuer, or create its own grant.
"""
from __future__ import annotations

import base64
import json
import math
import os
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit

from .store import AuthorizationError, ValidationError


SCOPE_MAP = {"memory:read": "read", "memory:write": "write", "memory:correct": "correct"}
MAX_TOKEN_BYTES = 16384
MAX_CONFIG_BYTES = 65536
MAX_JWKS_BYTES = 262144
_B64 = re.compile(r"^[A-Za-z0-9_-]+$")


class OAuthConfigurationError(ValidationError):
    """Trusted local configuration is invalid or unavailable; fail closed."""


class OAuthAuthenticationError(AuthorizationError):
    status = 401
    error = "invalid_token"
    scope = None

    def __init__(self):
        super().__init__("Invalid or unbound OAuth access token")


class OAuthScopeError(AuthorizationError):
    status = 403
    error = "insufficient_scope"

    def __init__(self, scope="memory:read"):
        if scope not in SCOPE_MAP:
            raise ValueError("Unknown OAuth scope")
        self.scope = scope
        super().__init__("OAuth access token lacks the required scope")


def _json_object(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON member")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("Nonfinite JSON number")

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Nonfinite JSON number")
        return number

    result = json.loads(data, object_pairs_hook=pairs, parse_constant=constant,
                        parse_float=finite_float)
    if not isinstance(result, dict):
        raise ValueError("Object required")
    return result


def _read_file(path, limit, *, private=False):
    """Read a bounded regular file, refusing final-component symlinks.

    Parent directories are part of the trusted administrator-selected path.
    Atomic replacement supports key rotation without accepting token URLs.
    """
    try:
        if Path(path).is_symlink():
            raise ValueError("Symlink refused")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                             | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
                raise ValueError("File is not a bounded regular file")
            if private and (stat.S_IMODE(info.st_mode) & 0o077
                            or info.st_uid != os.geteuid()):
                raise ValueError("Private file must be owned by the runtime user")
            data = stream.read(limit + 1)
            if len(data) > limit:
                raise ValueError("File exceeds bounds")
            return data
    except (OSError, ValueError):
        # Do not expose a path, credential, key body or filesystem exception.
        raise OAuthConfigurationError("OAuth trust or grant file is unavailable or unsafe") from None


def _text(value, maximum=2048):
    return (isinstance(value, str) and 0 < len(value) <= maximum
            and not any(ord(character) < 32 or ord(character) == 127 for character in value))


def _https_url(value):
    if not _text(value) or not value.isascii() or any(c in value for c in ('"', "\\", " ")):
        raise ValueError("Invalid HTTPS URL")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment):
        raise ValueError("Invalid HTTPS URL")
    _ = parsed.port  # Validate a supplied port rather than reflecting it in headers.
    return parsed


def _local_path(value, directory):
    if not _text(value, 4096) or "\x00" in value:
        raise ValueError("Invalid local path")
    # Do not resolve the final symlink: _read_file must be able to refuse it.
    return Path(os.path.abspath(directory / value))


class OAuthAuthenticator:
    """Verify a narrow access-token profile and intersect current local grants.

    Supported access tokens use RS256 with an explicit access-token indicator:
    an ``at+jwt`` header, Keycloak's signed ``typ: Bearer``, or signed
    ``token_use: access``. Identity tokens and bare opaque credentials are refused.
    Bindings and issuer policy are fixed at startup. JWKS and private grant files
    are read again for each call, and Store checks revocation on every call.
    """

    def __init__(self, store, config_path):
        try:
            import jwt
            from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
        except ImportError:
            raise OAuthConfigurationError("OAuth support requires the declared oauth dependencies") from None
        self._jwt = jwt
        self._rsa_type = RSAPublicKey
        self._store = store
        config_path = Path(os.path.abspath(config_path))
        self._config_path = config_path
        try:
            config = _json_object(_read_file(config_path, MAX_CONFIG_BYTES))
            required = {"issuer", "resource", "jwks_file", "bindings"}
            if not required <= config.keys() or config.keys() - required - {
                "max_token_lifetime_seconds", "clock_skew_seconds",
            }:
                raise ValueError("Invalid configuration fields")
            self.issuer = config["issuer"]
            _https_url(self.issuer)
            self.resource = config["resource"]
            resource_url = _https_url(self.resource)
            if resource_url.path != "/mcp":
                raise ValueError("Resource must name the MCP endpoint")
            self.metadata_path = "/.well-known/oauth-protected-resource/mcp"
            self.metadata_url = f"{resource_url.scheme}://{resource_url.netloc}{self.metadata_path}"
            self.max_token_lifetime = config.get("max_token_lifetime_seconds", 300)
            self.clock_skew = config.get("clock_skew_seconds", 5)
            if (type(self.max_token_lifetime) is not int or not 1 <= self.max_token_lifetime <= 300
                    or type(self.clock_skew) is not int or not 0 <= self.clock_skew <= 30):
                raise ValueError("Invalid token timing policy")
            self._jwks_file = _local_path(config["jwks_file"], config_path.parent)
            entries = config["bindings"]
            if not isinstance(entries, list) or not 1 <= len(entries) <= 32:
                raise ValueError("Invalid connection bindings")
            self._bindings = {}
            grant_paths = set()
            for entry in entries:
                if not isinstance(entry, dict) or set(entry) != {"subject", "client_id", "grant_token_file"}:
                    raise ValueError("Invalid connection binding")
                if not _text(entry["subject"], 255) or not _text(entry["client_id"]):
                    raise ValueError("Invalid connection identity")
                identity = (entry["subject"], entry["client_id"])
                grant_path = _local_path(entry["grant_token_file"], config_path.parent)
                if identity in self._bindings or grant_path in grant_paths:
                    raise ValueError("Duplicate connection binding")
                self._bindings[identity] = grant_path
                grant_paths.add(grant_path)
            self._keys()  # Refuse an invalid trust configuration before listening.
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
            raise OAuthConfigurationError("Invalid OAuth resource configuration") from None

    @property
    def local_files(self):
        """Read-only path inventory for startup output/input collision checks."""
        return (self._config_path, self._jwks_file, *self._bindings.values())

    def resource_metadata(self):
        return {"resource": self.resource, "resource_name": "RefactoredMemory",
                "authorization_servers": [self.issuer],
                "scopes_supported": list(SCOPE_MAP), "bearer_methods_supported": ["header"]}

    def www_authenticate(self, error=None, scope=None):
        if error not in (None, "invalid_token", "insufficient_scope"):
            raise ValueError("Unknown OAuth challenge")
        parts = ['Bearer realm="RefactoredMemory"', f'resource_metadata="{self.metadata_url}"']
        if error:
            parts.append(f'error="{error}"')
        if scope is not None:
            if scope not in SCOPE_MAP:
                raise ValueError("Unknown OAuth scope")
            parts.append(f'scope="{scope}"')
        return ", ".join(parts)

    def _keys(self):
        try:
            document = _json_object(_read_file(self._jwks_file, MAX_JWKS_BYTES))
            items = document.get("keys")
            if not isinstance(items, list) or not 1 <= len(items) <= 16:
                raise ValueError("Invalid JWKS")
            keys = {}
            for item in items:
                if (not isinstance(item, dict) or item.get("kty") != "RSA"
                        or not _text(item.get("kid"), 256)
                        or item["kid"] in keys or item.get("alg", "RS256") != "RS256"
                        or item.get("use", "sig") != "sig"
                        or item.get("key_ops", ["verify"]) != ["verify"]
                        or {"d", "p", "q", "dp", "dq", "qi", "oth"} & item.keys()):
                    raise ValueError("Invalid verification key")
                if (not _text(item.get("n"), 1500) or not _B64.fullmatch(item["n"])
                        or not _text(item.get("e"), 12) or not _B64.fullmatch(item["e"])):
                    raise ValueError("Invalid RSA public parameters")
                key = self._jwt.PyJWK.from_dict(item, algorithm="RS256").key
                if not isinstance(key, self._rsa_type) or not 2048 <= key.key_size <= 8192:
                    raise ValueError("Invalid RSA key size")
                keys[item["kid"]] = key
            return keys
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, self._jwt.PyJWTError):
            raise OAuthConfigurationError("OAuth verification keys are unavailable or invalid") from None

    def _claims(self, token):
        try:
            if not isinstance(token, str) or not token.isascii() or len(token) > MAX_TOKEN_BYTES:
                raise ValueError("Invalid token")
            parts = token.split(".")
            if len(parts) != 3 or not all(_B64.fullmatch(part) for part in parts):
                raise ValueError("Invalid compact token")
            header, claims = [_json_object(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
                              for part in parts[:2]]
            if (header.get("alg") != "RS256" or not _text(header.get("kid"), 256)
                    or header.get("typ") not in ("JWT", "at+jwt", "application/at+jwt")
                    or {"crit", "jku", "jwk", "x5u", "x5c", "b64"} & header.keys()):
                raise ValueError("Unsupported token header")
            # Reject explicit identity-token markers even if another marker says access.
            if ("token_use" in claims and claims["token_use"] != "access"
                    or "typ" in claims and claims["typ"] not in ("Bearer", "access", "at+jwt", "application/at+jwt")):
                raise ValueError("Not an access token")
            if not (header["typ"] in ("at+jwt", "application/at+jwt")
                    or claims.get("typ") == "Bearer" or claims.get("token_use") == "access"):
                raise ValueError("Access-token indicator required")
            for name in ("exp", "iat", "nbf"):
                if name not in claims and name == "nbf":
                    continue
                value = claims.get(name)
                if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 2**53:
                    raise ValueError("Invalid token time")
            if (not 0 < claims["exp"] - claims["iat"] <= self.max_token_lifetime
                    or claims.get("nbf", claims["iat"]) >= claims["exp"]):
                raise ValueError("Token lifetime exceeds policy")
            if not _text(claims.get("sub"), 255):
                raise ValueError("Token subject required")
            client_id = claims.get("azp", claims.get("client_id"))
            if (not _text(client_id) or "azp" in claims and "client_id" in claims
                    and claims["azp"] != claims["client_id"]):
                raise ValueError("Token client identity required")
            scopes = claims.get("scope")
            if not isinstance(scopes, str) or len(scopes) > 4096 or any(ord(c) < 32 or ord(c) > 126 for c in scopes):
                raise ValueError("Token scope required")
            key = self._keys().get(header["kid"])
            if key is None:
                raise ValueError("Unknown verification key")
            verified = self._jwt.decode(token, key, algorithms=["RS256"], issuer=self.issuer,
                                        audience=self.resource, leeway=self.clock_skew,
                                        options={"require": ["exp", "iat", "iss", "aud", "sub"]})
            return verified, client_id
        except OAuthConfigurationError:
            raise
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, OverflowError, self._jwt.PyJWTError):
            raise OAuthAuthenticationError() from None

    def __call__(self, token, scope=None):
        claims, client_id = self._claims(token)
        path = self._bindings.get((claims["sub"], client_id))
        if path is None:
            raise OAuthAuthenticationError()
        try:
            grant_token = _read_file(path, 1024, private=True).decode("ascii").strip()
            if not grant_token or any(character.isspace() for character in grant_token):
                raise OAuthConfigurationError("OAuth grant file is invalid")
            actor = self._store.authenticate(grant_token)
        except (AuthorizationError, UnicodeError):
            raise OAuthAuthenticationError() from None
        if actor["kind"] != "agent":
            raise OAuthAuthenticationError()
        token_scopes = {SCOPE_MAP[value] for value in claims["scope"].split() if value in SCOPE_MAP}
        if not token_scopes:
            raise OAuthScopeError()
        if scope is not None and scope not in token_scopes:
            required = next((external for external, internal in SCOPE_MAP.items() if internal == scope), None)
            if required is None:
                raise OAuthAuthenticationError()
            raise OAuthScopeError(required)
        if scope is not None and scope not in actor["scopes"]:
            # Reauthorization cannot widen a locally restricted grant.
            raise AuthorizationError("Access denied by the current local grant")
        effective = token_scopes & set(actor["scopes"])
        if not effective:
            raise OAuthAuthenticationError()
        return {**actor, "scopes": sorted(effective)}

    authenticate = __call__
