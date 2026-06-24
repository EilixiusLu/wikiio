FROM python:3.11-slim

WORKDIR /app

# 使用腾讯云 Debian 镜像源加速国内下载
RUN sed -i 's|deb.debian.org|mirrors.tencent.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirrors.tencent.com|g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|mirrors.tencent.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|security.debian.org|mirrors.tencent.com|g' /etc/apt/sources.list

# Install build dependencies for psycopg2, asyncpg, bcrypt, and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies（使用腾讯云 PyPI 镜像加速）
COPY requirements.txt .
RUN pip config set global.index-url https://mirrors.tencent.com/pypi/simple/ && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (.dockerignore excludes __pycache__, .env, venv, tests, etc.)
COPY . .

# Ensure log directory exists (logger resolves to /logs/ at runtime inside containers)
RUN mkdir -p /logs

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
