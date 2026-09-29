FROM python:3.12-slim

WORKDIR /app

COPY . .
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY app ./app

CMD ["ddtrace-run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
