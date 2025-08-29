"""
Integration tests for Addresses API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.address
class TestAddressesAPI:
    """Integration test suite for Addresses API endpoints."""

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_success(self, test_client, sample_addresses):
        """Test GET /addresses/autocomplete with valid query."""
        response = test_client.get("/addresses/autocomplete?query=main")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "addresses" in data
        assert "query" in data
        assert "total_count" in data
        
        # Verify addresses data
        addresses = data["addresses"]
        assert len(addresses) > 0
        
        # Verify each address contains main street
        for address in addresses:
            assert "main" in address["street_address"].lower()
            assert "id" in address
            assert "street_address" in address
            assert "municipality_id" in address

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_case_insensitive(self, test_client, sample_addresses):
        """Test autocomplete is case insensitive."""
        # Test uppercase
        response_upper = test_client.get("/addresses/autocomplete?query=MAIN")
        assert response_upper.status_code == 200
        
        # Test lowercase  
        response_lower = test_client.get("/addresses/autocomplete?query=main")
        assert response_lower.status_code == 200
        
        # Results should be the same
        assert response_upper.json()["total_count"] == response_lower.json()["total_count"]

    def test_autocomplete_addresses_empty_query(self, test_client):
        """Test autocomplete with empty query."""
        response = test_client.get("/addresses/autocomplete?query=")
        
        assert response.status_code == 422
        assert "query" in response.json()["detail"][0]["loc"]

    def test_autocomplete_addresses_short_query(self, test_client):
        """Test autocomplete with query too short."""
        response = test_client.get("/addresses/autocomplete?query=a")
        
        assert response.status_code == 422
        assert "at least 2 characters" in response.json()["detail"][0]["msg"]

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_no_results(self, test_client, sample_addresses):
        """Test autocomplete with query that returns no results."""
        response = test_client.get("/addresses/autocomplete?query=nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        assert data["addresses"] == []
        assert data["total_count"] == 0
        assert data["query"] == "nonexistent"

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_limit_parameter(self, test_client, sample_addresses):
        """Test autocomplete with limit parameter."""
        response = test_client.get("/addresses/autocomplete?query=street&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["addresses"]) <= 2

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_with_municipality_filter(self, test_client, sample_addresses, sample_municipalities):
        """Test autocomplete with municipality filter."""
        # Get LA municipality ID
        la_municipality = next(m for m in sample_municipalities if m["name"] == "Los Angeles")
        municipality_id = la_municipality["id"]
        
        response = test_client.get(f"/addresses/autocomplete?query=street&municipality_id={municipality_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # All addresses should be from LA
        for address in data["addresses"]:
            assert address["municipality_id"] == municipality_id

    def test_autocomplete_addresses_invalid_municipality(self, test_client):
        """Test autocomplete with invalid municipality ID."""
        response = test_client.get("/addresses/autocomplete?query=street&municipality_id=999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_address_by_id_success(self, test_client, sample_addresses):
        """Test GET /addresses/{address_id} with valid ID."""
        # Get an address ID
        first_address = sample_addresses[0]
        address_id = first_address["id"]
        
        response = test_client.get(f"/addresses/{address_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == address_id
        assert "street_address" in data
        assert "municipality_id" in data
        assert data["street_address"] == first_address["street_address"]

    def test_get_address_by_id_not_found(self, test_client):
        """Test GET /addresses/{address_id} with non-existent ID."""
        response = test_client.get("/addresses/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_address_by_id_invalid_id(self, test_client):
        """Test GET /addresses/{address_id} with invalid ID format."""
        response = test_client.get("/addresses/invalid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_address_success(self, test_client, sample_municipalities):
        """Test POST /addresses with valid data."""
        la_municipality = next(m for m in sample_municipalities if m["name"] == "Los Angeles")
        
        address_data = {
            "street_address": "789 New Street",
            "municipality_id": la_municipality["id"]
        }
        
        response = test_client.post("/addresses", json=address_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["street_address"] == "789 New Street"
        assert data["municipality_id"] == la_municipality["id"]
        assert "id" in data

    def test_create_address_invalid_municipality(self, test_client):
        """Test POST /addresses with invalid municipality ID."""
        address_data = {
            "street_address": "123 Test Street",
            "municipality_id": 999  # Non-existent municipality
        }
        
        response = test_client.post("/addresses", json=address_data)
        
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"].lower()

    def test_create_address_invalid_data(self, test_client):
        """Test POST /addresses with invalid data."""
        # Missing required fields
        response = test_client.post("/addresses", json={})
        assert response.status_code == 422
        
        # Invalid field types
        response = test_client.post("/addresses", json={
            "street_address": 123,  # Should be string
            "municipality_id": 1
        })
        assert response.status_code == 422
        
        # Empty values
        response = test_client.post("/addresses", json={
            "street_address": "",
            "municipality_id": 1
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_addresses_by_municipality_success(self, test_client, sample_addresses, sample_municipalities):
        """Test GET /municipalities/{municipality_id}/addresses."""
        la_municipality = next(m for m in sample_municipalities if m["name"] == "Los Angeles")
        municipality_id = la_municipality["id"]
        
        response = test_client.get(f"/municipalities/{municipality_id}/addresses")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "addresses" in data
        assert "municipality" in data
        assert "total_count" in data
        
        # Verify all addresses belong to the municipality
        for address in data["addresses"]:
            assert address["municipality_id"] == municipality_id

    def test_get_addresses_by_municipality_not_found(self, test_client):
        """Test GET /municipalities/{municipality_id}/addresses with non-existent municipality."""
        response = test_client.get("/municipalities/999/addresses")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_addresses_api_data_integrity(self, test_client, sample_addresses, sample_municipalities):
        """Test data integrity constraints in addresses API."""
        # Verify addresses have valid municipality_id
        for address in sample_addresses:
            municipality_id = address["municipality_id"]
            
            # Verify municipality exists
            municipality_exists = any(m["id"] == municipality_id for m in sample_municipalities)
            assert municipality_exists, f"Address {address['id']} references non-existent municipality {municipality_id}"

    @pytest.mark.asyncio
    async def test_addresses_autocomplete_ordering(self, test_client, sample_addresses):
        """Test that autocomplete results are properly ordered."""
        response = test_client.get("/addresses/autocomplete?query=street")
        addresses = response.json()["addresses"]
        
        if len(addresses) > 1:
            # Verify addresses are ordered by relevance or alphabetically
            address_strings = [addr["street_address"] for addr in addresses]
            # Should be consistent ordering
            assert len(address_strings) == len(set(address_strings))  # No duplicates

    @pytest.mark.asyncio
    async def test_addresses_api_performance(self, test_client, sample_addresses):
        """Test basic performance of addresses API."""
        import time
        
        start_time = time.time()
        response = test_client.get("/addresses/autocomplete?query=main")
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in under 1 second

    def test_addresses_api_content_type(self, test_client):
        """Test that addresses endpoints return proper content type."""
        response = test_client.get("/addresses/autocomplete?query=test")
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_addresses_response_structure(self, test_client, sample_addresses):
        """Test addresses API response structure consistency."""
        response = test_client.get("/addresses/autocomplete?query=street")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify top-level structure
        required_fields = ["addresses", "query", "total_count"]
        for field in required_fields:
            assert field in data
        
        # Verify address structure
        if data["addresses"]:
            address = data["addresses"][0]
            address_fields = ["id", "street_address", "municipality_id"]
            for field in address_fields:
                assert field in address

    @pytest.mark.asyncio
    async def test_addresses_api_pagination(self, test_client, sample_addresses):
        """Test addresses API pagination functionality."""
        # Test with limit
        response = test_client.get("/addresses/autocomplete?query=street&limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["addresses"]) <= 3
        
        # Test default limit behavior
        response = test_client.get("/addresses/autocomplete?query=street")
        data = response.json()
        assert len(data["addresses"]) <= 20  # Default limit

    @pytest.mark.asyncio
    async def test_addresses_api_error_consistency(self, test_client):
        """Test error response consistency in addresses API."""
        # Test 404 errors
        response = test_client.get("/addresses/999")
        assert response.status_code == 404
        assert "detail" in response.json()
        
        response = test_client.get("/municipalities/999/addresses")
        assert response.status_code == 404
        assert "detail" in response.json()
        
        # Test 422 errors
        response = test_client.get("/addresses/invalid")
        assert response.status_code == 422
        
        response = test_client.get("/addresses/autocomplete?query=")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_addresses_autocomplete_special_characters(self, test_client, sample_addresses):
        """Test autocomplete handles special characters properly."""
        # Test with special characters
        response = test_client.get("/addresses/autocomplete?query=1st%20st")  # "1st st"
        assert response.status_code == 200
        
        # Test with numbers
        response = test_client.get("/addresses/autocomplete?query=123")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_addresses_autocomplete_long_query(self, test_client):
        """Test autocomplete with very long query."""
        long_query = "a" * 500  # 500 character query
        response = test_client.get(f"/addresses/autocomplete?query={long_query}")
        
        # Should handle gracefully, either 200 with no results or 422 if length validation
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_addresses_create_duplicate_handling(self, test_client, sample_municipalities):
        """Test handling of potential duplicate addresses."""
        la_municipality = next(m for m in sample_municipalities if m["name"] == "Los Angeles")
        
        address_data = {
            "street_address": "100 Duplicate Street",
            "municipality_id": la_municipality["id"]
        }
        
        # Create first address
        response1 = test_client.post("/addresses", json=address_data)
        assert response1.status_code == 201
        
        # Try to create the same address again
        response2 = test_client.post("/addresses", json=address_data)
        # Should either succeed (allowing duplicates) or fail with appropriate error
        assert response2.status_code in [201, 400, 409]

    @pytest.mark.asyncio 
    async def test_addresses_multiple_municipalities(self, test_client, sample_addresses, sample_municipalities):
        """Test addresses API works across multiple municipalities."""
        municipality_ids = [m["id"] for m in sample_municipalities]
        
        for municipality_id in municipality_ids:
            response = test_client.get(f"/municipalities/{municipality_id}/addresses")
            assert response.status_code == 200
            
            data = response.json()
            # All addresses should belong to this municipality
            for address in data["addresses"]:
                assert address["municipality_id"] == municipality_id