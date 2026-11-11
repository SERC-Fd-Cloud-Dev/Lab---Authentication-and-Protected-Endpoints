import os
import tempfile
from pathlib import Path
os.environ['JWT_SECRET'] = 'report-test-only-' + 'j' * 40
_temp = tempfile.TemporaryDirectory()
os.environ['LAB_DB_PATH'] = str(Path(_temp.name) / 'report-test.db')
import seed
import add_reporter
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from fastapi.testclient import TestClient
from auth import JWT_SECRET, ISSUER, AUDIENCE
from extension import app

client = TestClient(app)

def headers(subject):
    token = jwt.encode({'sub': subject, 'iss': ISSUER, 'aud': AUDIENCE,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=5)}, JWT_SECRET, algorithm='HS256')
    return {'Authorization': 'Bearer ' + token}

@pytest.mark.parametrize('subject,status', [('u1',403),('u3',200),('u4',403),('u5',200),('missing',401)])
def test_reporting_permission(subject, status):
    response = client.get('/reports/summary', headers=headers(subject))
    assert response.status_code == status
    if status == 200:
        assert response.json() == {'active_accounts': 4}

def test_service_has_only_its_permissions():
    assert client.get('/me', headers=headers('u5')).status_code == 200
    assert client.get('/staff', headers=headers('u5')).status_code == 403
    assert client.get('/profiles/u1', headers=headers('u5')).status_code == 403
    assert client.get('/reports/summary').status_code == 401
