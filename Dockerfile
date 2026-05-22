# -------------------------------------------------------
# Stage 1: Builder
# -------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# -------------------------------------------------------
# Stage 2: Runtime
# -------------------------------------------------------
FROM python:3.11-slim AS runtime

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create directories the app needs at runtime
RUN mkdir -p /app/db /app/artifacts /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]