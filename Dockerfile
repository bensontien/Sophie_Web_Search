FROM python:3.12-slim

LABEL maintainer="banson56561@gmail.com"

RUN apt-get update \
    && pip install --no-cache-dir --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8818

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8818"]