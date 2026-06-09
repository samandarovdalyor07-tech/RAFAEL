@echo off
title RAPHAIL - O'rnatish
color 0B

echo.
echo  ██████╗  █████╗ ██████╗ ██╗  ██╗ █████╗ ██╗██╗
echo  ██╔══██╗██╔══██╗██╔══██╗██║  ██║██╔══██╗██║██║
echo  ██████╔╝███████║██████╔╝███████║███████║██║██║
echo  ██╔══██╗██╔══██║██╔═══╝ ██╔══██║██╔══██║██║██║
echo  ██║  ██║██║  ██║██║     ██║  ██║██║  ██║██║███████╗
echo  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
echo.
echo  Shaxsiy AI Assistent - O'rnatish boshlandi
echo  ==========================================
echo.

REM Python tekshiruvi
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi!
    echo Python 3.10+ ni https://python.org dan o'rnating.
    pause
    exit /b 1
)

echo [OK] Python topildi.

REM Virtual environment
echo.
echo [1/5] Virtual muhit yaratilmoqda...
python -m venv venv
call venv\Scripts\activate.bat
echo [OK] venv tayyor.

REM pip yangilash
echo.
echo [2/5] pip yangilanmoqda...
python -m pip install --upgrade pip --quiet

REM PyAudio (Windows uchun alohida)
echo.
echo [3/5] PyAudio o'rnatilmoqda...
pip install pipwin --quiet
pipwin install pyaudio
if errorlevel 1 (
    echo PyAudio pipwin bilan o'rnatilmadi, pip orqali urinilmoqda...
    pip install pyaudio
)

REM Asosiy kutubxonalar
echo.
echo [4/5] Kutubxonalar o'rnatilmoqda...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [OGOHLANTIRISH] Ba'zi kutubxonalar o'rnatilmadi.
    echo requirements.txt ni tekshiring.
)

REM Whisper
echo.
echo [5/5] Whisper modeli yuklanmoqda (base)...
python -c "import whisper; whisper.load_model('base')"
if errorlevel 1 (
    echo [OGOHLANTIRISH] Whisper modeli yuklanmadi.
    echo Birinchi ishga tushirishda avtomatik yuklanadi.
)

REM .env fayl
echo.
if not exist .env (
    copy .env.example .env >nul
    echo [DIQQAT] .env fayl yaratildi!
    echo .env faylini oching va ANTHROPIC_API_KEY ni kiriting.
    notepad .env
) else (
    echo [OK] .env fayl mavjud.
)

echo.
echo  ==========================================
echo  O'rnatish tugadi!
echo.
echo  Ishga tushirish uchun: start.bat
echo  yoki: python main.py
echo  ==========================================
echo.
pause
