@echo off
cd /d %~dp0

REM Multiple candidate paths for cloudflared.exe installation
set CF_PATH1="C:\Program Files (x86)\cloudflared\cloudflared.exe"
set CF_PATH2="C:\Program Files\cloudflared\cloudflared.exe"

REM First, search in the current directory
if exist cloudflared.exe (
    set CF_CMD=cloudflared.exe
) else if exist "%CF_PATH1%" (
    set CF_CMD=%CF_PATH1%
) else if exist "%CF_PATH2%" (
    set CF_CMD=%CF_PATH2%
) else (
    echo [Warning] cloudflared not found. Installing with winget.
    winget install --id Cloudflare.cloudflared --silent
    REM After installation, check all paths again
    if exist "%CF_PATH1%" (
        set CF_CMD=%CF_PATH1%
    ) else if exist "%CF_PATH2%" (
        set CF_CMD=%CF_PATH2%
    ) else (
        REM Re-search the path with the where command
        where /r "C:\" cloudflared.exe > "%TEMP%\cf_path.txt" 2>nul
        set /p CF_CMD=<"%TEMP%\cf_path.txt"
        del "%TEMP%\cf_path.txt"
        if not defined CF_CMD (
            echo [Error] Failed to install or locate cloudflared.exe.
            pause
            exit /b
    )
)

:found
REM Operation check
"%CF_CMD%" --version

REM Create .cloudflared folder in user directory
if not exist "%USERPROFILE%\.cloudflared" (
    mkdir "%USERPROFILE%\.cloudflared"
)

REM Copy config.yml and authentication files to user directory
copy /Y config.yml "%USERPROFILE%\.cloudflared\"
for %%f in (*.json) do copy /Y "%%f" "%USERPROFILE%\.cloudflared\"

REM Install cloudflared service
set /p ACTIVATION=Paste the cloudflared activation command and press Enter:
%ACTIVATION%

echo.
echo Cloudflare tunnel installation and initial setup is complete.
pause
