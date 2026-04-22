@echo off
setlocal enabledelayedexpansion
title Kamuna AI - Cyber Security Assistant
color 0A

:MENU 
cls
echo ========================================
echo       KAMUNA AI SECURITY ASSISTANT
echo ========================================
echo.
echo   [1] Start Kamuna AI (Groq)
echo   [2] Start Kamuna AI (Colab)
echo   [3] Start Kamuna AI (Ollama)
echo   [4] Install Dependencies
echo   [5] Exit
echo.
set /p choice="Select option (1-5): "

if "%choice%"=="1" goto GROQ
if "%choice%"=="2" goto COLAB
if "%choice%"=="3" goto OLLAMA
if "%choice%"=="4" goto INSTALL
if "%choice%"=="5" goto EXIT
goto MENU

:GROQ
cls
echo ========================================
echo    Starting Kamuna AI with Groq API
echo ========================================
echo.
set /p api_key="Enter your Groq API Key: "
if "%api_key%"=="" (
    echo API Key cannot be empty!
    pause
    goto MENU
)

REM Set API key as environment variable
set GROQ_API_KEY=%api_key%

REM Run Kamuna AI
python cli.py --backend groq --api-key %api_key%
pause
goto MENU

:COLAB
cls
echo ========================================
echo   Starting Kamuna AI with Google Colab
echo ========================================
echo.
set /p colab_url="Enter Colab ngrok URL: "
if "%colab_url%"=="" (
    echo URL cannot be empty!
    pause
    goto MENU
)

python cli.py --backend colab --url %colab_url%
pause
goto MENU

:OLLAMA
cls
echo ========================================
echo   Starting Kamuna AI with Local Ollama
echo ========================================
echo.
echo Make sure Ollama is running...
python cli.py --backend ollama
pause
goto MENU

:INSTALL
cls
echo ========================================
echo     Installing Dependencies
echo ========================================
echo.
pip install groq requests python-dotenv
echo.
echo Dependencies installed successfully!
pause
goto MENU

:EXIT
exit