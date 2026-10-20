FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached separately from code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Cloud Run injects PORT (defaults to 8080). We bind to 8080.
ENV PORT=8080
EXPOSE 8080

# 0.0.0.0 so external traffic can reach the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
