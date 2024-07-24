FROM python:3.8.12-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libffi-dev \
    build-essential \
    && apt-get clean

WORKDIR /app
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "cnext_apitracker_backend.wsgi:application"]