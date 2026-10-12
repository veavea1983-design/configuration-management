@echo off
cd /d "%~dp0.."
py src\main.py --startup-script scripts\startup_error.txt
pause
