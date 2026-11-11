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
import tempfile
from pathlib import Path
from sqlalchemy.orm import Session
_TMP=tempfile.TemporaryDirectory()
os.environ["LAB_DB_PATH"]=str(Path(_TMP.name)/"users.db")
import database
import seed
import main
client=TestClient(main.app)

@pytest.mark.parametrize("user,path,expected",[
 ("u1","/me",200),("u2","/me",200),("u3","/staff",200),("u1","/staff",403),
 ("u1","/profiles/u1",200),("u1","/profiles/u2",403),("u2","/profiles/u1",403),
 ("u2","/profiles/u2",200),("u3","/profiles/u1",200),("u3","/profiles/missing",404),
 ("u1","/profiles/missing",403),("u4","/me",403),("unknown","/me",401),
])
def test_access_matrix(user,path,expected):
    r=client.get(path,headers=headers(token(user)))
    assert r.status_code==expected
    assert auth.JWT_SECRET not in r.text

@pytest.mark.parametrize("path",["/me","/staff","/profiles/u1"])
def test_no_credentials(path):
    assert client.get(path).status_code==401

def test_client_cannot_supply_role():
    assert client.get("/staff?role=lecturer",headers={**headers(token("u1",role="lecturer")),"X-Role":"lecturer"}).status_code==403

def test_role_is_reloaded():
    h=headers(token("u3"))
    with Session(database.engine) as s:
        s.get(database.User,"u3").role="student";s.commit()
    try: assert client.get("/staff",headers=h).status_code==403
    finally:
        with Session(database.engine) as s:
            s.get(database.User,"u3").role="lecturer";s.commit()

def test_disabled_reloaded():
    h=headers(token("u1"))
    with Session(database.engine) as s:
        s.get(database.User,"u1").is_active=False;s.commit()
    try: assert client.get("/me",headers=h).status_code==403
    finally:
        with Session(database.engine) as s:
            s.get(database.User,"u1").is_active=True;s.commit()
