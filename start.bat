@echo off
title RAPHAIL - Shaxsiy AI Assistent
color 0B

REM Virtual env aktivatsiya
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [OGOHLANTIRISH] venv topilmadi. install.bat ni ishga tushiring.
)

REM .env tekshiruvi
if not exist .env (
    echo [XATO] .env fayl topilmadi!
    echo install.bat ni ishga tushiring.
    pause
    exit /b 1
)

echo Raphail ishga tushirilmoqda...
python main.py

echo.
echo Raphail to'xtatildi.
pause
