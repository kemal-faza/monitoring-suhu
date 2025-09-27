@echo off
echo ========================================
echo    Single-Node Historical Analysis
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting Historical Data Analysis...
echo This will analyze all historical data from single-node system.
echo.
echo Press Ctrl+C to stop the analysis
echo ========================================

python "src/single_node/analisis.py"

pause