"""
Sample data fixtures for testing.
"""

from typing import Dict, List, Any


class SampleDataFixtures:
    """Class containing sample data for testing."""
    
    @staticmethod
    def get_sample_states() -> List[Dict[str, Any]]:
        """Get sample state data for testing."""
        return [
            {"id": 1, "code": "CA", "name": "California"},
            {"id": 2, "code": "NY", "name": "New York"},
            {"id": 3, "code": "TX", "name": "Texas"},
            {"id": 4, "code": "FL", "name": "Florida"},
            {"id": 5, "code": "WA", "name": "Washington"},
            {"id": 6, "code": "IL", "name": "Illinois"},
            {"id": 7, "code": "PA", "name": "Pennsylvania"},
            {"id": 8, "code": "OH", "name": "Ohio"},
            {"id": 9, "code": "GA", "name": "Georgia"},
            {"id": 10, "code": "NC", "name": "North Carolina"}
        ]
    
    @staticmethod
    def get_sample_municipalities() -> List[Dict[str, Any]]:
        """Get sample municipality data for testing."""
        return [
            # California municipalities
            {"id": 1, "name": "Los Angeles", "type": "city", "state_id": 1},
            {"id": 2, "name": "San Francisco", "type": "city", "state_id": 1},
            {"id": 3, "name": "Sacramento", "type": "city", "state_id": 1},
            {"id": 4, "name": "San Diego", "type": "city", "state_id": 1},
            {"id": 5, "name": "Oakland", "type": "city", "state_id": 1},
            
            # New York municipalities
            {"id": 6, "name": "New York City", "type": "city", "state_id": 2},
            {"id": 7, "name": "Buffalo", "type": "city", "state_id": 2},
            {"id": 8, "name": "Rochester", "type": "city", "state_id": 2},
            {"id": 9, "name": "Albany", "type": "city", "state_id": 2},
            
            # Texas municipalities
            {"id": 10, "name": "Houston", "type": "city", "state_id": 3},
            {"id": 11, "name": "Dallas", "type": "city", "state_id": 3},
            {"id": 12, "name": "Austin", "type": "city", "state_id": 3},
            {"id": 13, "name": "San Antonio", "type": "city", "state_id": 3},
            
            # Florida municipalities
            {"id": 14, "name": "Miami", "type": "city", "state_id": 4},
            {"id": 15, "name": "Orlando", "type": "city", "state_id": 4},
            {"id": 16, "name": "Tampa", "type": "city", "state_id": 4},
            {"id": 17, "name": "Jacksonville", "type": "city", "state_id": 4},
            
            # Washington municipalities
            {"id": 18, "name": "Seattle", "type": "city", "state_id": 5},
            {"id": 19, "name": "Spokane", "type": "city", "state_id": 5},
            {"id": 20, "name": "Tacoma", "type": "city", "state_id": 5}
        ]
    
    @staticmethod
    def get_sample_addresses() -> List[Dict[str, Any]]:
        """Get sample address data for testing."""
        return [
            # Los Angeles addresses
            {"id": 1, "street_address": "123 Main Street", "municipality_id": 1},
            {"id": 2, "street_address": "456 Oak Avenue", "municipality_id": 1},
            {"id": 3, "street_address": "789 Pine Road", "municipality_id": 1},
            {"id": 4, "street_address": "321 Elm Street", "municipality_id": 1},
            {"id": 5, "street_address": "654 Maple Drive", "municipality_id": 1},
            {"id": 6, "street_address": "987 Sunset Boulevard", "municipality_id": 1},
            {"id": 7, "street_address": "147 Hollywood Avenue", "municipality_id": 1},
            {"id": 8, "street_address": "258 Beverly Hills Drive", "municipality_id": 1},
            
            # San Francisco addresses
            {"id": 9, "street_address": "100 Market Street", "municipality_id": 2},
            {"id": 10, "street_address": "200 Van Ness Avenue", "municipality_id": 2},
            {"id": 11, "street_address": "300 Lombard Street", "municipality_id": 2},
            {"id": 12, "street_address": "400 Castro Street", "municipality_id": 2},
            {"id": 13, "street_address": "500 Mission Street", "municipality_id": 2},
            
            # Sacramento addresses
            {"id": 14, "street_address": "101 Capitol Mall", "municipality_id": 3},
            {"id": 15, "street_address": "202 J Street", "municipality_id": 3},
            {"id": 16, "street_address": "303 K Street", "municipality_id": 3},
            
            # New York City addresses
            {"id": 17, "street_address": "1 Times Square", "municipality_id": 6},
            {"id": 18, "street_address": "100 Broadway", "municipality_id": 6},
            {"id": 19, "street_address": "200 Fifth Avenue", "municipality_id": 6},
            {"id": 20, "street_address": "300 Park Avenue", "municipality_id": 6},
            {"id": 21, "street_address": "400 Madison Avenue", "municipality_id": 6},
            
            # Houston addresses
            {"id": 22, "street_address": "1000 Main Street", "municipality_id": 10},
            {"id": 23, "street_address": "2000 Texas Avenue", "municipality_id": 10},
            {"id": 24, "street_address": "3000 Memorial Drive", "municipality_id": 10},
            
            # Seattle addresses
            {"id": 25, "street_address": "100 Pike Street", "municipality_id": 18},
            {"id": 26, "street_address": "200 Pine Street", "municipality_id": 18},
            {"id": 27, "street_address": "300 1st Avenue", "municipality_id": 18},
            {"id": 28, "street_address": "400 2nd Avenue", "municipality_id": 18}
        ]
    
    @staticmethod
    def get_sample_data_by_state(state_code: str) -> Dict[str, Any]:
        """Get sample data filtered by state code."""
        states = SampleDataFixtures.get_sample_states()
        municipalities = SampleDataFixtures.get_sample_municipalities()
        addresses = SampleDataFixtures.get_sample_addresses()
        
        # Find the state
        state = next((s for s in states if s["code"] == state_code), None)
        if not state:
            return {"state": None, "municipalities": [], "addresses": []}
        
        # Filter municipalities by state
        state_municipalities = [m for m in municipalities if m["state_id"] == state["id"]]
        municipality_ids = [m["id"] for m in state_municipalities]
        
        # Filter addresses by municipalities in this state
        state_addresses = [a for a in addresses if a["municipality_id"] in municipality_ids]
        
        return {
            "state": state,
            "municipalities": state_municipalities,
            "addresses": state_addresses
        }
    
    @staticmethod
    def get_sample_data_by_municipality(municipality_id: int) -> Dict[str, Any]:
        """Get sample data filtered by municipality ID."""
        states = SampleDataFixtures.get_sample_states()
        municipalities = SampleDataFixtures.get_sample_municipalities()
        addresses = SampleDataFixtures.get_sample_addresses()
        
        # Find the municipality
        municipality = next((m for m in municipalities if m["id"] == municipality_id), None)
        if not municipality:
            return {"municipality": None, "state": None, "addresses": []}
        
        # Find the state
        state = next((s for s in states if s["id"] == municipality["state_id"]), None)
        
        # Filter addresses by municipality
        municipality_addresses = [a for a in addresses if a["municipality_id"] == municipality_id]
        
        return {
            "municipality": municipality,
            "state": state,
            "addresses": municipality_addresses
        }
    
    @staticmethod
    def get_addresses_for_autocomplete(query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get addresses that match autocomplete query."""
        addresses = SampleDataFixtures.get_sample_addresses()
        query_lower = query.lower()
        
        # Filter addresses that contain the query
        matching_addresses = [
            addr for addr in addresses 
            if query_lower in addr["street_address"].lower()
        ]
        
        # Sort by relevance (starts with query first, then contains)
        def sort_key(addr):
            street = addr["street_address"].lower()
            if street.startswith(query_lower):
                return (0, street)
            else:
                return (1, street)
        
        matching_addresses.sort(key=sort_key)
        return matching_addresses[:limit]
    
    @staticmethod
    def get_test_scenarios() -> Dict[str, Dict[str, Any]]:
        """Get predefined test scenarios."""
        return {
            "california_complete": {
                "state": {"id": 1, "code": "CA", "name": "California"},
                "municipality": {"id": 1, "name": "Los Angeles", "type": "city", "state_id": 1},
                "address": {"id": 1, "street_address": "123 Main Street", "municipality_id": 1}
            },
            "new_york_partial": {
                "state": {"id": 2, "code": "NY", "name": "New York"},
                "municipality": {"id": 6, "name": "New York City", "type": "city", "state_id": 2},
                "address": None
            },
            "empty_state": {
                "state": {"id": 100, "code": "MT", "name": "Montana"},
                "municipality": None,
                "address": None
            }
        }
    
    @staticmethod
    def get_validation_test_cases() -> Dict[str, List[Dict[str, Any]]]:
        """Get test cases for validation testing."""
        return {
            "invalid_state_codes": [
                {"code": "", "name": "Empty Code"},
                {"code": "C", "name": "Too Short"},
                {"code": "CAL", "name": "Too Long"},
                {"code": "123", "name": "Numeric Code"},
                {"code": "ca", "name": "Lowercase"}  # Should be handled by normalization
            ],
            "invalid_municipality_names": [
                {"name": "", "type": "city", "state_id": 1},
                {"name": "   ", "type": "city", "state_id": 1},
                {"name": "A" * 256, "type": "city", "state_id": 1}  # Too long
            ],
            "invalid_addresses": [
                {"street_address": "", "municipality_id": 1},
                {"street_address": "   ", "municipality_id": 1},
                {"street_address": "A" * 500, "municipality_id": 1}  # Too long
            ]
        }
    
    @staticmethod
    def get_performance_test_data(size: str = "medium") -> Dict[str, List[Dict[str, Any]]]:
        """Get test data for performance testing."""
        sizes = {
            "small": {"states": 5, "municipalities_per_state": 3, "addresses_per_municipality": 5},
            "medium": {"states": 10, "municipalities_per_state": 10, "addresses_per_municipality": 20},
            "large": {"states": 50, "municipalities_per_state": 20, "addresses_per_municipality": 100}
        }
        
        config = sizes.get(size, sizes["medium"])
        
        # Generate states
        states = []
        for i in range(config["states"]):
            states.append({
                "id": i + 1,
                "code": f"S{i+1:02d}",
                "name": f"State {i+1}"
            })
        
        # Generate municipalities
        municipalities = []
        municipality_id = 1
        for state in states:
            for j in range(config["municipalities_per_state"]):
                municipalities.append({
                    "id": municipality_id,
                    "name": f"City {j+1} in {state['name']}",
                    "type": "city",
                    "state_id": state["id"]
                })
                municipality_id += 1
        
        # Generate addresses
        addresses = []
        address_id = 1
        for municipality in municipalities:
            for k in range(config["addresses_per_municipality"]):
                addresses.append({
                    "id": address_id,
                    "street_address": f"{(k+1)*100} Street {k+1}",
                    "municipality_id": municipality["id"]
                })
                address_id += 1
        
        return {
            "states": states,
            "municipalities": municipalities,
            "addresses": addresses
        }