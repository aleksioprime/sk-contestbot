@echo on
call "C:\venv\contestbot\Scripts\activate.bat"
cd "C:\Development\contestbot"
set URL=https://25e2-46-235-65-112.eu.ngrok.io/
set TOKEN=5395574766:AAFbvibum0EMBf106oMaKIFOl2dc8fP1QtQ
set HOST=localhost
set PORT=5000
python app.py
pause