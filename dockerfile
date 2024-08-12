FROM public.ecr.aws/careers360/cnext-backend-base:arm64 AS base

FROM base AS backend

WORKDIR /app
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "cnext_apitracker_backend.wsgi:application"]