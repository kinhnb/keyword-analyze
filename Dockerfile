FROM python:3.10-slim

# Create non-root user for security
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt production-requirements.txt ./
RUN pip install --no-cache-dir -r production-requirements.txt && \
    rm -rf /root/.cache/pip

# Copy application code
COPY ai_serp_keyword_research /app/ai_serp_keyword_research
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start the application
CMD alembic upgrade head && gunicorn ai_serp_keyword_research.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 4 --timeout 120 