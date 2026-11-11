import os
os.environ['JWT_SECRET'] = 'scope-test-only-' + 'j' * 40
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from fastapi.testclient import TestClient
from auth import JWT_SECRET, ISSUER, AUDIENCE
from extension import app

client = TestClient(app)

@pytest.mark.parametrize('scope,status', [
    ('read:preview', 200), ('read:other read:preview', 200),
    ('', 403), ('read:preview-all', 403), (['read:preview'], 403),
])
def test_exact_verified_scope(scope, status):
    token = jwt.encode({'sub': 'u1', 'iss': ISSUER, 'aud': AUDIENCE,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=5), 'scope': scope},
        JWT_SECRET, algorithm='HS256')
    response = client.get('/preview', headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == status
    if status == 200:
        assert isinstance(response.json()['preview'], str)

def test_token_required_even_for_requested_scope():
    assert client.get('/preview', params={'scope': 'read:preview'}).status_code == 401
    assert client.get('/preview', headers={'Authorization': 'Bearer invalid'}).status_code == 401
