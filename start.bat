@if not "%~0"=="%~dp0.\%~nx0" start /min cmd /c,"%~dp0.\%~nx0" %* & goto :eof

REM Move to the directory where this batch file exists
cd /d %~dp0

REM Check Python version
python --version

REM Activate venv
call venv\Scripts\activate.bat

REM Launch GUI application
python gui\app_gui.py

REM Pause when finished
pause
