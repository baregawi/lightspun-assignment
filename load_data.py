#!/usr/bin/env python3
"""
Data loading script for the Lightspun FastAPI application.

This script loads sample data from JSON files into the PostgreSQL database:
1. All US states from data/all_states.json
2. Municipalities from data/state_municipalities.json  
3. Addresses from data/addresses_by_municipality_complete.json

Usage:
    python load_data.py [--clear] [--states] [--municipalities] [--addresses]
    
    --clear: Clear existing data before loading
    --states: Load only states data
    --municipalities: Load only municipalities data
    --addresses: Load only addresses data
    (If no specific flags, loads all data)
"""

import asyncio
import json
import os
import sys
import argparse
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent))

# Import configuration and setup
from lightspun.config import get_config
from lightspun.logging_config import get_logger
from lightspun.database import init_database, database, connect_db, disconnect_db, Base, engine

# Load configuration (logging setup is automatic)
config = get_config()

# Initialize database with configuration
init_database(config)

# Initialize logger
logger = get_logger('load_data')

async def clear_all_data():
    """Clear all existing data from the database tables"""
    logger.info("Clearing existing data...")
    
    # Clear in order to respect foreign key constraints
    await database.execute("DELETE FROM addresses")
    await database.execute("DELETE FROM municipalities") 
    await database.execute("DELETE FROM states")
    
    # Reset sequences
    await database.execute("ALTER SEQUENCE addresses_id_seq RESTART WITH 1")
    await database.execute("ALTER SEQUENCE municipalities_id_seq RESTART WITH 1")
    await database.execute("ALTER SEQUENCE states_id_seq RESTART WITH 1")
    
    logger.info("Successfully cleared all existing data")

async def load_states_data():
    """Load states data from data/all_states.json"""
    logger.info("Loading states data...")
    
    # Read states data
    states_file = Path(__file__).parent / "data" / "all_states.json"
    if not states_file.exists():
        logger.error(f"States data file not found: {states_file}")
        raise FileNotFoundError(f"States data file not found: {states_file}")
    
    with open(states_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Insert states
    states_inserted = 0
    for state in data['states']:
        # Check if state already exists
        check_query = "SELECT COUNT(*) FROM states WHERE code = :code"
        exists = await database.fetch_val(query=check_query, values={"code": state['code']})
        
        if not exists:
            query = """
                INSERT INTO states (code, name) 
                VALUES (:code, :name)
            """
            await database.execute(query=query, values=state)
            states_inserted += 1
    
    logger.info(f"Successfully loaded {states_inserted} new states from {len(data['states'])} total")
    return states_inserted

async def load_municipalities_data():
    """Load municipalities data from data/state_municipalities.json"""
    logger.info("Loading municipalities data...")
    
    # Read municipalities data
    municipalities_file = Path(__file__).parent / "data" / "state_municipalities.json"
    if not municipalities_file.exists():
        logger.error(f"Municipalities data file not found: {municipalities_file}")
        raise FileNotFoundError(f"Municipalities data file not found: {municipalities_file}")
    
    with open(municipalities_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    municipalities_inserted = 0
    
    # Process each state's municipalities
    for state_code, state_info in data['state_municipalities'].items():
        # Get the state ID
        state_query = "SELECT id FROM states WHERE code = :code"
        state_row = await database.fetch_one(query=state_query, values={"code": state_code})
        
        if not state_row:
            logger.warning(f"State {state_code} not found in database, skipping municipalities")
            continue
        
        state_id = state_row['id']
        
        # Insert municipalities for this state
        for municipality in state_info['municipalities']:
            # Check if municipality already exists
            check_query = "SELECT COUNT(*) FROM municipalities WHERE name = :name AND state_id = :state_id"
            exists = await database.fetch_val(
                query=check_query, 
                values={"name": municipality['name'], "state_id": state_id}
            )
            
            if not exists:
                query = """
                    INSERT INTO municipalities (name, type, state_id) 
                    VALUES (:name, :type, :state_id)
                """
                values = {
                    "name": municipality['name'],
                    "type": municipality['type'],
                    "state_id": state_id
                }
                
                try:
                    await database.execute(query=query, values=values)
                    municipalities_inserted += 1
                except Exception as e:
                    logger.error(f"Error inserting municipality {municipality['name']}: {e}", exc_info=True)
    
    logger.info(f"Successfully loaded {municipalities_inserted} new municipalities")
    return municipalities_inserted

async def load_addresses_data():
    """Load addresses data from data/addresses_by_municipality_complete.json"""
    logger.info("Loading addresses data...")
    
    # Read addresses data
    addresses_file = Path(__file__).parent / "data" / "addresses_by_municipality_complete.json"
    if not addresses_file.exists():
        logger.error(f"Addresses data file not found: {addresses_file}")
        raise FileNotFoundError(f"Addresses data file not found: {addresses_file}")
    
    with open(addresses_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    addresses_inserted = 0
    
    # Process addresses for each state and municipality
    for state_code, municipalities in data['addresses_by_municipality'].items():
        for municipality_name, addresses in municipalities.items():
            # Parse addresses and insert them
            for address_str in addresses:
                # Parse the full address string
                # Format: "123 Main St, Los Angeles, CA"
                parts = address_str.rsplit(', ', 2)
                if len(parts) != 3:
                    logger.warning(f"Skipping invalid address format: {address_str}")
                    continue
                
                street_address = parts[0]
                city = parts[1] 
                parsed_state_code = parts[2]
                
                # Validate state code matches
                if parsed_state_code != state_code:
                    logger.warning(f"State code mismatch in address: {address_str}")
                    continue
                
                # Check if address already exists
                check_query = "SELECT COUNT(*) FROM addresses WHERE full_address = :full_address"
                exists = await database.fetch_val(
                    query=check_query, 
                    values={"full_address": address_str}
                )
                
                if not exists:
                    # Insert address
                    query = """
                        INSERT INTO addresses (street_address, city, state_code, full_address)
                        VALUES (:street_address, :city, :state_code, :full_address)
                    """
                    values = {
                        "street_address": street_address,
                        "city": city,
                        "state_code": state_code,
                        "full_address": address_str
                    }
                    
                    try:
                        await database.execute(query=query, values=values)
                        addresses_inserted += 1
                    except Exception as e:
                        logger.error(f"Error inserting address {address_str}: {e}", exc_info=True)
    
    logger.info(f"Successfully loaded {addresses_inserted} new addresses")
    return addresses_inserted

async def create_tables():
    """Create database tables if they don't exist"""
    logger.info("Creating database tables if needed...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")

async def verify_data():
    """Verify loaded data by checking counts"""
    logger.info("Verifying loaded data...")
    
    # Count records in each table
    states_count = await database.fetch_val("SELECT COUNT(*) FROM states")
    municipalities_count = await database.fetch_val("SELECT COUNT(*) FROM municipalities")
    addresses_count = await database.fetch_val("SELECT COUNT(*) FROM addresses")
    
    logger.info(f"Data verification - States: {states_count}, Municipalities: {municipalities_count}, Addresses: {addresses_count}")
    
    # Show sample data from each table
    logger.info("Retrieving sample data for verification...")
    
    # Sample states
    states_sample = await database.fetch_all("SELECT code, name FROM states LIMIT 3")
    states_list = [f"{state['code']}: {state['name']}" for state in states_sample]
    logger.info(f"States sample: {', '.join(states_list)}")
    
    # Sample municipalities 
    munis_sample = await database.fetch_all("""
        SELECT m.name, m.type, s.code 
        FROM municipalities m 
        JOIN states s ON m.state_id = s.id 
        LIMIT 3
    """)
    munis_list = [f"{muni['name']} ({muni['type']}) - {muni['code']}" for muni in munis_sample]
    logger.info(f"Municipalities sample: {', '.join(munis_list)}")
    
    # Sample addresses
    addresses_sample = await database.fetch_all("SELECT full_address FROM addresses LIMIT 3")
    addresses_list = [addr['full_address'] for addr in addresses_sample]
    logger.info(f"Addresses sample: {', '.join(addresses_list)}")

async def main():
    """Main data loading function"""
    parser = argparse.ArgumentParser(description='Load sample data into PostgreSQL database')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before loading')
    parser.add_argument('--states', action='store_true', help='Load only states data')
    parser.add_argument('--municipalities', action='store_true', help='Load only municipalities data')  
    parser.add_argument('--addresses', action='store_true', help='Load only addresses data')
    
    args = parser.parse_args()
    
    # If no specific flags, load all data
    load_all = not (args.states or args.municipalities or args.addresses)
    
    try:
        logger.info(f"Starting data loading process - Database URL: {config.get_database_url(hide_password=True)}")
        logger.info(f"Environment: {config.environment}")
        
        # Connect to database
        await connect_db()
        
        # Create tables
        await create_tables()
        
        # Clear data if requested
        if args.clear:
            await clear_all_data()
        
        # Load data based on flags
        total_loaded = 0
        
        if args.states or load_all:
            count = await load_states_data()
            total_loaded += count
        
        if args.municipalities or load_all:
            count = await load_municipalities_data()
            total_loaded += count
            
        if args.addresses or load_all:
            count = await load_addresses_data()
            total_loaded += count
        
        # Verify the loaded data
        await verify_data()
        
        logger.info(f"Data loading completed successfully! Total records loaded: {total_loaded}")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during data loading: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await disconnect_db()

if __name__ == "__main__":
    asyncio.run(main())