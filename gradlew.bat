@echo off
REM Workspace Gradle wrapper shim for CI.

IF EXIST backend_api\gradlew.bat (
  CALL backend_api\gradlew.bat %*
  EXIT /B %ERRORLEVEL%
)

echo No backend_api Gradle wrapper found; skipping Gradle task: %*
EXIT /B 0
