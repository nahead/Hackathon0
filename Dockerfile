# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install git (needed for vault sync)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY railway_all_in_one.py .

# Expose port (Fly.io will set PORT env variable)
EXPOSE 8080

# Run the application
CMD ["python", "railway_all_in_one.py"]
