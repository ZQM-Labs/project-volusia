# Project Volusia Docker Image
# Build: docker build -t project-volusia .
# Run: docker-compose up -d

FROM python:3.11-slim

LABEL maintainer="zqmcomputing@gmail.com"
LABEL version="2.1.0"
LABEL description="Volusia County Open Data Portal"

# Security: non-root user
RUN useradd -m -u 1000 volusia

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source
COPY Tools/volusia_data/ Tools/volusia_data/
COPY scripts/ scripts/

# Create data directories
RUN mkdir -p /app/Data /app/Media && \
    chown -R volusia:volusia /app

USER volusia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8789/api/health')" || exit 1

CMD ["python", "Tools/volusia_data/portal_app.py"]