@echo off
echo.
echo  ========================================
echo   🌿 SAGE - AI Health Assistant
echo  ========================================
echo.

:: Check for environment variables
if "%GOOGLE_CLIENT_ID%"=="" (
    echo  [!] GOOGLE_CLIENT_ID not set
    echo      Set it with: set GOOGLE_CLIENT_ID=your-client-id
    echo.
)

if "%GOOGLE_CLIENT_SECRET%"=="" (
    echo  [!] GOOGLE_CLIENT_SECRET not set
    echo      Set it with: set GOOGLE_CLIENT_SECRET=your-client-secret
    echo.
)

if "%ANTHROPIC_API_KEY%"=="" (
    echo  [!] ANTHROPIC_API_KEY not set
    echo      You'll be prompted to enter it in the app
    echo.
)

echo  Starting Sage...
echo.
echo  [1/2] Starting Backend (Flask) on port 5000...
start "Sage Backend" cmd /k "cd backend && python app.py"

:: Wait for backend to start
timeout /t 3 /nobreak > nul

echo  [2/2] Starting Frontend (Streamlit) on port 8501...
start "Sage Frontend" cmd /k "cd frontend && streamlit run app.py"

echo.
echo  ========================================
echo   Sage is starting up!
echo  ========================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:8501
echo.
echo   Press any key to close this window...
pause > nul