from starlette.testclient import TestClient
from main import app

api_client = TestClient(app)

def test_health_check():
    response = api_client.get("/health-check")
    assert response.status_code == 200
    
