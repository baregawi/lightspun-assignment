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
from lightspun.config import get_config
from lightspun.init_db import init_database_with_data

async def main():
    print("🚀 Setting up Lightspun database...")
    
    # Load configuration
    config = get_config()
    print(f"📊 Database URL: {config.get_database_url(hide_password=True)}")
    
    try:
        await init_database_with_data()
        print("✅ Database setup completed successfully!")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())