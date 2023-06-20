FROM python:3.9-alpine

WORKDIR /app

RUN apk update && \
    apk add --no-cache build-base

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV RDS_HOST=rds-database-1.cvnkpkz7gh8g.us-east-1.rds.amazonaws.com
ENV RDS_DATABASE=mydb

EXPOSE 5000

CMD ["python", "app.py"]
