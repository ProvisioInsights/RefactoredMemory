"""Read-only host bind-mount checks using the actual rendered Compose configuration.

Run on the deployment host with filesystem access to the approved private paths.
This does not start containers or prove network/firewall isolation.
"""
import argparse
import json
from pathlib import Path
import stat
import subprocess
import sys

DIRECTORIES = {"/data", "/config", "/exports", "/backups"}


def check_path(path):
    if not path.is_absolute():
        raise ValueError(f"Bind path must be absolute: {path}")
    for component in (*reversed(path.parents), path):
        if component.is_symlink():
            raise ValueError(f"Symlink in bind path is refused: {component}")
    info = path.stat()
    if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        raise ValueError(f"Bind source must be a regular file or directory: {path}")
    return info


def inspect_config(config, selected):
    checked = 0
    for name in selected:
        service = config["services"][name]
        uid = int(str(service["user"]).split(":", 1)[0])
        for mount in service.get("volumes", []):
            if mount["type"] != "bind":
                continue
            if mount.get("bind", {}).get("create_host_path", False):
                raise ValueError(f"Implicit bind creation is forbidden for {name}")
            source, target = Path(mount["source"]), mount["target"]
            info = check_path(source)
            if (target in DIRECTORIES) != stat.S_ISDIR(info.st_mode):
                raise ValueError(f"Bind source has the wrong file/directory type: {source}")
            if target in {"/data", "/config", "/exports", "/backups"}:
                if info.st_uid != uid or stat.S_IMODE(info.st_mode) != 0o700:
                    raise ValueError(f"Private directory must be owned by runtime UID {uid} with mode 0700: {source}")
            if target.startswith("/run/secrets/") or target.endswith(".key"):
                if info.st_uid != uid or stat.S_IMODE(info.st_mode) not in {0o400, 0o600}:
                    raise ValueError(f"Secret file must be owned by runtime UID {uid} with mode 0400/0600: {source}")
            if target == "/config":
                for index, child in enumerate(source.rglob("*")):
                    if index >= 1000:
                        raise ValueError("Configuration tree exceeds the preflight inspection bound")
                    if child.is_symlink():
                        raise ValueError(f"Symlink in configuration tree is refused: {child}")
                    if child == source / "secrets" or source / "secrets" in child.parents:
                        private_info = child.stat()
                        mode = stat.S_IMODE(private_info.st_mode)
                        allowed_mode = mode == 0o700 if stat.S_ISDIR(private_info.st_mode) else (
                            stat.S_ISREG(private_info.st_mode) and mode in {0o400, 0o600})
                        if private_info.st_uid != uid or not allowed_mode:
                            raise ValueError(f"Private grant subtree requires UID {uid}, directories 0700 and regular files 0400/0600: {child}")
            checked += 1
    return {"result": "passed", "services": selected, "bind_sources_checked": checked,
            "limits": "Read-only path checks; no container startup, credentials login or NAS isolation qualification"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--owner", action="store_true")
    parser.add_argument("--oidc", action="store_true")
    parser.add_argument("--tunnel", action="store_true")
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    command = ["docker", "compose", "--env-file", str(args.env_file), "-f", str(directory / "compose.yaml")]
    selected = ["memory", "sync-ingress"]
    if args.owner:
        command += ["-f", str(directory / "compose.owner.yaml"), "--profile", "owner"]
        selected = ["owner"]
    if args.oidc:
        command += ["-f", str(directory / "compose.oidc.yaml")]
        selected += ["postgres", "keycloak", "auth-admin-ingress"]
    if args.tunnel:
        command += ["--profile", "tunnel"]
        selected += ["tunnel"]
    result = subprocess.run(command + ["config", "--format", "json"], text=True, capture_output=True, check=True)
    print(json.dumps(inspect_config(json.loads(result.stdout), selected), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(json.dumps({"result": "failed", "message": str(error)}), file=sys.stderr)
        sys.exit(2)
