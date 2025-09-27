@echo off
echo ========================================
echo    Multi-Node Heatmap Dashboard
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
echo Starting Multi-Node Heatmap Dashboard...
echo Dashboard will be available at: http://127.0.0.1:8050
echo.
echo Press Ctrl+C to stop the dashboard
echo ========================================

cd src\multi_node
python heatmap_dashboard.py

pause