import os
os.environ['TMDB_API_KEY'] = 'synthetic-test-provider'
os.environ['GAME_API_KEY'] = 'guess-test-only-' + 'g' * 40
import pytest
from fastapi.testclient import TestClient
import extension

client = TestClient(extension.app)

@pytest.mark.parametrize('title,correct', [
    ('The Hidden Signal', True), ('  THE HIDDEN SIGNAL  ', True), ('A Different Film', False),
])
def test_guess_returns_only_correctness(monkeypatch, title, correct):
    monkeypatch.setattr(extension, 'get_movie', lambda: {'title': 'The Hidden Signal'})
    response = client.post('/movie/guess', json={'title': title})
    assert response.status_code == 200
    assert response.json() == {'correct': correct}

@pytest.mark.parametrize('body', [{}, {'title':''}, {'title':'x'*201}, {'title':123}])
def test_invalid_guess_stops_before_provider(monkeypatch, body):
    def must_not_call():
        raise AssertionError('Invalid request reached provider')
    monkeypatch.setattr(extension, 'get_movie', must_not_call)
    assert client.post('/movie/guess', json=body).status_code == 422
