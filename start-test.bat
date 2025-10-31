@echo off
echo Starting Prontivus ICD-10 Test Environment...

echo.
echo 1. Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python main.py"

echo.
echo 2. Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 3. Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both servers are starting...
echo.
echo 📋 Test URLs:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    ICD-10 Test Page: http://localhost:3000/test-icd10
echo    API Docs: http://localhost:8000/docs
echo.
echo 🔍 To test ICD-10 search:
echo    1. Go to http://localhost:3000/test-icd10
echo    2. Try searching for: diabetes, cancer, mental, E10, etc.
echo    3. Or go to a consultation page and use the SOAP form
echo.
pause
