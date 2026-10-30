@echo off
title Jurat Yordamchi
cd /d "%~dp0"
where python >nul 2>nul || (echo Python topilmadi. winget install Python.Python.3.12 & pause & exit /b)
python -m pip install --quiet --disable-pip-version-check -r requirements.txt
python yordamchi.py
pause
