FROM python:3.11-slim

WORKDIR /app/flask_app

# Install ffmpeg
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY flask_app/ /app/flask_app/
COPY scripts/ /app/scripts/
COPY .project-root /app/.project-root
COPY requirements.txt /app/

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
