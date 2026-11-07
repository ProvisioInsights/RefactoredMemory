"""Real-signature OAuth resource tests using only ephemeral synthetic identities."""
import base64
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

try:
    import jwt
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
except ImportError:
    jwt = None

from refactoredmemory.oauth import (
    OAuthAuthenticator, OAuthAuthenticationError, OAuthConfigurationError,
    OAuthScopeError, SCOPE_MAP,
)
from refactoredmemory.service import Service
from refactoredmemory.store import AuthorizationError, Store


class OptionalDependencyTests(unittest.TestCase):
    def test_importing_core_does_not_import_crypto_dependencies(self):
        code = """
import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name == 'jwt' or name.startswith('cryptography'):
        raise ImportError('Synthetic optional dependency absence')
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from refactoredmemory.oauth import OAuthAuthenticator, OAuthConfigurationError
from refactoredmemory.service import Service
from refactoredmemory.mcp import Dispatcher
try:
    OAuthAuthenticator(None, 'synthetic-nonexistent')
except OAuthConfigurationError as error:
    assert 'dependencies' in str(error)
else:
    raise AssertionError('OAuth did not fail closed without dependencies')
"""
        completed = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)


@unittest.skipUnless(jwt, "Install the declared oauth extra to run real-signature tests")
class OAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.next_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="refmem-synthetic-oauth-")
        self.path = Path(self.temp.name)
        self.store = Store(self.path / "memory.sqlite3", store_id="synthetic-owner", peer_id="synthetic-peer")
        self.grant = self.store.create_grant("synthetic-oauth-client", ["read", "write", "correct"])
        self.grant_file = self.path / "client.token"
        self.set_grant(self.grant)
        self.jwk = self.public_key(self.key, "synthetic-key")
        self.set_keys([self.jwk])
        self.config = {
            "issuer": "https://identity.synthetic/realms/refactoredmemory",
            "resource": "https://memory.synthetic/mcp",
            "jwks_file": "jwks.json", "clock_skew_seconds": 0,
            "max_token_lifetime_seconds": 300,
            "bindings": [{"subject": "synthetic-subject", "client_id": "synthetic-client",
                          "grant_token_file": "client.token"}],
        }
        self.configure()

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    @staticmethod
    def public_key(key, kid):
        return {**jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key(), as_dict=True),
                "kid": kid, "alg": "RS256", "use": "sig", "key_ops": ["verify"]}

    def set_grant(self, token):
        self.grant_file.write_text(token + "\n")
        self.grant_file.chmod(0o600)

    def set_keys(self, keys):
        (self.path / "jwks.json").write_text(json.dumps({"keys": keys}))

    def configure(self, config=None):
        (self.path / "oauth.json").write_text(json.dumps(config or self.config))
        self.auth = OAuthAuthenticator(self.store, self.path / "oauth.json")
        self.service = Service(self.store, authenticate=self.auth)
        return self.auth

    def claims(self):
        now = int(time.time())
        return {"iss": self.config["issuer"], "aud": self.config["resource"],
                "sub": "synthetic-subject", "azp": "synthetic-client",
                "iat": now - 1, "exp": now + 200, "typ": "Bearer",
                "scope": "memory:read memory:write memory:correct"}

    def token(self, updates=None, *, remove=(), headers=None, key=None):
        claims = {**self.claims(), **(updates or {})}
        for name in remove:
            claims.pop(name, None)
        return jwt.encode(claims, key or self.key, algorithm="RS256",
                          headers={"kid": "synthetic-key", "typ": "JWT", **(headers or {})})

    def raw_token(self, header_text, claims_text):
        def encode(value):
            return base64.urlsafe_b64encode(value).rstrip(b"=")
        payload = encode(header_text.encode()) + b"." + encode(claims_text.encode())
        signature = self.key.sign(payload, padding.PKCS1v15(), hashes.SHA256())
        return (payload + b"." + encode(signature)).decode()

    def test_authenticated_capture_preserves_agent_provenance_and_evidence(self):
        token = self.token()
        actor = self.auth(token, "write")
        self.assertEqual(actor["kind"], "agent")
        self.assertEqual(set(actor["scopes"]), {"read", "write", "correct"})
        actions = [
            {"type": "entity", "id": "project", "entity_type": "project", "label": "Synthetic project"},
            {"type": "source", "id": "evidence", "uri": "synthetic://meeting", "content": "Use local storage."},
            {"type": "assertion", "id": "decision", "subject": "project", "predicate": "decision",
             "value": "Use local storage", "source_ids": ["evidence"]},
        ]
        arguments = {"actions": actions, "request_id": "synthetic-idempotency-key"}
        result = self.service.call("memory_submit", arguments, token)
        repeat = self.service.call("memory_submit", arguments, token)
        self.assertEqual(result["operation_id"], repeat["operation_id"])
        fact = self.service.call("memory_query", {"subject": "project"}, token)["assertions"][0]
        self.assertEqual(fact["actor"]["id"], actor["id"])
        self.assertEqual(fact["actor"]["kind"], "agent")
        self.assertEqual(fact["source_ids"], ["evidence"])
        self.assertNotEqual(fact.get("human_verified"), True)
        self.assertEqual(self.service.call("memory_source", {"source_id": "evidence"}, token)["source"]["content"],
                         "Use local storage.")

    def test_signature_algorithm_and_token_selected_keys_are_rejected(self):
        tokens = [self.token(key=self.next_key), self.token(headers={"kid": "unknown-key"}),
                  jwt.encode(self.claims(), "synthetic-shared-secret" * 3, algorithm="HS256",
                             headers={"kid": "synthetic-key"}),
                  jwt.encode(self.claims(), "", algorithm="none", headers={"kid": "synthetic-key"})]
        for name, value in {"jku": "https://attacker.invalid/jwks", "jwk": self.jwk,
                            "x5u": "https://attacker.invalid/cert", "x5c": ["forged"],
                            "crit": ["synthetic"], "b64": True, "typ": "id+jwt"}.items():
            tokens.append(self.raw_token(json.dumps({"alg": "RS256", "kid": "synthetic-key",
                                                     "typ": "JWT", name: value}), json.dumps(self.claims())))
        for token in tokens:
            with self.subTest(header=token.split(".")[0]), self.assertRaises(OAuthAuthenticationError):
                self.auth(token)

    def test_issuer_audience_and_required_times_are_verified(self):
        now = int(time.time())
        invalid = [{"iss": "https://other.synthetic/"}, {"iss": [self.config["issuer"]]},
                   {"aud": "https://other.synthetic/mcp"}, {"aud": [12, self.config["resource"]]},
                   {"iat": now - 201, "exp": now - 1}, {"iat": now + 60, "exp": now + 100},
                   {"nbf": now + 60}, {"nbf": now + 201}, {"exp": now + 400},
                   {"exp": now - 1}, {"exp": True}, {"iat": str(now)}, {"nbf": None},
                   {"iat": float("nan")}, {"exp": float("inf")}, {"iat": -1}]
        for updates in invalid:
            with self.subTest(updates=updates), self.assertRaises(OAuthAuthenticationError):
                self.auth(self.raw_token('{"alg":"RS256","kid":"synthetic-key","typ":"JWT"}',
                                         json.dumps({**self.claims(), **updates})))
        for missing in ("iss", "aud", "sub", "iat", "exp", "scope", "azp"):
            with self.subTest(missing=missing), self.assertRaises(OAuthAuthenticationError):
                self.auth(self.token(remove=[missing]))
        self.auth(self.token({"aud": ["another-resource", self.config["resource"]]}))

    def test_client_subject_and_access_token_type_binding(self):
        for update in ({"sub": "unbound-subject"}, {"azp": "unbound-client"},
                       {"client_id": "conflicting-client"}, {"token_use": "id"},
                       {"typ": "ID"}, {"typ": "JWT"}, {"scope": ["memory:read"]}):
            with self.subTest(update=update), self.assertRaises(OAuthAuthenticationError):
                self.auth(self.token(update))
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(self.token(remove=["typ"]))
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(self.token({"token_use": "id"}, headers={"typ": "at+jwt"}))
        self.auth(self.token({"client_id": "synthetic-client"}, remove=["azp"]))
        self.auth(self.token({"client_id": "synthetic-client"}))
        self.auth(self.token(remove=["typ"], headers={"typ": "at+jwt"}))
        self.auth(self.token({"token_use": "access"}, remove=["typ"]))

    def test_scopes_are_intersected_with_current_local_grant(self):
        read_token = self.token({"scope": "memory:read admin sync"})
        self.assertEqual(self.auth(read_token)["scopes"], ["read"])
        with self.assertRaises(OAuthScopeError) as error:
            self.auth(read_token, "write")
        self.assertEqual((error.exception.status, error.exception.scope), (403, "memory:write"))
        self.set_grant(self.store.create_grant("synthetic-read-only", ["read"]))
        full_token = self.token()
        self.assertEqual(self.auth(full_token)["scopes"], ["read"])
        with self.assertRaises(AuthorizationError) as denied:
            self.auth(full_token, "write")
        self.assertNotIsInstance(denied.exception, OAuthScopeError,
                                 "Reauthorization must not promise to widen a local grant")
        for scope in ("", "admin sync", "memory:admin", "read write", "memory:Read"):
            with self.subTest(scope=scope), self.assertRaises(OAuthScopeError):
                self.auth(self.token({"scope": scope}))
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(full_token, "admin")

    def test_correction_requires_separate_scope_before_store_changes(self):
        token = self.token({"scope": "memory:read memory:write"})
        correction = {"type": "assertion", "id": "correction", "subject": "project", "predicate": "decision",
                      "value": "Different", "source_ids": ["evidence"], "kind": "correct",
                      "predecessors": ["prior"], "reason": "Synthetic correction"}
        with self.assertRaises(OAuthScopeError) as error:
            self.service.call("memory_submit", {"actions": [correction]}, token)
        self.assertEqual(error.exception.scope, "memory:correct")
        self.assertEqual(self.store.query()["assertions"], [])

    def test_revocation_is_immediate_and_owner_peer_grants_never_bind(self):
        token = self.token()
        self.auth(token)
        self.store.revoke_grant(self.grant)
        with self.assertRaises(OAuthAuthenticationError):
            self.service.call("memory_query", {"known_at": 0}, token)
        self.set_grant(self.store.create_grant("synthetic-owner-grant", ["read", "admin"], kind="owner"))
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(token)
        self.store.admit_peer("other-peer", "12" * 32)
        self.set_grant(self.store.create_grant("synthetic-peer-grant", ["sync"], kind="peer", peer_id="other-peer"))
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(token)
        replacement = self.store.create_grant("synthetic-rotated-client", ["read"])
        self.set_grant(replacement)
        self.assertEqual(self.auth(token)["id"], self.store.authenticate(replacement)["id"])

    def test_jwks_rotation_is_applied_without_restart(self):
        old_token = self.token()
        next_jwk = self.public_key(self.next_key, "synthetic-next-key")
        new_token = self.token(key=self.next_key, headers={"kid": "synthetic-next-key"})
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(new_token)
        self.set_keys([self.jwk, next_jwk])
        self.auth(old_token)
        self.auth(new_token)
        self.set_keys([next_jwk])
        self.auth(new_token)
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(old_token)

    def test_unsafe_jwks_fails_closed(self):
        private = {**jwt.algorithms.RSAAlgorithm.to_jwk(self.key, as_dict=True), "kid": "synthetic-key"}
        weak = self.public_key(rsa.generate_private_key(public_exponent=65537, key_size=1024), "synthetic-key")
        invalid_keys = [[], [self.jwk, self.jwk], [private], [weak], [{**self.jwk, "use": "enc"}],
                        [{**self.jwk, "alg": "HS256"}], [{**self.jwk, "key_ops": ["sign", "verify"]}],
                        [{**self.jwk, "n": "!"}], [{**self.jwk, "kty": "EC"}]]
        for keys in invalid_keys:
            with self.subTest(keys=len(keys)):
                self.set_keys(keys)
                with self.assertRaises(OAuthConfigurationError):
                    self.auth(self.token())
        (self.path / "jwks.json").unlink()
        with self.assertRaises(OAuthConfigurationError):
            self.auth(self.token())

    def test_duplicate_json_members_are_rejected_even_with_valid_signature(self):
        header = '{"alg":"RS256","kid":"synthetic-key","typ":"JWT"}'
        claims = json.dumps(self.claims())
        duplicate_claim = claims[:-1] + ',"sub":"synthetic-subject"}'
        duplicate_header = header[:-1] + ',"kid":"synthetic-key"}'
        for h, c in ((header, duplicate_claim), (duplicate_header, claims)):
            with self.assertRaises(OAuthAuthenticationError):
                self.auth(self.raw_token(h, c))
        (self.path / "jwks.json").write_text('{"keys":[],"keys":' + json.dumps([self.jwk]) + '}')
        with self.assertRaises(OAuthConfigurationError):
            self.auth(self.token())

    def test_malformed_tokens_are_bounded_and_errors_do_not_leak_secrets(self):
        for token in (None, 123, "", "secret", "a.b.c", "x" * 17000, "é.é.é", "..", "e30=.e30=.x"):
            with self.subTest(kind=type(token).__name__), self.assertRaises(OAuthAuthenticationError) as error:
                self.auth(token)
            self.assertEqual(str(error.exception), "Invalid or unbound OAuth access token")

    def test_private_grant_file_permissions_symlinks_and_size_are_enforced(self):
        token = self.token()
        self.grant_file.chmod(0o644)
        with self.assertRaises(OAuthConfigurationError):
            self.auth(token)
        self.grant_file.chmod(0o600)
        target = self.path / "private-target"
        self.grant_file.rename(target)
        self.grant_file.symlink_to(target)
        with self.assertRaises(OAuthConfigurationError):
            self.auth(token)
        self.grant_file.unlink()
        self.set_grant("x" * 1025)
        with self.assertRaises(OAuthConfigurationError):
            self.auth(token)
        self.set_grant("nonexistent-synthetic-grant")
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(token)

    def test_configuration_is_strict_and_does_not_allow_header_injection(self):
        changes = [{"issuer": "http://identity.synthetic"}, {"issuer": "https://u:p@identity.synthetic"},
                   {"issuer": "https://identity.synthetic/#fragment"},
                   {"resource": "https://memory.synthetic/mcp?token=secret"},
                   {"resource": "https://memory.synthetic/another"},
                   {"resource": "https://memory.synthetic/mcp\r\nInjected: x"},
                   {"resource": 'https://memory.synthetic\"/mcp'}, {"jwks_url": "https://attacker.invalid/"},
                   {"max_token_lifetime_seconds": 301}, {"max_token_lifetime_seconds": True},
                   {"clock_skew_seconds": 31}, {"clock_skew_seconds": -1}, {"bindings": []},
                   {"bindings": self.config["bindings"] * 2}]
        another = {**self.config["bindings"][0], "client_id": "second-client"}
        changes.append({"bindings": self.config["bindings"] + [another]})
        for change in changes:
            with self.subTest(change=change), self.assertRaises(OAuthConfigurationError):
                self.configure({**self.config, **change})
        # A changed on-disk binding cannot silently modify a running server's policy.
        self.configure()
        config = copy.deepcopy(self.config)
        config["bindings"][0]["subject"] = "new-subject"
        (self.path / "oauth.json").write_text(json.dumps(config))
        self.auth(self.token())
        with self.assertRaises(OAuthAuthenticationError):
            self.auth(self.token({"sub": "new-subject"}))

    def test_metadata_and_challenge_publish_only_pinned_resource_policy(self):
        expected = {"resource": self.config["resource"], "resource_name": "RefactoredMemory",
                    "authorization_servers": [self.config["issuer"]],
                    "scopes_supported": list(SCOPE_MAP), "bearer_methods_supported": ["header"]}
        self.assertEqual(self.auth.resource_metadata(), expected)
        altered = self.auth.resource_metadata()
        altered["authorization_servers"].append("https://attacker.invalid")
        self.assertEqual(self.auth.resource_metadata(), expected)
        self.assertEqual(self.auth.metadata_path, "/.well-known/oauth-protected-resource/mcp")
        self.assertEqual(self.auth.local_files, (self.path / "oauth.json", self.path / "jwks.json", self.grant_file))
        with self.assertRaises(AttributeError):
            self.auth.local_files = ()
        challenge = self.auth.www_authenticate("insufficient_scope", "memory:write")
        self.assertIn('resource_metadata="https://memory.synthetic/.well-known/oauth-protected-resource/mcp"', challenge)
        self.assertIn('error="insufficient_scope"', challenge)
        self.assertIn('scope="memory:write"', challenge)
        for error, scope in (("\r\nInjected", None), (None, 'memory:read"\r\nInjected')):
            with self.assertRaises(ValueError):
                self.auth.www_authenticate(error, scope)


if __name__ == "__main__":
    unittest.main()
