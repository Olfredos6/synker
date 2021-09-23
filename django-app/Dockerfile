FROM python:3.9-slim
WORKDIR /synker
COPY ./requirements.txt .
RUN apt update \
    && apt upgrade -y \
    && apt install git -y \
    && pip install -r requirements.txt
