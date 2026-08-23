@echo off
cd /d "%~dp0backend"
set PYTHONPATH=%~dp0backend;%~dp0
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
