@echo off
REM バッチファイルのある場所に移動
cd /d %~dp0

REM cloudflared.exeのパスが通っているか確認
where cloudflared.exe >nul 2>nul
if errorlevel 1 (
    echo [警告] cloudflared.exe のパスが通っていません。wingetでインストールします。
    winget install --id Cloudflare.cloudflared --silent
    REM wingetでインストール後、パスが通っているか再確認
    where cloudflared.exe >nul 2>nul
    if errorlevel 1 (
        echo [エラー] cloudflared.exe のパスがまだ通っていません。
        echo 必要に応じて "C:\Program Files\Cloudflare\Cloudflared" をPATHに追加してください。
        echo.
        echo 現在のPATH:
        echo %PATH%
        pause
        exit /b
    ) else (
        echo cloudflared.exe のパスは通っています。
    )
) else (
    echo cloudflared.exe のパスは通っています。
)

REM .cloudflaredフォルダをユーザーディレクトリに作成
if not exist "%USERPROFILE%\.cloudflared" (
    mkdir "%USERPROFILE%\.cloudflared"
)

REM config.ymlと認証ファイルをユーザーディレクトリにコピー
copy /Y config.yml "%USERPROFILE%\.cloudflared\"
for %%f in (*.json) do copy /Y "%%f" "%USERPROFILE%\.cloudflared\"

REM cloudflaredサービスのインストール（有効化トークンは管理者が案内）
set /p ACTIVATION=cloudflaredの有効化コマンドを貼り付けてEnterしてください:
%ACTIVATION%

echo.
echo Cloudflareトンネルのインストールと初期設定が完了しました。
pause
