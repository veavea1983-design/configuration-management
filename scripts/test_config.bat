@echo off
cd /d "%~dp0.."
py src\main.py --vfs data\cli_vfs ^
  --startup-script scripts\startup_error.txt ^
  --config config.json
pause
