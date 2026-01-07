@echo off
REM Backend workspace Gradle wrapper shim for CI.

IF EXIST android\gradlew.bat (
  CALL android\gradlew.bat %*
  EXIT /B %ERRORLEVEL%
)

echo No Android Gradle wrapper found in backend_api; skipping Gradle task: %*
EXIT /B 0
