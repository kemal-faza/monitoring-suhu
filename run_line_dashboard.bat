@echo off
:: Mengatur judul jendela Command Prompt
title IoT Dashboard Launcher

echo ==========================================================
echo      IoT REAL-TIME DASHBOARD LAUNCHER
echo ==========================================================
echo.

:: Variabel untuk nama virtual environment
set VENV_DIR=venv

:: Langkah 1: Periksa apakah virtual environment sudah ada
echo [1/4] Memeriksa virtual environment ('%VENV_DIR%')...
:: PERBAIKAN: Menggunakan tanda kutip di sekitar path
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment tidak ditemukan. Membuat baru...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo GAGAL membuat virtual environment. Pastikan Python terinstal dan ada di PATH.
        pause
        exit /b
    )
    echo Virtual environment berhasil dibuat.
) else (
    echo Virtual environment sudah ada.
)
echo.

:: Langkah 2: Aktifkan virtual environment
echo [2/4] Mengaktifkan virtual environment...
:: PERBAIKAN: Menggunakan tanda kutip di sekitar path
call "%VENV_DIR%\Scripts\activate.bat"
echo Aktif.
echo.

:: Langkah 3: Install semua package yang dibutuhkan
echo [3/4] Menginstall/memverifikasi package dari requirements.txt...
:: PERBAIKAN: Menggunakan tanda kutip di sekitar path
pip install -r "requirements.txt" --no-warn-script-location
echo Package siap.
echo.

:: Langkah 4: Jalankan aplikasi utama
echo [4/4] Menjalankan aplikasi dashboard...
echo Buka browser dan akses http://127.0.0.1:8050/
echo Tekan CTRL+C di jendela ini untuk menghentikan server.
echo.
:: PERBAIKAN: Menggunakan tanda kutip di sekitar path
python "src/line_dashboard.py"

echo.
echo ==========================================================
echo      Aplikasi Dashboard telah ditutup.
echo ==========================================================
pause