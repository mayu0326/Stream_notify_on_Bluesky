@echo off

REM Move to the directory where the batch file itself resides 
cd /d %~dp0

REM Check Python version 
python --version

REM Create venv 
python -m venv venv

REM Venv activation 
call venv\Scripts\activate.bat

REM Install required packages 
pip install -r requirements.txt

REM Send completion message 
echo Installation completed.

REM Pause on exit 
pause