FROM python:3.11-slim

RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/triqler_runner.py
ENV PATH="/app:${PATH}"

LABEL tool="triqler_runner.py"
