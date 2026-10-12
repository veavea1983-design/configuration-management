@echo off
cd /d "%~dp0.."
py src\main.py --vfs data\vfs_deep ^
  --startup-script scripts\startup.txt
pause
