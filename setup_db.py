#!/usr/bin/env python3
"""
Database setup script for the Lightspun FastAPI application.

This script initializes the PostgreSQL database with tables and sample data.
Make sure PostgreSQL is running before executing this script.

Usage:
    python setup_db.py
"""

import asyncio
import sys
import os
from lightspun.init_db import init_database

async def main():
    print("🚀 Setting up Lightspun database...")
    print(f"📊 Database URL: {os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/lightspun_db')}")
    
    try:
        await init_database()
        print("✅ Database setup completed successfully!")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())