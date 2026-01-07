#!/usr/bin/env bash
set -euo pipefail

# Workspace Gradle wrapper shim for CI.
# Some analysis jobs run `./gradlew check` from the workspace root.
# Delegate to backend_api/gradlew if present; otherwise no-op.

if [[ -f "./backend_api/gradlew" ]]; then
  exec bash "./backend_api/gradlew" "$@"
fi

echo "No backend_api Gradle wrapper found; skipping Gradle task: ${*:-<none>}"
exit 0
