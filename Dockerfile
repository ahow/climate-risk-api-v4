FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal, no GDAL/HDF5 needed!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY climate_risk_processor_v4_cloud.py .

# Copy climate data
COPY climate_data /app/climate_data

# Expose port
EXPOSE 8000

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "app:app"]

