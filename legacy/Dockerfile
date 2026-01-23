# Dockerfile for Lunar New Year Red Envelope Horse Racing Game
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "server.py"]
