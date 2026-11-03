# Hermes Offline Android — phase 1

This is an initial **native Android shell**, not a complete Hermes port.

- Android 9–16 intended support (minSdk 28, compileSdk/targetSdk 35).
- No network permission, cloud backend, billing integration, or GGUF.
- LiteRT-LM 0.18.0 dependency declared for future offline inference.
- No model weights are bundled.
- No model loading, chat inference, memory port, agent tools, or Hermes compatibility bridge yet.
- Not compiled, signed, installed, or device-tested at commit time.

## Build prerequisite

Use JDK 17 and Android SDK 35. Run `gradle :app:assembleDebug` from this directory with a compatible Gradle distribution. No Gradle wrapper is checked in, so reproducibility remains an open issue.

## Security

Do not enable unrestricted shell commands, arbitrary plugin execution, or network services in the Android process. Implement sandboxed, user-authorized tool adapters before enabling agent capabilities.

## Next verification gates

1. Add a pinned Gradle wrapper and verify its distribution checksum.
2. Compile on Android SDK 35 and fix actual compiler errors.
3. Implement and test local model import, hash verification and LiteRT-LM initialization.
4. Port Hermes session/memory semantics with migration tests.
5. Verify on real Android 9 and Android 16 devices, then sign and inspect APK.
