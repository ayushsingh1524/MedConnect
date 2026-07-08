# ==============================================================================
# Multi-Target Dockerfile for MedConnect AI
# ==============================================================================
# This Dockerfile defines both the frontend and backend production images using
# Docker multi-stage builds. The docker-compose.yml uses the `target` parameter
# to build the specific service.
# ==============================================================================


# ------------------------------------------------------------------------------
# 1. Frontend Builder Stage
# ------------------------------------------------------------------------------
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build


# ------------------------------------------------------------------------------
# 2. Frontend Production Stage (Nginx)
# ------------------------------------------------------------------------------
FROM nginx:alpine AS frontend

# Copy compiled React app from builder
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Note: In a full production environment, you would copy a custom nginx.conf here
# to handle React Router client-side routing fallback to index.html.
# RUN rm /etc/nginx/conf.d/default.conf
# COPY frontend/nginx.conf /etc/nginx/conf.d/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


# ------------------------------------------------------------------------------
# 3. Backend Production Stage (FastAPI)
# ------------------------------------------------------------------------------
FROM python:3.10-slim AS backend
WORKDIR /app/backend

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for psycopg2/asyncpg if needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir asyncpg psycopg2-binary  # Required for PostgreSQL

# Copy backend source code
COPY backend/ ./

# Expose FastAPI port
EXPOSE 8000

# Run Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
