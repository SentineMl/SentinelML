FROM python:3.11-slim

WORKDIR /app

COPY generator.py .

# Environment variables with defaults
ENV SLEEP_SECONDS=1.0
ENV ANOMALY_RATE=0.05

CMD ["python", "-u", "generator.py"]