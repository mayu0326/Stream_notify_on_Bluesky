@echo off

REM バッチファイル自身が存在するディレクトリに移動
cd /d %~dp0

REM Pythonバージョン確認
python --version

REM venv作成
python -m venv venv

REM venv有効化
call venv\Scripts\activate.bat

REM 必要なパッケージインストール
pip install -r requirements.txt

REM 完了メッセージを出す
echo インストールが完了しました。

REM 終了時に一時停止
pause
