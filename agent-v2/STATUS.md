# ChatGPT Coding Agent v2 — integration status

A local standard-library Python prototype has been implemented and tested separately from this GitHub repository. Its six-file archive contains `agent_v2/core.py`, `agent_v2/__main__.py`, `agent_v2/__init__.py`, `tests/test_core.py`, `.github/workflows/agent-v2-tests.yml`, and `README.md`.

## Observed local evidence
- `python -m unittest discover -s tests -v`: 13/13 PASS after correcting a test-harness defect.
- `python -m compileall -q agent_v2 tests`: PASS.
- CLI smoke test of `python-compile`: PASS.
- ZIP integrity: PASS.

## Critical boundary
**The source archive has NOT been imported into this GitHub branch.** The GitHub CI workflow has NOT been run. This status document is not proof of GitHub build success or deployed service operation. The prototype is an offline verification runner, not a full LLM coding agent or security sandbox.

## Next safe integration
Import and review the local archive into this feature branch, run GitHub Actions against the exact head SHA, and open a draft PR. Do not merge, enable paid services, or deploy production automatically.
