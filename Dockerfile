FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install optional dependencies
RUN pip install --no-cache-dir mux-python || echo "mux-python installation failed - continuing without it"

# Copy the application code
COPY main_optimized.py .
COPY main.py .

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application - use PORT env variable if available, otherwise default to 8000
CMD uvicorn main_optimized:app --host 0.0.0.0 --port ${PORT:-8000}