FROM python:3.11-slim

WORKDIR /app/flask_app

# Install ffmpeg via apt (no need to include ffmpeg binaries manually)
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Copy your project files
COPY flask_app/ /app/flask_app/
COPY scripts/ /app/scripts/
COPY .project-root /app/.project-root
COPY requirements.txt /app/

ENV PYTHONPATH=/app

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
