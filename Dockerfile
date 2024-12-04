# Inside CommonAssessmentTool/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY app/ app/
COPY tests/ tests/

# Set environment variables if needed
ENV PYTHONPATH=/app

# Expose the port your backend runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "-m", "app.main"]