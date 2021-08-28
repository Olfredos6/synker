FROM python:3.9-slim
COPY requirements.txt /app
RUN apt update \
    && apt upgrade \
    && apt install -y git \
    && pip install -r /app/requirements
COPY src/ /app
ENTRYPOINT bash -c python
CMD ["/app"]
