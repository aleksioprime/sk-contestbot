# Указываем Docker использовать образ Python в качестве базового
FROM python:3.7.9
# Устанавливаем необходимые переменные окружения
ENV PYTHONUNBUFFERED 1
ENV URL https://contestbot.aledev.ru/
ENV TOKEN 5395574766:AAFbvibum0EMBf106oMaKIFOl2dc8fP1QtQ
# Устанавливаем рабочий каталог контейнера 
RUN mkdir /app
WORKDIR /app
# Установка зависимостей
RUN pip install --upgrade pip
COPY ./requirements.txt ./
EXPOSE 8000
RUN pip install -r requirements.txt
# Копируем все файлы из локального проекта в контейнер
COPY ./ /app/
# Выполнение стартовых команд
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]