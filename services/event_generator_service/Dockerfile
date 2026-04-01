FROM python:3.11-slim

WORKDIR /app

COPY services/event_generator_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/event_generator_service/config.py services/event_generator_service/schema.py services/event_generator_service/generator.py ./
COPY services/orm /app/orm
RUN mkdir -p /app/data
COPY services/event_generator_service/data/ /app/data/




CMD ["python", "-u", "generator.py"]