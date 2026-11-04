# OpenViking / Hermes read-back verification

Hermes already contains a native OpenViking MemoryProvider at `plugins/memory/openviking/__init__.py`. Do **not** install a second memory provider or copy a standalone HTTP bridge into the agent loop.

## Existing integration points

- `agent/memory_provider.py`: MemoryProvider lifecycle, prefetch and sync hooks.
- `plugins/memory/openviking/__init__.py`: native OpenViking HTTP client, endpoint validation, identity handling, pending-session recovery and error sanitization.
- `~/.hermes/config.yaml`: select the OpenViking provider through the existing memory setup workflow.
- `~/.hermes/.env`: supply secrets through the existing profile secret mechanism. Never commit keys.

## Safe verification procedure

1. Run `hermes memory setup` and select the existing OpenViking provider; configure the endpoint and secret through Hermes' own setup.
2. Verify server identity and authentication using the native provider's diagnostics. Do not assume a generic HTTP 200 is proof of authentication.
3. Create a uniquely named non-sensitive test note in a dedicated test namespace; read it back and compare exact bytes. Do not overwrite real memory.
4. Exit Hermes, launch a fresh process, and read the note again.
5. Restart the **OpenViking service** using its documented administration procedure; read the note from a fresh process again.
6. Confirm pending-session replay is idempotent, and that credentials, authorization headers and note content do not appear in logs.
7. If any check fails, disable automatic synchronization and preserve the existing local memory store.

## Evidence boundary

The independent `openviking_hermes_bridge.zip` mock tests passed 5/5 on 2026-11-04, but this is **not** proof of compatibility with the real OpenViking API or of server-restart persistence. This branch intentionally avoids replacing the existing native provider. No live host connectivity, server restart or paid Cloudflare services are implied.

## Acceptance gates

- Auth: valid key accepted, invalid key rejected; no secret in logs.
- Round trip: write then exact read-back of a unique note.
- Restart: fresh Hermes process and fresh OpenViking process both recover the note.
- Recovery: repeated replay does not create duplicates or lose acknowledged data.
- Regression: existing Hermes memory and MCP behavior remains unchanged.
