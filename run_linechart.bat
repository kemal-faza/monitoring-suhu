@echo off
echo ========================================
echo    Multi-Node Line Chart Dashboard
echo ========================================
echo.

cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting Multi-Node Line Chart Dashboard...
echo Dashboard will be available at: http://127.0.0.1:8051
echo.
echo Press Ctrl+C to stop the dashboard
echo ========================================

cd src\multi_node
python line_chart_dashboard.py

pause