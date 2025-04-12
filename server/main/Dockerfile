# Use official Python image
FROM python:3.12-slim

# Install system dependencies (including libGL)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# firebase
COPY smart-lift-d68a6-firebase-adminsdk-thblg-979712ce71.json /app/smart-lift.json

## model
COPY person-detection-retail-0013.xml /app/model.xml
COPY person-detection-retail-0013.bin /app/model.bin

# Copy everything
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port if needed
EXPOSE 5000

# Default command
CMD ["python", "backend.py"]
