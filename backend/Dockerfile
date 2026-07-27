# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app
# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Expose the API port
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
