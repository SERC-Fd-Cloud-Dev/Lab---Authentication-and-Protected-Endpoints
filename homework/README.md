# Homework - Movie Guessing Game with TMDB

Build a small game API from blank application files. Obtain real movie details from TMDB, expose selected clues, and restrict the answer with a separate incoming API key. No CRUD or database is needed.

**Time:** approximately 60 minutes core, **after** obtaining a TMDB account/key; optional challenge 15 minutes extra. Account approval and installation time are not included.
**Prerequisites:** the root README environment, API-key verification, FastAPI routes, JSON dictionaries and HTTPX requests. Exercise 1 contains the complete authentication walkthrough if you need a recap.

## Endpoint and data contracts

These are **your FastAPI endpoints**. The game uses one fixed server-side movie ID. Shape notation describes JSON keys/types, not Python code. Public means that your API does not require an incoming credential; its outgoing TMDB request still needs its own key.

| Method and endpoint | Request data / credential | Successful response data shape | Protected? | Expected statuses |
|---|---|---|---|---|
| `GET /movie/clue` | No body or credential | `{year: integer, genres: string[], runtime: integer or null}` | **No — public clues** | 200; 502 upstream failure; 503 upstream rate limit; 504 timeout |
| `GET /movie/answer` | No body; `X-API-Key: <game key>` | `{title: string}` | **Yes — valid GAME_API_KEY** | 200; 401 missing/wrong game key; 502/503/504 upstream failure |
| `POST /movie/guess` | JSON body: `{title: string}` (1–200 characters) | `{correct: boolean}` | **No — public guessing** | 200 for right or wrong guess; 422 invalid body; 502/503/504 upstream failure |

Authentication/integration errors use `{detail: string}`. FastAPI body-validation errors use `{detail: array}`. A rejected answer request must make **zero TMDB calls**. The clue never returns a title, movie ID, overview or raw TMDB object.

This is the **outgoing provider request**, not another route to build:

| Method and provider endpoint | Request data / credential | Relevant provider response shape | Protection |
|---|---|---|---|
| `GET https://api.themoviedb.org/3/movie/{movie_id}` | Path: configured positive integer; query: `api_key=<TMDB_API_KEY>`, `language=en-GB`; no body | `{title: string, release_date: string, genres: [{id: integer, name: string}], runtime: integer or null, ...}` | **TMDB validates the outgoing TMDB key** |

Your helper transforms this to `{title: string, year: integer, genres: string[], runtime: integer or null}`. Each game endpoint selects only its permitted fields. Provider response values vary; use the supplied synthetic fixture for deterministic tests.

## Before you start

1. Sign in to TMDB, open account settings → API, and follow the current [API application instructions](https://developer.themoviedb.org/docs/authentication-application). Use the **v3 API key**, not the much longer API Read Access Token. Do this before the homework session.
2. Read the [API usage and attribution requirements](https://developer.themoviedb.org/docs/faq). Keep your application within the approved usage terms. If you cannot obtain access, ask the lecturer; do not borrow someone else's key.
3. `movie_ids.json` provides a small choice of IDs. Use a **single fixed movie** for both clues and answer; do not choose randomly on every request. Otherwise the answer might not match the clue.
4. `fixtures/movie.json` is synthetic test data. It supports offline unit tests but is not a replacement for the core live authenticated request.

## Part 1 - Guided Walkthrough (20 minutes)

### Create and configure the project

At repository root, create `work/movie-game/`, then `main.py`, `.env` and `.env.example` in that folder. Copy the **names only** from this homework's `.env.example` into yours. In your local `.env`, enter the TMDB key, a newly generated random game key of at least 32 characters, and a selected movie ID:

```dotenv
TMDB_API_KEY=your-private-v3-key
GAME_API_KEY=your-new-random-local-key
MOVIE_ID=603
```

These are instructions for local values, not usable sample credentials. Keep the committed `.env.example` blank. Generate the game key with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

| Credential | Direction | Who checks it? |
|---|---|---|
| `GAME_API_KEY` | Player/test client → your API, in `X-API-Key` | Your dependency |
| `TMDB_API_KEY` | Your server → TMDB, using its v3 `api_key` parameter | TMDB |

A player must never receive the TMDB credential. The outgoing query parameter is a provider-supported compatibility choice for this exercise; HTTPX `params` encodes it but **does not hide it from URL logs**. Use HTTPS, never print the full request URL or exception, and keep logs free of credentials. Your own API uses a header.

### Retrieve a movie safely

Start `main.py` with these imports/configuration and the helper below:

```python
from pathlib import Path
import os
import secrets
import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

load_dotenv(Path(__file__).with_name(".env"))
TMDB_KEY = os.environ.get("TMDB_API_KEY", "")
GAME_KEY = os.environ.get("GAME_API_KEY", "")
MOVIE_ID = int(os.environ.get("MOVIE_ID", "603"))
if not TMDB_KEY or len(GAME_KEY) < 32 or MOVIE_ID <= 0:
    raise RuntimeError("Configure TMDB_API_KEY, a random GAME_API_KEY and a positive MOVIE_ID")

app = FastAPI(title="Movie guessing game")
def get_movie():
    try:
        response = httpx.get(
            f"https://api.themoviedb.org/3/movie/{MOVIE_ID}",
            params={"api_key": TMDB_KEY, "language": "en-GB"}, timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()
        # Validate only the small subset used by this lesson.
        title = data["title"]
        date = data["release_date"]
        genres = [g["name"] for g in data["genres"]]
        runtime = data["runtime"]
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Missing title")
        if not isinstance(date, str) or len(date) < 4 or not date[:4].isdigit():
            raise ValueError("Missing release year")
        if not all(isinstance(g, str) for g in genres):
            raise ValueError("Invalid genres")
        if runtime is not None and (type(runtime) is not int or runtime < 0):
            raise ValueError("Invalid runtime")
        return {"title": title, "year": int(date[:4]), "genres": genres, "runtime": runtime}
    except httpx.TimeoutException:
        raise HTTPException(504, "Movie service timed out") from None
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 429:
            raise HTTPException(503, "Movie service temporarily unavailable") from None
        raise HTTPException(502, "Movie service request failed") from None
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise HTTPException(502, "Movie service unavailable or invalid response") from None
```

**What to notice:** the URL contains a server-chosen ID; the key comes from configuration. A five-second timeout prevents an unbounded wait. `raise_for_status` separates successful responses from upstream errors. We read only the required fields. Exceptions become generic API errors without including the URL, credential or TMDB body. The small error policy is supplied to keep this homework focused; retries and caching come later.

Create a temporary local check in a second file, `check_tmdb.py`:

```python
from main import get_movie
movie = get_movie()
print({"year": movie["year"], "genres": movie["genres"], "runtime": movie["runtime"]})
```

Run `python check_tmdb.py` from `work/movie-game`. Expect a dictionary of real year, genre names and runtime (which may be null). The output must contain no key or title. If you get a generic upstream error, check the API-key type, selected ID and network connection locally; do not paste credentials into a help request.

**Why does this work?** Name the component that checks each of the two keys. Why would sending `GAME_API_KEY` to TMDB fail?

## Part 2 - Guided Application (10 minutes)

Add `GET /movie/clue`. Use `get_movie()` and return **only** `year`, `genres` and `runtime`. Do not return the complete upstream dictionary, title, original title, overview, poster path or movie ID. Those could reveal or make it trivial to look up the answer.

Start the server with `python -m uvicorn main:app --reload`. Call `/movie/clue` without authentication. Expect **200**, useful clues and no title. The game intentionally relies on the same configured movie for its clue and answer.

## Part 3 - Supported Practice (10 minutes)

Plan the incoming protection. Milestones: extract `X-API-Key`; validate it against `GAME_API_KEY`; return the same generic **401** for missing/wrong keys; attach the dependency to the answer route only. Use the pattern you built in Exercise 1. Do not compare against `TMDB_API_KEY`.

<details><summary>Hint 1: attach protection</summary>

A route's `dependencies=[Depends(...)]` runs a check before calling the route. You can also request a dependency parameter when the endpoint needs its returned value.
</details>
<details><summary>Hint 2: avoid unnecessary upstream calls</summary>

The answer route must check the incoming key before calling `get_movie()`. Rejected incoming requests should make zero TMDB calls.
</details>

## Part 4 - Independent Task (20 minutes)

Implement `GET /movie/answer` returning the title for the same configured movie, protected with your game key. Write tests using the worked fixture pattern below, then extend them to the acceptance cases. Complete the attribution step.

### Worked test pattern

Create `test_game.py` beside your application. Use a synthetic key in tests and patch HTTPX rather than making a live TMDB call on every test:

```python
import os
os.environ["TMDB_API_KEY"] = "synthetic-test-key"
os.environ["GAME_API_KEY"] = "test-only-" + "g" * 40
import httpx
from fastapi.testclient import TestClient
import main
client = TestClient(main.app)

def test_clue(monkeypatch):
    def fake_get(url, **kwargs):
        return httpx.Response(200, json={"title":"The Hidden Signal",
            "release_date":"2020-02-03", "genres":[{"name":"Mystery"}], "runtime":101},
            request=httpx.Request("GET", url))
    monkeypatch.setattr(main.httpx, "get", fake_get)
    response = client.get("/movie/clue")
    assert response.status_code == 200
    assert "The Hidden Signal" not in response.text
```

Run `python -m pytest -q` and extend this pattern. You may instead load the supplied synthetic JSON fixture. Use `httpx.Response(401, ...)` to model bad upstream authentication, and raise `httpx.ReadTimeout` to model a timeout.

| Acceptance case | Expected behaviour |
|---|---|
| Clue, no key | 200; only year, genres, runtime |
| Answer, correct game key | 200; title |
| Answer, missing/wrong key | 401; no title; no TMDB call |
| Answer, TMDB key used as game key | 401 |
| TMDB rejects its credential | 502 generic upstream failure, not a player 401 |
| TMDB times out | 504 generic timeout |
| Responses, tracked files and evidence | No credentials or complete request URLs |

Keep a redacted record of **one live TMDB success** in addition to mocked tests. If account/network access is unavailable, complete the mock checks and label the live check incomplete for the review session; do not claim it passed.

### Credits and attribution

Create an application `CREDITS.md`. Include the exact notice **“This product uses the TMDB API but is not endorsed or certified by TMDB.”** and a link to TMDB. Obtain an approved TMDB logo from the official [logos and attribution page](https://www.themoviedb.org/about/logos-attribution), place it in your application assets, and display it in Credits according to the [FAQ](https://developer.themoviedb.org/docs/faq). Keep the TMDB logo less prominent than your own application identity. If you later add a web UI, link Credits from it. A text notice alone does not meet the stated logo requirement.

## Challenge Exercise

Add `POST /movie/guess` accepting a validated title string (1–200 characters) and returning only `{"correct": true}` or `{"correct": false}`. Compare after trimming whitespace and case-folding. Never return the correct answer on a wrong guess. Test case/whitespace handling and empty input. This is a small game action, not a CRUD resource. Explain why a public guessing endpoint would need abuse controls in a deployed game. Allow 15 extra minutes.

## Troubleshooting and completion

- 401 from **your answer endpoint**: inspect the incoming game header. 502 after a TMDB request: inspect the outgoing key type and movie ID privately.
- A title in the clue response: return an explicit safe field list, never the whole TMDB response.
- Clue and answer disagree: use one fixed server-side movie ID.
- Syntax/import errors: run from the application folder in the environment from the root README.
- Review evidence: source, passing mock tests, redacted live-check result, Credits and a two-sentence explanation of the two credentials. Bring this to the one-hour homework review.

Core completion includes the independent answer endpoint and live TMDB check. The guessing challenge is optional. Stop the local server/Codespace when finished.
