#!/usr/bin/env python3
"""Read-only, fail-closed skill synchronization planner (stdlib only).

The planner compares a canonical skill against repository files in local clones.
It never writes into target repositories or calls GitHub. Apply changes only
through separately reviewed feature-branch PRs.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

TARGET_PATH = ".github/skills/chatgpt-coding-agent/SKILL.md"
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def digest(content):
    return hashlib.sha256(content).hexdigest()


def validate_manifest(manifest):
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported manifest schema")
    if manifest.get("skill_path") != TARGET_PATH:
        raise ValueError("Unexpected skill path")
    if not SHA_PATTERN.fullmatch(manifest.get("sha256", "")):
        raise ValueError("Missing or invalid canonical SHA-256")
    repos = manifest.get("repositories")
    if not isinstance(repos, list) or not repos:
        raise ValueError("Repository list must be nonempty")
    if len(set(repos)) != len(repos) or any(not isinstance(r, str) or
            not REPO_PATTERN.fullmatch(r) for r in repos):
        raise ValueError("Invalid or duplicate repository")
    return repos


def safe_target(root, repo):
    owner, name = repo.split("/")
    candidate = (root / owner / name).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError("Repository escapes clone root")
    return candidate


def plan(manifest, canonical_bytes, clone_root):
    repos = validate_manifest(manifest)
    if digest(canonical_bytes) != manifest["sha256"]:
        raise ValueError("Canonical checksum mismatch")
    result = []
    for repo in repos:
        directory = safe_target(clone_root, repo)
        target = directory / TARGET_PATH
        if not directory.is_dir():
            state = "MISSING_CLONE"
            observed = None
        elif target.is_symlink() or not target.resolve().is_relative_to(directory):
            state = "BLOCKED_PATH"
            observed = None
        elif not target.is_file():
            state = "MISSING_SKILL"
            observed = None
        else:
            observed = digest(target.read_bytes())
            state = "IN_SYNC" if observed == manifest["sha256"] else "DRIFT"
        result.append({"repository": repo, "state": state,
                       "observed_sha256": observed})
    return {"schema_version": 1, "canonical_sha256": manifest["sha256"],
            "skill_path": TARGET_PATH, "targets": result,
            "summary": {state: sum(t["state"] == state for t in result)
                        for state in ("IN_SYNC", "DRIFT", "MISSING_CLONE",
                                      "MISSING_SKILL", "BLOCKED_PATH")}}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--canonical", required=True)
    parser.add_argument("--clones", required=True)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
        content = pathlib.Path(args.canonical).read_bytes()
        root = pathlib.Path(args.clones).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Clone root is not a directory")
        report = plan(manifest, content, root)
        print(json.dumps(report, indent=2))
        return 0 if report["summary"]["IN_SYNC"] == len(report["targets"]) else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
