#!/bin/sh
set -e

# Wait for PostgreSQL to be reachable
echo "=== Waiting for PostgreSQL ==="
RETRIES=30
until [ $RETRIES -eq 0 ] || python -c "
import asyncio, asyncpg, os, sys

async def check():
    try:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'], timeout=2)
        await conn.close()
        return True
    except Exception:
        return False

sys.exit(0 if asyncio.run(check()) else 1)
"; do
    RETRIES=$((RETRIES - 1))
    echo "PostgreSQL not ready yet, retrying... ($RETRIES attempts left)"
    sleep 2
done

if [ $RETRIES -eq 0 ]; then
    echo "=== Failed to connect to PostgreSQL after 30 attempts ==="
    exit 1
fi
echo "=== PostgreSQL is ready ==="

# Run Alembic migrations (idempotent — safe to run on every start)
echo "=== Running database migrations ==="
alembic upgrade head
echo "=== Migrations complete ==="

# Execute the container's CMD (replaces shell, ensures proper signal handling)
exec "$@"
