import logging
from starlette.testclient import TestClient
from main import app
from app.models.objects import DrsObject
from app.api.endpoints.objects import router as api_router
from app.business.oauth import auth_request

#api_client = TestClient(app)

async def override_auth(q: str = None):
    return {'sub': '6881b886938c9fbd5aed4b3d1fec035955a9f87b@elixir-europe.org', 'kid': 'rsa1', 'iss': 'https://login.elixir-czech.org/oidc/', 'preferred_username': 'soumyadip', 'given_name': 'Soumyadip', 'aud': '79e2eb28-dd2a-4239-9f53-e9063762e8ed', 'name': 'Soumyadip De', 'family_name': 'De', 'email': 'soumyadip@ebi.ac.uk'}

def test_get_object_403():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/0430d58d1199abc6310c7b51fedac148cc3b2d08c4c2dd5f40861e6ef930d7cf1502b92fa945a625acf80ef1dd2d3ea68d6b80e45043ec212f8f891fe2e48b91")
        assert response.status_code == 403

# This test case will enable auth for next test cases
def test_override_dependency():
    app.dependency_overrides[auth_request] = override_auth

def test_get_object_success():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/0430d58d1199abc6310c7b51fedac148cc3b2d08c4c2dd5f40861e6ef930d7cf1502b92fa945a625acf80ef1dd2d3ea68d6b80e45043ec212f8f891fe2e48b91")
        assert response.status_code == 200
        drsObject = DrsObject(**response.json())
        assert drsObject.id == '0430d58d1199abc6310c7b51fedac148cc3b2d08c4c2dd5f40861e6ef930d7cf1502b92fa945a625acf80ef1dd2d3ea68d6b80e45043ec212f8f891fe2e48b91'
        
def test_get_object_404():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/test")
        assert response.status_code == 404
        assert response.json().get('msg') == 'Requested DrsObject was not found'
    

