# Настроить доступ к файлу
# chmod u+x "devops/run_contestbot_mac.command"
# Отключить в настройках MacOS Ресивер AirPlay
source ~/venv/contestbot/bin/activate
# Установить в виртуальное окружение необходимые библиотеки
# pip3 install -r requirements.txt
export URL=https://1b1f-217-117-248-194.eu.ngrok.io/
export TOKEN=5395574766:AAFbvibum0EMBf106oMaKIFOl2dc8fP1QtQ
export HOST=localhost
export PORT=5000
python3 ~/develop/contestbot/app.py