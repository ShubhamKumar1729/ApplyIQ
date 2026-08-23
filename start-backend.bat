@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0venv\Scripts\python.exe" (
  set PY=%~dp0venv\Scripts\python.exe
) else (
  set PY=python
)

echo Using: %PY%
"%PY%" -c "import uvicorn" 2>nul
if errorlevel 1 (
  echo Installing backend requirements into this Python...
  "%PY%" -m pip install -r "%~dp0backend\requirements.txt"
  "%PY%" -m playwright install chromium
)

set PYTHONPATH=%~dp0backend;%~dp0
cd /d "%~dp0backend"
"%PY%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
