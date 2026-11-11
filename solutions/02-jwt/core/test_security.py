import os
os.environ["LAB_API_KEY"] = "unit-test-only-key-" + "x" * 32
os.environ["JWT_SECRET"] = "unit-test-only-signing-" + "j" * 32
os.environ["TMDB_API_KEY"] = "synthetic-upstream-key"
os.environ["GAME_API_KEY"] = "unit-test-only-game-" + "g" * 32
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from fastapi.testclient import TestClient
import auth

def token(subject="u1", **changes):
    claims={"sub":subject,"exp":datetime.now(timezone.utc)+timedelta(minutes=5),"iss":auth.ISSUER,"aud":auth.AUDIENCE}
    claims.update(changes)
    for key in list(claims):
        if claims[key] is None: del claims[key]
    return jwt.encode(claims,auth.JWT_SECRET,algorithm="HS256")

def headers(value):
    return {"Authorization":"Bearer "+value}
import main
client=TestClient(main.app)

@pytest.mark.parametrize("path",["/me","/token-info","/badge"])
def test_valid(path):
    assert client.get(path,headers=headers(token())).status_code==200

@pytest.mark.parametrize("bad",[
    "not-a-token", token(exp=0),token(exp=None),token(sub=None),token(subject=""),
    token(iss="wrong"),token(aud="wrong"),token(iss=None),token(aud=None),
    jwt.encode({"sub":"u1","exp":9999999999,"iss":auth.ISSUER,"aud":auth.AUDIENCE},"wrong-"+"x"*40,algorithm="HS256"),
    jwt.encode({"sub":"u1","exp":9999999999,"iss":auth.ISSUER,"aud":auth.AUDIENCE},"",algorithm="none"),
])
def test_bad(bad):
    r=client.get("/me",headers=headers(bad))
    assert r.status_code==401
    assert r.headers["www-authenticate"]=="Bearer"

@pytest.mark.parametrize("h",[{}, {"Authorization":"Basic abc"}, {"Authorization":"Bearer "}])
def test_missing(h):
    assert client.get("/me",headers=h).status_code==401

def test_subject_and_no_echo():
    t=token("u2");r=client.get("/badge",headers=headers(t))
    assert r.json()=={"subject":"u2","badge":"authenticated learner"}
    assert t not in r.text and auth.JWT_SECRET not in r.text
