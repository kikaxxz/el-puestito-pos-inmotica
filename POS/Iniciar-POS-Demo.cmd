@echo off
setlocal
cd /d "%~dp0"
set PUESTITO_DEMO=1
set TESTING=true
python app.py
