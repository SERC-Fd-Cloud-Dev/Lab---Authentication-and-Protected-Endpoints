import os
os.environ["LAB_API_KEY"] = "unit-test-only-key-" + "x" * 32
os.environ["JWT_SECRET"] = "unit-test-only-signing-" + "j" * 32
os.environ["TMDB_API_KEY"] = "synthetic-upstream-key"
os.environ["GAME_API_KEY"] = "unit-test-only-game-" + "g" * 32
import pytest
from fastapi.testclient import TestClient
import main
client = TestClient(main.app)

@pytest.mark.parametrize("path", ["/protected", "/status", "/lab-info"])
@pytest.mark.parametrize("key,expected", [(None,401),("wrong",401),(os.environ["LAB_API_KEY"],200)])
def test_key_matrix(path,key,expected):
    response=client.get(path,headers={} if key is None else {"X-API-Key":key})
    assert response.status_code == expected
    assert os.environ["LAB_API_KEY"] not in response.text
    if expected==401: assert response.headers["www-authenticate"] == "APIKey"

def test_query_is_not_header():
    assert client.get("/protected",params={"api_key":os.environ["LAB_API_KEY"]}).status_code==401

def test_public_and_openapi():
    assert client.get("/public").status_code==200
    schema=client.get("/openapi.json").json()
    assert schema["components"]["securitySchemes"]["APIKeyHeader"]["in"]=="header"
    assert "security" not in schema["paths"]["/public"]["get"]
