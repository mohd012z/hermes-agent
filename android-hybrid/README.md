# Hermes Hybrid Android client (prototype)

This is a **remote dashboard client**, not an on-device Hermes inference engine. It requires an independently hosted HTTPS Hermes dashboard, compatible authentication, and a reachable server. It does not use GGUF or bundle any model. It does not start the Hermes Python gateway.

Build with JDK 17+, Android SDK platform 35, and Gradle 8.9+: `gradle :app:assembleDebug` from this directory. APK: `app/build/outputs/apk/debug/app-debug.apk`.

Security: HTTPS-only input, origin-locked WebView navigation, no mixed content, no file/content access, TLS errors fail closed. This prototype does not yet support safe file uploads, OAuth external browser redirects, certificate pinning, persistent session management, or a tested Hermes dashboard protocol. Never expose the Hermes gateway directly to the public Internet without access controls.

Target: Android 9+ (API 28). No paid services are configured. The project must be compiled and device-tested before use; a source commit is not a verified APK.

## MT Manager MCP integration (same-device Hermes runtime)

MT Manager provides a separate MCP server for permitted file and APK operations. It is **not** a Hermes host or a local AI inference model. Start MT Manager's MCP service on port 8787, create a bearer token under **AUTH**, and enable bearer authentication. Keep its default-deny file policy; permit only a dedicated project folder as needed. Its local MCP endpoint is `http://127.0.0.1:8787/mcp` when running on the same phone.

A configuration template is provided at [config/mt-manager-mcp.example.yaml](config/mt-manager-mcp.example.yaml). Merge its `mcp_servers.mt_manager` entry into the running Hermes engine's `~/.hermes/config.yaml` (do not overwrite existing MCP servers). Supply `MT_MANAGER_MCP_TOKEN` as a private environment variable in the **Hermes runtime**, not in GitHub, an APK resource, or an Android WebView. Reload MCP connections and verify an explicitly permitted read-only file operation before enabling writes. If Hermes runs on another machine, loopback points to that machine rather than your phone: use a trusted encrypted private connection and the actual reachable address; do not publish the unencrypted MCP port.

**Integration boundary:** The current Android APK is a dashboard WebView and offline notes workspace; it cannot directly load this YAML, authenticate to MT Manager, or execute Hermes MCP tools. An operational Hermes runtime and integration tests are required. No secrets or paid services are provisioned by this example.
