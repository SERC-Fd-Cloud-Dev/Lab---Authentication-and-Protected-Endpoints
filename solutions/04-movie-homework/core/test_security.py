import os
os.environ["LAB_API_KEY"] = "unit-test-only-key-" + "x" * 32
os.environ["JWT_SECRET"] = "unit-test-only-signing-" + "j" * 32
os.environ["TMDB_API_KEY"] = "synthetic-upstream-key"
os.environ["GAME_API_KEY"] = "unit-test-only-game-" + "g" * 32
import httpx
import pytest
from fastapi.testclient import TestClient
import main
client=TestClient(main.app)
MOVIE={"title":"The Hidden Signal","release_date":"2020-02-03","genres":[{"name":"Mystery"}],"runtime":101}

def mock_response(status=200,data=None):
    return httpx.Response(status,json=MOVIE if data is None else data,request=httpx.Request("GET","https://api.themoviedb.org/3/movie/603"))

def test_clue_and_answer(monkeypatch):
    seen=[]
    def fake(url,**kwargs):
        seen.append((url,kwargs)); return mock_response()
    monkeypatch.setattr(main.httpx,"get",fake)
    r=client.get("/movie/clue")
    assert r.json()=={"year":2020,"genres":["Mystery"],"runtime":101}
    assert "The Hidden Signal" not in r.text and "title" not in r.text
    assert client.get("/movie/answer",headers={"X-API-Key":main.GAME_KEY}).json()=={"title":"The Hidden Signal"}
    assert all(x[1]["params"]["api_key"]==main.TMDB_KEY and x[1]["timeout"]==5.0 for x in seen)
    assert all(main.TMDB_KEY not in x[0] for x in seen)

@pytest.mark.parametrize("key",[None,"wrong","synthetic-upstream-key"])
def test_answer_rejected_before_tmdb(monkeypatch,key):
    def must_not_call(*args,**kwargs): raise AssertionError("Unauthenticated request reached TMDB")
    monkeypatch.setattr(main.httpx,"get",must_not_call)
    r=client.get("/movie/answer",headers={} if key is None else {"X-API-Key":key})
    assert r.status_code==401

@pytest.mark.parametrize("upstream,status",[(401,502),(403,502),(404,502),(429,503),(500,502)])
def test_upstream_errors(monkeypatch,upstream,status):
    monkeypatch.setattr(main.httpx,"get",lambda *a,**k:mock_response(upstream))
    r=client.get("/movie/clue"); assert r.status_code==status
    assert main.TMDB_KEY not in r.text and "api_key" not in r.text

@pytest.mark.parametrize("error,status",[(httpx.ReadTimeout("synthetic secret URL"),504),(httpx.ConnectError("synthetic secret URL"),502)])
def test_network_errors(monkeypatch,error,status):
    def fail(*a,**k):raise error
    monkeypatch.setattr(main.httpx,"get",fail)
    r=client.get("/movie/clue");assert r.status_code==status
    assert "synthetic secret URL" not in r.text

@pytest.mark.parametrize("data",[{},[],{**MOVIE,"title":None},{**MOVIE,"runtime":"long"},{**MOVIE,"release_date":""}])
def test_malformed(monkeypatch,data):
    monkeypatch.setattr(main.httpx,"get",lambda *a,**k:mock_response(data=data))
    assert client.get("/movie/clue").status_code==502
