"""
Integration tests for Municipalities API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.municipality
class TestMunicipalitiesAPI:
    """Integration test suite for Municipalities API endpoints."""

    @pytest.mark.asyncio
    async def test_get_municipalities_in_state_success(self, test_client, sample_states, sample_municipalities):
        """Test GET /states/{state_code}/municipalities with valid state."""
        response = test_client.get("/states/CA/municipalities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "municipalities" in data
        assert "state" in data
        assert "total_count" in data
        
        # Verify municipalities data
        municipalities = data["municipalities"]
        assert len(municipalities) == 3  # LA, SF, Sacramento
        
        municipality_names = {m["name"] for m in municipalities}
        expected_names = {"Los Angeles", "San Francisco", "Sacramento"}
        assert municipality_names == expected_names
        
        # Verify state data
        state = data["state"]
        assert state["code"] == "CA"
        assert state["name"] == "California"
        
        # Verify count
        assert data["total_count"] == len(municipalities)

    @pytest.mark.asyncio
    async def test_get_municipalities_in_state_lowercase(self, test_client, sample_states, sample_municipalities):
        """Test GET /states/{state_code}/municipalities with lowercase state code."""
        response = test_client.get("/states/ca/municipalities")
        
        assert response.status_code == 200
        data = response.json()
        assert data["state"]["code"] == "CA"

    def test_get_municipalities_in_state_not_found(self, test_client):
        """Test GET /states/{state_code}/municipalities with non-existent state."""
        response = test_client.get("/states/XX/municipalities")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_municipalities_in_state_invalid_code(self, test_client):
        """Test GET /states/{state_code}/municipalities with invalid state code."""
        response = test_client.get("/states/C/municipalities")
        assert response.status_code == 422
        
        response = test_client.get("/states/CAL/municipalities")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_municipalities_in_state_empty(self, test_client, clean_db):
        """Test GET /states/{state_code}/municipalities with state that has no municipalities."""
        # Create a state with no municipalities
        state_data = {"code": "MT", "name": "Montana"}
        state_response = test_client.post("/states", json=state_data)
        
        response = test_client.get("/states/MT/municipalities")
        
        assert response.status_code == 200
        data = response.json()
        assert data["municipalities"] == []
        assert data["total_count"] == 0
        assert data["state"]["code"] == "MT"

    @pytest.mark.asyncio
    async def test_get_municipality_by_id_success(self, test_client, sample_states, sample_municipalities):
        """Test GET /municipalities/{municipality_id} with valid ID."""
        # Get a municipality ID
        la_municipality = next(m for m in sample_municipalities if m["name"] == "Los Angeles")
        municipality_id = la_municipality["id"]
        
        response = test_client.get(f"/municipalities/{municipality_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == municipality_id
        assert data["name"] == "Los Angeles"
        assert data["type"] == "city"
        assert "state_id" in data

    def test_get_municipality_by_id_not_found(self, test_client):
        """Test GET /municipalities/{municipality_id} with non-existent ID."""
        response = test_client.get("/municipalities/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_municipality_by_id_invalid_id(self, test_client):
        """Test GET /municipalities/{municipality_id} with invalid ID format."""
        response = test_client.get("/municipalities/invalid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_municipality_success(self, test_client, sample_states):
        """Test POST /municipalities with valid data."""
        ca_state = next(state for state in sample_states if state["code"] == "CA")
        
        municipality_data = {
            "name": "Oakland",
            "type": "city",
            "state_id": ca_state["id"]
        }
        
        response = test_client.post("/municipalities", json=municipality_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Oakland"
        assert data["type"] == "city"
        assert data["state_id"] == ca_state["id"]
        assert "id" in data

    def test_create_municipality_invalid_state(self, test_client):
        """Test POST /municipalities with invalid state ID."""
        municipality_data = {
            "name": "Test City",
            "type": "city",
            "state_id": 999  # Non-existent state
        }
        
        response = test_client.post("/municipalities", json=municipality_data)
        
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"].lower()

    def test_create_municipality_invalid_data(self, test_client):
        """Test POST /municipalities with invalid data."""
        # Missing required fields
        response = test_client.post("/municipalities", json={})
        assert response.status_code == 422
        
        # Invalid field types
        response = test_client.post("/municipalities", json={
            "name": 123,  # Should be string
            "type": "city",
            "state_id": 1
        })
        assert response.status_code == 422
        
        # Empty values
        response = test_client.post("/municipalities", json={
            "name": "",
            "type": "",
            "state_id": 1
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_municipalities_api_data_integrity(self, test_client, sample_states, sample_municipalities):
        """Test data integrity constraints in municipalities API."""
        # Verify municipalities have valid state_id
        response = test_client.get("/states/CA/municipalities")
        municipalities = response.json()["municipalities"]
        
        ca_state = next(state for state in sample_states if state["code"] == "CA")
        
        for municipality in municipalities:
            assert municipality["state_id"] == ca_state["id"]

    @pytest.mark.asyncio 
    async def test_municipalities_api_ordering(self, test_client, sample_states, sample_municipalities):
        """Test that municipalities are returned in correct order."""
        response = test_client.get("/states/CA/municipalities")
        municipalities = response.json()["municipalities"]
        
        # Verify municipalities are ordered by name
        municipality_names = [m["name"] for m in municipalities]
        assert municipality_names == sorted(municipality_names)

    @pytest.mark.asyncio
    async def test_municipalities_api_multiple_states(self, test_client, sample_states, sample_municipalities):
        """Test municipalities API with multiple states."""
        # Test California municipalities
        ca_response = test_client.get("/states/CA/municipalities")
        ca_data = ca_response.json()
        ca_count = ca_data["total_count"]
        
        # Test New York municipalities  
        ny_response = test_client.get("/states/NY/municipalities")
        ny_data = ny_response.json()
        ny_count = ny_data["total_count"]
        
        # Test Texas municipalities
        tx_response = test_client.get("/states/TX/municipalities")
        tx_data = tx_response.json()
        tx_count = tx_data["total_count"]
        
        # Verify different states have different municipalities
        assert ca_count == 3  # LA, SF, Sacramento
        assert ny_count == 2  # New York, Buffalo  
        assert tx_count == 2  # Houston, Dallas

    @pytest.mark.asyncio
    async def test_municipalities_api_state_validation(self, test_client, sample_states, sample_municipalities):
        """Test that municipalities API validates state exists."""
        # Valid state
        response = test_client.get("/states/CA/municipalities")
        assert response.status_code == 200
        
        # Invalid state
        response = test_client.get("/states/ZZ/municipalities")
        assert response.status_code == 404

    def test_municipalities_api_content_type(self, test_client, sample_states):
        """Test that municipalities endpoints return proper content type."""
        response = test_client.get("/states/CA/municipalities")
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_municipalities_api_performance(self, test_client, sample_states, sample_municipalities):
        """Test basic performance of municipalities API."""
        import time
        
        start_time = time.time()
        response = test_client.get("/states/CA/municipalities") 
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in under 1 second

    @pytest.mark.asyncio
    async def test_municipalities_response_structure(self, test_client, sample_states, sample_municipalities):
        """Test municipalities API response structure consistency."""
        response = test_client.get("/states/CA/municipalities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify top-level structure
        required_fields = ["municipalities", "state", "total_count"]
        for field in required_fields:
            assert field in data
        
        # Verify municipality structure
        if data["municipalities"]:
            municipality = data["municipalities"][0]
            municipality_fields = ["id", "name", "type", "state_id"]
            for field in municipality_fields:
                assert field in municipality
        
        # Verify state structure
        state = data["state"] 
        state_fields = ["id", "code", "name"]
        for field in state_fields:
            assert field in state

    @pytest.mark.asyncio
    async def test_municipalities_api_error_consistency(self, test_client):
        """Test error response consistency in municipalities API."""
        # Test 404 errors
        response = test_client.get("/states/XX/municipalities")
        assert response.status_code == 404
        assert "detail" in response.json()
        
        response = test_client.get("/municipalities/999")
        assert response.status_code == 404
        assert "detail" in response.json()
        
        # Test 422 errors
        response = test_client.get("/states/C/municipalities") 
        assert response.status_code == 422
        
        response = test_client.get("/municipalities/invalid")
        assert response.status_code == 422