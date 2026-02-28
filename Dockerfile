FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project files
COPY . .

# Expose port
EXPOSE 8080

# Run the app
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 backend.app:app