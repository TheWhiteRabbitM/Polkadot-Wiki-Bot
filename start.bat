@echo off
REM Polkadot Wiki Bot Startup Script
REM Usage: start.bat

echo.
echo 🪐 Starting Polkadot Wiki Bot...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Load environment variables from .env file
if exist ".env" (
    echo ✅ Loading environment variables...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
)

REM Check if token is set
if "%WIKI_BOT_TOKEN%"=="" (
    echo ❌ Error: WIKI_BOT_TOKEN not set!
    echo Please create a .env file with your bot token.
    echo Example: WIKI_BOT_TOKEN=your_token_here
    pause
    exit /b 1
)

echo 🚀 Starting bot...
echo Press Ctrl+C to stop
echo.

REM Run the bot
python wikibot.py

pause
