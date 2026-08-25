FROM python:3.11-slim

WORKDIR /app

# Upgrade pip first so it resolves manylinux wheels correctly
RUN pip install --upgrade pip --no-cache-dir

# Copy and install runtime dependencies only (no docling, no sentence-transformers,
# no Rust/Fortran build tools required — all packages have pre-built wheels)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (includes pre-built standards corpus in standards/)
COPY . .

# Expose default port; Render overrides via $PORT
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
