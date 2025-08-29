import asyncio
from .config import get_config
from .database import init_database, Base, engine, database
from .models import State, Municipality, Address

async def create_tables():
    """Create all database tables"""
    if engine is None:
        raise RuntimeError("Database engine not initialized")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

async def populate_sample_data():
    """Populate database with sample data"""
    await database.connect()
    
    # Sample states data
    states_data = [
        {"code": "AL", "name": "Alabama"},
        {"code": "AK", "name": "Alaska"},
        {"code": "AZ", "name": "Arizona"},
        {"code": "AR", "name": "Arkansas"},
        {"code": "CA", "name": "California"},
        {"code": "CO", "name": "Colorado"},
        {"code": "CT", "name": "Connecticut"},
        {"code": "DE", "name": "Delaware"},
        {"code": "FL", "name": "Florida"},
        {"code": "GA", "name": "Georgia"},
        {"code": "HI", "name": "Hawaii"},
        {"code": "ID", "name": "Idaho"},
        {"code": "IL", "name": "Illinois"},
        {"code": "IN", "name": "Indiana"},
        {"code": "IA", "name": "Iowa"},
        {"code": "KS", "name": "Kansas"},
        {"code": "KY", "name": "Kentucky"},
        {"code": "LA", "name": "Louisiana"},
        {"code": "ME", "name": "Maine"},
        {"code": "MD", "name": "Maryland"},
        {"code": "MA", "name": "Massachusetts"},
        {"code": "MI", "name": "Michigan"},
        {"code": "MN", "name": "Minnesota"},
        {"code": "MS", "name": "Mississippi"},
        {"code": "MO", "name": "Missouri"},
        {"code": "MT", "name": "Montana"},
        {"code": "NE", "name": "Nebraska"},
        {"code": "NV", "name": "Nevada"},
        {"code": "NH", "name": "New Hampshire"},
        {"code": "NJ", "name": "New Jersey"},
        {"code": "NM", "name": "New Mexico"},
        {"code": "NY", "name": "New York"},
        {"code": "NC", "name": "North Carolina"},
        {"code": "ND", "name": "North Dakota"},
        {"code": "OH", "name": "Ohio"},
        {"code": "OK", "name": "Oklahoma"},
        {"code": "OR", "name": "Oregon"},
        {"code": "PA", "name": "Pennsylvania"},
        {"code": "RI", "name": "Rhode Island"},
        {"code": "SC", "name": "South Carolina"},
        {"code": "SD", "name": "South Dakota"},
        {"code": "TN", "name": "Tennessee"},
        {"code": "TX", "name": "Texas"},
        {"code": "UT", "name": "Utah"},
        {"code": "VT", "name": "Vermont"},
        {"code": "VA", "name": "Virginia"},
        {"code": "WA", "name": "Washington"},
        {"code": "WV", "name": "West Virginia"},
        {"code": "WI", "name": "Wisconsin"},
        {"code": "WY", "name": "Wyoming"},
        {"code": "DC", "name": "District of Columbia"}
    ]
    
    # Insert states
    for state_data in states_data:
        query = "INSERT INTO states (code, name) VALUES (:code, :name) ON CONFLICT (code) DO NOTHING"
        await database.execute(query=query, values=state_data)
    
    # Get state IDs for municipalities
    ca_state = await database.fetch_one("SELECT id FROM states WHERE code = 'CA'")
    ny_state = await database.fetch_one("SELECT id FROM states WHERE code = 'NY'")
    tx_state = await database.fetch_one("SELECT id FROM states WHERE code = 'TX'")
    
    if ca_state and ny_state and tx_state:
        # Sample municipalities data
        municipalities_data = [
            {"name": "Los Angeles", "type": "city", "state_id": ca_state["id"]},
            {"name": "San Francisco", "type": "city", "state_id": ca_state["id"]},
            {"name": "San Diego", "type": "city", "state_id": ca_state["id"]},
            {"name": "Sacramento", "type": "city", "state_id": ca_state["id"]},
            {"name": "Oakland", "type": "city", "state_id": ca_state["id"]},
            {"name": "New York City", "type": "city", "state_id": ny_state["id"]},
            {"name": "Buffalo", "type": "city", "state_id": ny_state["id"]},
            {"name": "Rochester", "type": "city", "state_id": ny_state["id"]},
            {"name": "Yonkers", "type": "city", "state_id": ny_state["id"]},
            {"name": "Syracuse", "type": "city", "state_id": ny_state["id"]},
            {"name": "Houston", "type": "city", "state_id": tx_state["id"]},
            {"name": "San Antonio", "type": "city", "state_id": tx_state["id"]},
            {"name": "Dallas", "type": "city", "state_id": tx_state["id"]},
            {"name": "Austin", "type": "city", "state_id": tx_state["id"]},
            {"name": "Fort Worth", "type": "city", "state_id": tx_state["id"]}
        ]
        
        # Insert municipalities
        for muni_data in municipalities_data:
            query = """INSERT INTO municipalities (name, type, state_id) 
                      VALUES (:name, :type, :state_id) 
                      ON CONFLICT DO NOTHING"""
            await database.execute(query=query, values=muni_data)
    
    # Sample addresses data
    addresses_data = [
        {
            "street_address": "123 Main Street",
            "city": "Los Angeles",
            "state_code": "CA",
            "full_address": "123 Main Street, Los Angeles, CA"
        },
        {
            "street_address": "456 Oak Avenue",
            "city": "San Francisco",
            "state_code": "CA",
            "full_address": "456 Oak Avenue, San Francisco, CA"
        },
        {
            "street_address": "789 Pine Road",
            "city": "San Diego",
            "state_code": "CA",
            "full_address": "789 Pine Road, San Diego, CA"
        },
        {
            "street_address": "321 Elm Street",
            "city": "New York",
            "state_code": "NY",
            "full_address": "321 Elm Street, New York, NY"
        },
        {
            "street_address": "654 Broadway",
            "city": "Buffalo",
            "state_code": "NY",
            "full_address": "654 Broadway, Buffalo, NY"
        },
        {
            "street_address": "987 Cedar Lane",
            "city": "Houston",
            "state_code": "TX",
            "full_address": "987 Cedar Lane, Houston, TX"
        },
        {
            "street_address": "147 Maple Drive",
            "city": "Dallas",
            "state_code": "TX",
            "full_address": "147 Maple Drive, Dallas, TX"
        },
        {
            "street_address": "258 Birch Way",
            "city": "Austin",
            "state_code": "TX",
            "full_address": "258 Birch Way, Austin, TX"
        }
    ]
    
    # Insert addresses
    for addr_data in addresses_data:
        query = """INSERT INTO addresses (street_address, city, state_code, full_address) 
                  VALUES (:street_address, :city, :state_code, :full_address)
                  ON CONFLICT DO NOTHING"""
        await database.execute(query=query, values=addr_data)
    
    await database.disconnect()
    print("✅ Sample data populated")

async def init_database_with_data():
    """Initialize database with tables and sample data"""
    # Load configuration and initialize database
    config = get_config()
    init_database(config)
    
    await create_tables()
    await populate_sample_data()

if __name__ == "__main__":
    asyncio.run(init_database_with_data())