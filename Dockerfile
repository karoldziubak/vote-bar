# Multi-stage Dockerfile for vote-bar Streamlit app
# Optimized for fast builds with uv and proper caching

# Stage 1: Base image with uv
FROM python:3.11-slim AS base

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Stage 2: Dependencies (cached layer)
FROM base AS deps

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies in virtual environment
RUN uv sync --no-install-project --no-dev

# Stage 3: Development image (includes dev dependencies)
FROM deps AS development

# Install dev dependencies
RUN uv sync --no-install-project

# Copy source code
COPY . .

# Install the project in editable mode
RUN uv sync

# Expose Streamlit port
EXPOSE 8501

# Health check for development
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command for development (with hot reload)
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]

# Stage 4: Production image (minimal, no dev dependencies)
FROM deps AS production

# Copy only necessary source files
COPY app.py ./
COPY logic/ ./logic/
COPY README.md LICENSE ./

# Install the project
RUN uv sync --no-dev

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Health check for production
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Production command (optimized)
CMD ["uv", "run", "streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--server.runOnSave", "false", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "true"]