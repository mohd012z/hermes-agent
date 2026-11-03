# Hermes Hybrid Android client (prototype)

This is a **remote dashboard client**, not an on-device Hermes inference engine. It requires an independently hosted HTTPS Hermes dashboard, compatible authentication, and a reachable server. It does not use GGUF or bundle any model. It does not start the Hermes Python gateway.

Build with JDK 17+, Android SDK platform 35, and Gradle 8.9+: `gradle :app:assembleDebug` from this directory. APK: `app/build/outputs/apk/debug/app-debug.apk`.

Security: HTTPS-only input, origin-locked WebView navigation, no mixed content, no file/content access, TLS errors fail closed. This prototype does not yet support safe file uploads, OAuth external browser redirects, certificate pinning, persistent session management, or a tested Hermes dashboard protocol. Never expose the Hermes gateway directly to the public Internet without access controls.

Target: Android 9+ (API 28). No paid services are configured. The project must be compiled and device-tested before use; a source commit is not a verified APK.
