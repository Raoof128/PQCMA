# Multi-stage Dockerfile for PQC Migration Auditor
# Optimized for production use with minimal image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY pqc_migration_auditor/ ./pqc_migration_auditor/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e ".[all]"

# Stage 2: Runtime
FROM python:3.11-slim

# Metadata
LABEL maintainer="Australian Cybersecurity Engineer" \
      description="PQC Migration Auditor - Quantum-vulnerable cryptography scanner" \
      version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi8 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash pqcuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/pqc-audit /usr/local/bin/pqc-audit

# Copy application code
COPY --chown=pqcuser:pqcuser pqc_migration_auditor/ ./pqc_migration_auditor/
COPY --chown=pqcuser:pqcuser pyproject.toml README.md ./

# Create directories for scanning and reports
RUN mkdir -p /scan /reports && \
    chown -R pqcuser:pqcuser /scan /reports

# Switch to non-root user
USER pqcuser

# Set volumes for scanning and reports
VOLUME ["/scan", "/reports"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD pqc-audit --version || exit 1

# Default command (show help)
ENTRYPOINT ["pqc-audit"]
CMD ["--help"]

# Example usage in comments:
# Build: docker build -t pqc-auditor .
# Run:   docker run -v /path/to/code:/scan -v /path/to/reports:/reports pqc-auditor scan /scan --output /reports/scan.json
