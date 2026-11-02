# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# Install dependencies in an isolated layer so they are cached separately
# from application code. Rebuilds only re-run pip when requirements.txt changes.
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system-level build dependencies needed by some Python packages
# (e.g. scikit-learn, pandas, python-docx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency manifest first — maximises Docker layer cache hits
COPY requirements.txt .

# Install into a prefix we can copy wholesale into the final stage
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
# Lean final image — no build tools, no cache, smaller attack surface
FROM python:3.11-slim AS runtime

WORKDIR /app

# Pull in compiled packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Expose the port Uvicorn will listen on
EXPOSE 8000

# Run database migrations then start the server.
# --host 0.0.0.0 makes the app reachable outside the container.
# --workers 1 is safe for SQLite; increase for PostgreSQL in production.
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1"]
