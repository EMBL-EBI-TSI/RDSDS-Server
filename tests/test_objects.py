import logging
from starlette.testclient import TestClient
from main import app
from app.models.objects import DrsObject
from app.api.endpoints.objects import router as api_router

#api_client = TestClient(app)

def test_get_object_success():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/0430d58d1199abc6310c7b51fedac148cc3b2d08c4c2dd5f40861e6ef930d7cf1502b92fa945a625acf80ef1dd2d3ea68d6b80e45043ec212f8f891fe2e48b91")
        assert response.status_code == 200
        drsObject = DrsObject(**response.json())
        assert drsObject.id == '0430d58d1199abc6310c7b51fedac148cc3b2d08c4c2dd5f40861e6ef930d7cf1502b92fa945a625acf80ef1dd2d3ea68d6b80e45043ec212f8f891fe2e48b91'

def test_get_bundle_success():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/9b338448d613f4aed943d811a76d2350fc719b1bc334c0b64f442ed2f86848d07882958fb24000989a9986dcfaa492509ce02fb77586a60899544e9bda2dcfc1")
        assert response.status_code == 200
        drsObject = DrsObject(**response.json())
        assert drsObject.id == '9b338448d613f4aed943d811a76d2350fc719b1bc334c0b64f442ed2f86848d07882958fb24000989a9986dcfaa492509ce02fb77586a60899544e9bda2dcfc1'


def test_get_object_404():
    with TestClient(app) as api_client:
        response = api_client.get("/ga4gh/drs/v1/objects/test")
        assert response.status_code == 404
        assert response.json().get('msg') == 'Requested DrsObject was not found'
    
