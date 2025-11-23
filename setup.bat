@echo off
REM Setup script for Email QA Agentic Platform (Windows)

echo Setting up Email QA Agentic Platform...

REM Create backend virtual environment
echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env >nul 2>&1
    if errorlevel 1 (
        echo EMAIL_ON_ACID_API_KEY=your_key_here > .env
        echo EMAIL_ON_ACID_API_SECRET=your_secret_here >> .env
        echo OPENAI_API_KEY=your_openai_key_here >> .env
    )
    echo Please update .env with your actual API credentials
)

REM Return to root directory
cd ..

REM Setup frontend
echo Setting up frontend...
cd frontend
npm install

REM Return to root directory
cd ..

echo Setup complete!
echo.
echo To run the platform:
echo 1. Start the backend: cd backend && venv\Scripts\activate.bat && python main.py
echo 2. Start the frontend: cd frontend && npm run dev
echo.
echo Visit http://localhost:3000 in your browser