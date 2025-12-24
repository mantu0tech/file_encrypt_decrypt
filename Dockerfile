FROM python:3.10

LABEL mail="mantasha@gmail.com"

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
# 