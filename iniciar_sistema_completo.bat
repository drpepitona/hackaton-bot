@echo off
echo ================================================================
echo        SISTEMA DE ANALISIS FINANCIERO CON IA
echo ================================================================
echo.
echo Iniciando Backend (Python FastAPI)...
echo.

cd /d "D:\curosor\ pojects\hackaton"
start "Backend API - Puerto 8000" cmd /k "py api_chatbot.py"

timeout /t 3 /nobreak > nul

echo.
echo ================================================================
echo Backend iniciado en: http://localhost:8000
echo Docs API: http://localhost:8000/docs
echo.
echo NOTA: Abre otra terminal para iniciar el frontend React:
echo   cd "C:\Users\josea\OneDrive\Desktop\news-bot-drag-main"
echo   npm run dev
echo ================================================================
echo.

pause

