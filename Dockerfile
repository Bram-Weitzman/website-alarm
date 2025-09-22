# Use a modern, slim Python base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file first to leverage Docker's build cache
COPY requirements.txt .

# Install dependencies without caching to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application script
COPY web_alarm.py .

# Set the command to run when the container starts
CMD ["python", "web_alarm.py"]
