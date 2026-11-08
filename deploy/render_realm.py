"""Render an unpopulated Keycloak realm; never reads or creates owner credentials."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

CLIENTS = ("refmem-chatgpt", "refmem-claude", "refmem-openai-api", "refmem-anthropic-api")


def realm(resource, callbacks):
    parsed = urlparse(resource)
    if parsed.scheme != "https" or not parsed.hostname or parsed.path != "/mcp" or parsed.query or parsed.fragment:
        raise ValueError("resource must be the exact https://host/mcp URL")
    if set(callbacks) != set(CLIENTS):
        raise ValueError("supply exact callback URL lists for all four clients")
    clients = []
    for client_id in CLIENTS:
        urls = callbacks[client_id]
        if not isinstance(urls, list) or not urls:
            raise ValueError("each client needs at least one verified callback URL")
        for url in urls:
            p = urlparse(url)
            if p.scheme != "https" or not p.hostname or "*" in url or p.fragment or p.username or p.password:
                raise ValueError("callbacks must be exact HTTPS URLs without wildcards or credentials")
        clients.append({
            "clientId": client_id, "enabled": True, "protocol": "openid-connect",
            "publicClient": True, "standardFlowEnabled": True,
            "fullScopeAllowed": False,
            "directAccessGrantsEnabled": False, "implicitFlowEnabled": False,
            "serviceAccountsEnabled": False, "redirectUris": urls, "webOrigins": [],
            "attributes": {"pkce.code.challenge.method": "S256", "access.token.lifespan": "300"},
            "defaultClientScopes": ["memory:read", "memory:write"],
            "optionalClientScopes": ["memory:correct"],
            "protocolMappers": [{"name": "memory-resource", "protocol": "openid-connect",
                "protocolMapper": "oidc-audience-mapper", "consentRequired": False,
                "config": {"included.custom.audience": resource, "access.token.claim": "true", "id.token.claim": "false"}},
                {"name": "subject", "protocol": "openid-connect", "protocolMapper": "oidc-sub-mapper",
                 "config": {"access.token.claim": "true", "introspection.token.claim": "true"}}],
        })
    return {
        "realm": "refactoredmemory", "enabled": True, "sslRequired": "all",
        "registrationAllowed": False, "resetPasswordAllowed": False,
        "rememberMe": False, "bruteForceProtected": True,
        "accessTokenLifespan": 300, "revokeRefreshToken": True, "refreshTokenMaxReuse": 0,
        "ssoSessionIdleTimeout": 1800, "ssoSessionMaxLifespan": 36000,
        "clientScopes": [{"name": name, "protocol": "openid-connect", "attributes": {"include.in.token.scope": "true"}}
            for name in ("memory:read", "memory:write", "memory:correct")],
        "clients": clients,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", required=True)
    parser.add_argument("--callbacks", type=Path, required=True, help="JSON mapping four client IDs to exact HTTPS callback lists")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = realm(args.resource, json.loads(args.callbacks.read_text()))
    with args.output.open("x") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
