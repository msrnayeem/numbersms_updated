# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Create a non-root user
RUN useradd -m appuser

# Set the working directory in the container
WORKDIR /app

# Install dependencies needed for mysqlclient and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json and package-lock.json (if exists)
COPY package*.json ./
RUN npm ci --only=production

# Copy the rest of the application code
COPY . .

# Build Tailwind CSS for production
RUN npm run build

# Remove development dependencies
RUN apt-get purge -y --auto-remove gcc \
    && npm prune --production \
    && rm -rf /root/.npm /root/.cache

# Change ownership of the application files to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Make port 5000 available
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app \
    FLASK_ENV=production

# Run gunicorn with appropriate production settings - now on port 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "wsgi:application"]