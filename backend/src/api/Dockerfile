FROM python:3.11-slim

WORKDIR /app

COPY requirements .
RUN pip install --no-cache-dir -r requirements

COPY auth.py cache.py crud.py database.py email_config.py google_auth.py main.py models.py schemas.py alembic.ini ./
COPY alembic/ ./alembic/

EXPOSE 8000