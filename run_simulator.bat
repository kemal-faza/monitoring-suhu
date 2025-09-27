@echo off
echo ========================================
echo    Multi-Node Simulator
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
echo Starting Multi-Node Simulator...
echo This will simulate 3 nodes: sim_001, sim_002, sim_003
echo.
echo Press Ctrl+C to stop the simulator
echo ========================================

cd src\multi_node
python node_simulator.py

pause