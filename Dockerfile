FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8000

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads temp

# Set permissions
RUN chmod -R 777 uploads temp

# Create a simple health check script
RUN echo '#!/bin/bash\n\
for i in {1..12}; do\n\
  if curl -f http://localhost:$PORT/; then\n\
    exit 0\n\
  fi\n\
  sleep 5\n\
done\n\
exit 1' > /usr/local/bin/healthcheck.sh \
    && chmod +x /usr/local/bin/healthcheck.sh

# Expose the port
EXPOSE $PORT

# Run the application directly with Python
CMD ["python", "app.py"] 