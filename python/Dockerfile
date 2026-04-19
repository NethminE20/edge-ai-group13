# Lightweight Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (for caching)
COPY requirements.txt .

# Install libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run full pipeline (AI + simulation)
CMD ["python", "main.py"]