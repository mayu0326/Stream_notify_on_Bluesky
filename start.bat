@if not "%~0"=="%~dp0.\%~nx0" start /min cmd /c,"%~dp0.\%~nx0" %* & goto :eof

REM バッチファイル自身が存在するディレクトリに移動
cd /d %~dp0

REM Pythonバージョン確認
python --version

REM venv有効化
call venv\Scripts\activate.bat

REM GUIアプリの起動
python gui\app_gui.py

REM 終了時に一時停止
pause
