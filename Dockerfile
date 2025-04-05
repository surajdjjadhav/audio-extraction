FROM python:3.11-slim

WORKDIR /app/flask_app

# Copy application and scripts
COPY flask_app/ /app/flask_app/
COPY scripts/ /app/scripts/

# ✅ Copy .project-root to /app
COPY .project-root /app/.project-root

# Add /app to Python path so it can find scripts and logger
ENV PYTHONPATH=/app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
