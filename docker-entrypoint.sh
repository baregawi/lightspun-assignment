#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! python -c "
import asyncpg
import asyncio
import sys
import os

async def check_db():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await conn.close()
        print('PostgreSQL is ready!')
        return True
    except Exception as e:
        print(f'PostgreSQL not ready: {e}')
        return False

if not asyncio.run(check_db()):
    sys.exit(1)
"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Initialize database if needed
echo "Initializing database..."
python setup_db.py

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn lightspun.app:app --host 0.0.0.0 --port 8000