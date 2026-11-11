import os
os.environ['LAB_API_KEY'] = 'rotation-current-test-' + 'a' * 40
os.environ['LAB_API_KEY_NEXT'] = 'rotation-next-test-' + 'b' * 40
import pytest
from fastapi.testclient import TestClient
from extension import app

client = TestClient(app)

@pytest.mark.parametrize('path', ['/protected', '/status', '/lab-info'])
@pytest.mark.parametrize('key,status', [
    (os.environ['LAB_API_KEY'], 200),
    (os.environ['LAB_API_KEY_NEXT'], 200),
    ('unknown', 401), (None, 401),
])
def test_rotation_keeps_the_boundary(path, key, status):
    headers = {} if key is None else {'X-API-Key': key}
    response = client.get(path, headers=headers)
    assert response.status_code == status
    assert os.environ['LAB_API_KEY'] not in response.text
    assert os.environ['LAB_API_KEY_NEXT'] not in response.text

def test_public_stays_public_and_query_key_does_not_work():
    assert client.get('/public').status_code == 200
    assert client.get('/protected', params={'api_key': os.environ['LAB_API_KEY_NEXT']}).status_code == 401
