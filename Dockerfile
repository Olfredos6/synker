FROM python:3.9-slim
WORKDIR /app
COPY ./requirements.txt .
RUN apt update \
    && apt upgrade -y \
    && apt install -y git \
    && pip install -r requirements.txt
