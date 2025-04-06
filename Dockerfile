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

# Create a more robust health check script
RUN echo '#!/bin/bash\n\
echo "Waiting for application to start..."\n\
for i in {1..60}; do\n\
  echo "Attempt $i: Checking health..."\n\
  if curl -f http://localhost:$PORT/health; then\n\
    echo "Health check passed!"\n\
    exit 0\n\
  fi\n\
  echo "Health check failed, retrying in 5 seconds..."\n\
  sleep 5\n\
done\n\
echo "Health check failed after 60 attempts"\n\
exit 1' > /usr/local/bin/healthcheck.sh \
    && chmod +x /usr/local/bin/healthcheck.sh

# Expose the port
EXPOSE $PORT

# Run the application with proper signal handling
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --preload app:app"] 