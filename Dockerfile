# Dockerfile remains the same.
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install requests
CMD ["python", "web_alarm.py"]

