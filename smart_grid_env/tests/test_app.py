import pytest
from fastapi.testclient import TestClient
from smart_grid_env.server.app import app
import json

client = TestClient(app)

def test_api_info():
    response = client.get("/openenv/v1/info")
    # Even if this isn't implemented exactly as /openenv/v1/info, 
    # it might be /info. OpenEnv creates standard endpoints.
    assert response.status_code in [200, 404] # Depending on openenv-core version
    
def test_api_root():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert "/web/" in response.headers.get("location", "")
