@echo off
:: Mengatur judul jendela Command Prompt
title IoT Desktop Monitor Launcher

echo ==========================================================
echo      IoT REAL-TIME DESKTOP MONITOR LAUNCHER
echo ==========================================================
echo.

:: Variabel untuk nama virtual environment
set VENV_DIR=venv

:: Langkah 1: Periksa apakah virtual environment sudah ada
echo [1/4] Memeriksa virtual environment ('%VENV_DIR%')...
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
call "%VENV_DIR%\Scripts\activate.bat"
echo Aktif.
echo.

:: Langkah 3: Install semua package yang dibutuhkan
echo [3/4] Menginstall/memverifikasi package dari requirements.txt...
pip install -r "requirements.txt" --quiet --no-warn-script-location
echo Package siap.
echo.

:: Langkah 4: Jalankan aplikasi utama
echo [4/4] Menjalankan aplikasi monitor desktop...
echo Sebuah jendela aplikasi akan muncul secara otomatis.
echo Tutup jendela aplikasi tersebut untuk keluar.
echo.
:: PERUBAHAN UTAMA: Menjalankan gui.py
python "src/gui.py"

echo.
echo ==========================================================
echo      Aplikasi Monitor telah ditutup.
echo ==========================================================
pause