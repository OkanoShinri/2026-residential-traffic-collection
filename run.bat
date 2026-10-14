@echo off
chcp 65001 > nul
cd /d "%~dp0"

where uv > nul 2>&1
if errorlevel 1 (
    echo 必要なツール uv をインストールします。
    powershell -NoProfile -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

where uv > nul 2>&1
if errorlevel 1 (
    echo.
    echo uv のインストールに失敗しました。この画面を撮影して連絡してください。
    pause
    exit /b 1
)

uv run scripts.py

echo.
echo この画面は閉じて大丈夫です。何かキーを押すと閉じます。
pause > nul
