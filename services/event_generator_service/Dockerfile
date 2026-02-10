FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py schema.py generator.py ./
RUN mkdir -p /app/data
COPY data/ /app/data/




CMD ["python", "-u", "generator.py"]