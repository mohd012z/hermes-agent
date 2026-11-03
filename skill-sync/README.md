# Central ChatGPT skill synchronization

Canonical skill: `.github/skills/chatgpt-coding-agent/SKILL.md` in `mohd012z/hermes-agent`, pinned by SHA-256 in `skill-sync/manifest.json`.

## Architecture

- **Source of truth:** one canonical skill and an immutable content checksum.
- **Registry:** `manifest.json` lists the 32 nonempty repositories with skill branches.
- **Planner:** `plan.py` reads local repository clones and emits deterministic JSON statuses: `IN_SYNC`, `DRIFT`, `MISSING_CLONE`, `MISSING_SKILL`, `BLOCKED_PATH`.
- **Executor:** intentionally absent. Applying updates must use reviewed feature-branch commits/PRs with the exact expected checksum. This prevents a repository instruction file from granting new write authority.
- **Verification:** run `python -m unittest discover -s skill-sync -p 'test_*.py' -v` from the repository root, or `cd skill-sync && python -m unittest -v`.
- **Report:** `python skill-sync/plan.py --manifest skill-sync/manifest.json --canonical .github/skills/chatgpt-coding-agent/SKILL.md --clones /path/to/local/clones`.

Clone layout: `/path/to/local/clones/mohd012z/<repo>/`. The tool does not clone repositories, contact GitHub, modify branches, or enable billing. Its exit code is 0 only when every target is in sync; 1 for drift or missing targets; 2 for invalid input.

## Deployment policy

1. Confirm the canonical content and checksum before any distribution.
2. Fetch target branch head and existing file SHA before writing.
3. Use feature branches and draft PRs; do not modify default branches automatically.
4. Verify each target file checksum after the write.
5. Reconcile conflicts manually and report blocked repositories without bypassing safety controls.
6. Never automatically merge, deploy, create secrets, or enable paid services.

## Current known exceptions

`ceet_store` retained an earlier skill version after a tool-level write block. `mda-sentinel-android` is empty and excluded from the 32-target registry. The registry represents desired state, not a claim that all 32 are currently synchronized.

## Limitations

The planner is read-only and local. GitHub remote readback and CI are separate verification gates. Skill files alone do not install global ChatGPT skills or grant runtime access.
