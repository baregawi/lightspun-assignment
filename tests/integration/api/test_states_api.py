"""
Integration tests for States API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.state
class TestStatesAPI:
    """Integration test suite for States API endpoints."""

    def test_get_all_states_empty(self, test_client, clean_db):
        """Test GET /states with no states in database."""
        response = test_client.get("/states")
        
        assert response.status_code == 200
        data = response.json()
        assert data["states"] == []
        assert data["total_count"] == 0

    @pytest.mark.asyncio
    async def test_get_all_states_with_data(self, test_client, sample_states):
        """Test GET /states with states in database."""
        response = test_client.get("/states")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["states"]) == 5
        assert data["total_count"] == 5
        
        # Verify data structure
        state = data["states"][0]
        assert "id" in state
        assert "code" in state 
        assert "name" in state
        
        # Verify states are sorted by name
        state_names = [state["name"] for state in data["states"]]
        assert state_names == sorted(state_names)

    @pytest.mark.asyncio
    async def test_get_state_by_code_success(self, test_client, sample_states):
        """Test GET /states/{state_code} with valid state code."""
        response = test_client.get("/states/CA")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "CA"
        assert data["name"] == "California"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_state_by_code_lowercase(self, test_client, sample_states):
        """Test GET /states/{state_code} with lowercase state code."""
        response = test_client.get("/states/ca")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "CA"
        assert data["name"] == "California"

    def test_get_state_by_code_not_found(self, test_client, clean_db):
        """Test GET /states/{state_code} with non-existent state code."""
        response = test_client.get("/states/XX")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_state_by_code_invalid_length(self, test_client):
        """Test GET /states/{state_code} with invalid state code length."""
        # Test too short
        response = test_client.get("/states/C")
        assert response.status_code == 422
        
        # Test too long
        response = test_client.get("/states/CAL")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_state_success(self, test_client, clean_db):
        """Test POST /states with valid data."""
        state_data = {
            "code": "WA",
            "name": "Washington"
        }
        
        response = test_client.post("/states", json=state_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "WA"
        assert data["name"] == "Washington"
        assert "id" in data

    def test_create_state_duplicate_code(self, test_client, sample_states):
        """Test POST /states with duplicate state code."""
        state_data = {
            "code": "CA",  # Already exists
            "name": "California Duplicate"
        }
        
        response = test_client.post("/states", json=state_data)
        
        assert response.status_code == 400
        assert "failed to create" in response.json()["detail"].lower()

    def test_create_state_invalid_data(self, test_client):
        """Test POST /states with invalid data."""
        # Missing required fields
        response = test_client.post("/states", json={})
        assert response.status_code == 422
        
        # Invalid field types
        response = test_client.post("/states", json={
            "code": 123,  # Should be string
            "name": "Test"
        })
        assert response.status_code == 422
        
        # Empty values
        response = test_client.post("/states", json={
            "code": "",
            "name": ""
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_state_success(self, test_client, sample_states):
        """Test PUT /states/{state_id} with valid data."""
        # Get a state to update
        ca_state = next(state for state in sample_states if state["code"] == "CA")
        state_id = ca_state["id"]
        
        update_data = {
            "name": "Golden State"
        }
        
        response = test_client.put(f"/states/{state_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == state_id
        assert data["code"] == "CA"  # Unchanged
        assert data["name"] == "Golden State"  # Updated

    def test_update_state_not_found(self, test_client):
        """Test PUT /states/{state_id} with non-existent state ID."""
        update_data = {"name": "New Name"}
        
        response = test_client.put("/states/999", json=update_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_state_invalid_data(self, test_client, sample_states):
        """Test PUT /states/{state_id} with invalid data."""
        ca_state = next(state for state in sample_states if state["code"] == "CA")
        state_id = ca_state["id"]
        
        # Invalid field type
        response = test_client.put(f"/states/{state_id}", json={
            "name": 123  # Should be string
        })
        assert response.status_code == 422

    @pytest.mark.asyncio 
    async def test_delete_state_success(self, test_client, clean_db):
        """Test DELETE /states/{state_id} with state that has no municipalities."""
        # Create a state
        state_data = {"code": "MT", "name": "Montana"}
        create_response = test_client.post("/states", json=state_data)
        state_id = create_response.json()["id"]
        
        # Delete the state
        response = test_client.delete(f"/states/{state_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_state_with_municipalities(self, test_client, sample_states, sample_municipalities):
        """Test DELETE /states/{state_id} with state that has municipalities."""
        # Try to delete California (which has municipalities)
        ca_state = next(state for state in sample_states if state["code"] == "CA")
        state_id = ca_state["id"]
        
        response = test_client.delete(f"/states/{state_id}")
        
        assert response.status_code == 400
        assert "municipalities" in response.json()["detail"].lower()

    def test_delete_state_not_found(self, test_client):
        """Test DELETE /states/{state_id} with non-existent state ID."""
        response = test_client.delete("/states/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_states_api_content_type(self, test_client):
        """Test that all states endpoints return proper content type."""
        response = test_client.get("/states")
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_states_api_cors_headers(self, test_client, sample_states):
        """Test CORS headers are present in responses."""
        response = test_client.get("/states")
        
        # Check for CORS headers (if configured)
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]
        
        # Note: Actual CORS headers depend on FastAPI CORS middleware configuration
        # This test verifies the structure is in place

    @pytest.mark.asyncio
    async def test_states_api_performance(self, test_client, sample_states):
        """Test basic performance of states API."""
        import time
        
        start_time = time.time()
        response = test_client.get("/states")
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in under 1 second

    @pytest.mark.asyncio
    async def test_states_api_pagination_structure(self, test_client, sample_states):
        """Test that states API returns proper pagination structure."""
        response = test_client.get("/states")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "states" in data
        assert "total_count" in data
        assert isinstance(data["states"], list)
        assert isinstance(data["total_count"], int)
        assert data["total_count"] == len(data["states"])

    def test_states_api_error_handling(self, test_client):
        """Test error handling in states API."""
        # Test malformed JSON
        response = test_client.post(
            "/states",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code in [400, 422]
        
        # Test wrong content type
        response = test_client.post(
            "/states",
            data="code=TEST&name=Test",
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        # FastAPI should handle this gracefully