FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and Node.js for Prisma
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Prisma schema for migrations
COPY packages/database/prisma ./prisma
COPY packages/database/package.json ./prisma/
COPY packages/database/prisma.config.ts ./prisma/

# Install Prisma
RUN cd prisma && npm install prisma@latest

# Copy application code
COPY apps/api/ .

# Note: ML models will be downloaded on first use at runtime
# This avoids build-time dependency conflicts

# Expose port
EXPOSE 8000

# Run migrations then start server
CMD cd prisma && npx prisma db push --accept-data-loss && cd /app && gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} --timeout 120
