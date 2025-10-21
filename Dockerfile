FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Expose the port
EXPOSE 8000

# Simple health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import http.client; c=http.client.HTTPConnection('localhost', int(__import__('os').getenv('PORT', '8000'))); c.request('GET', '/health'); r=c.getresponse(); exit(0 if r.status == 200 else 1)"

# Run the application - use PORT env variable if available, otherwise default to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}