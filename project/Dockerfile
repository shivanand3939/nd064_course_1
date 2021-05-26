FROM python:2.7

WORKDIR /app

COPY ./techtrends /app

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 3111

RUN python init_db.py


CMD ["python", "app.py"]
