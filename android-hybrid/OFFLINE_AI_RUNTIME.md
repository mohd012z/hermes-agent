# Hermes Android local AI runtime integration gates

Status: DESIGN ONLY. No embedded model or inference is implemented by this document.

## Verified upstream API
Official LiteRT-LM Kotlin Android guide: https://github.com/google-ai-edge/LiteRT-LM/blob/main/docs/api/kotlin/getting_started.md

- Android artifact: `com.google.ai.edge.litertlm:litertlm-android`.
- API: `Engine(EngineConfig(modelPath=...))`, `engine.initialize()`, `engine.createConversation()`, `conversation.sendMessageAsync(...)`; close engine and conversation.
- Model format: `.litertlm`, not GGUF.
- Initialize on background thread; never on UI thread.
- Upstream warns 0.17.x/0.18.x Kotlin metadata 2.4.0 requires Kotlin 2.3+, while 0.16.1 requires Kotlin 2.2+. Select a fixed verified release rather than `latest.release`.

## Integration sequence (not yet complete)
1. Add Kotlin Android Gradle plugin with version compatible with chosen LiteRT-LM artifact. Verify dependency resolution and Android 9 minSdk compatibility before shipping.
2. Implement SAF model import; copy into private app storage with byte-count bound, disk-space check, SHA-256 report and explicit user consent. Do not import secrets.
3. Implement background inference worker with cancellation, model initialization timeout, engine/conversation lifecycle and out-of-memory reporting.
4. Show local model state (not installed/loading/ready/error). Never label offline AI ready until a real generation succeeds with connectivity disabled.
5. Keep agent mode review-only by default; proposed file replacements require user confirmation and explicit Save As. Reject path traversal, binary files, oversized inputs and unsupported edits.
6. Implement device-level offline inference smoke test, build/unit tests, Android 9 compatibility test and a full source-edit-save-reopen regression.
7. Never enable billing or deploy a remote provider by default.

## Current limitations
The Android hybrid app currently contains a source editor, prompt generator and clipboard-based review flow; it does not yet execute AI inference or project tests. GitHub Actions compilation alone does not prove local inference, model support or installation on a physical phone.
