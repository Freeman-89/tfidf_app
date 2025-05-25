FROM python:3.13-slim

WORKDIR /app
COPY tfidf_project/ .
RUN apt update &&  apt upgrade -y \
    && pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn", "tfidf_project.wsgi:application", "--workers", "3", "--bind", "0.0.0.0:8000"]