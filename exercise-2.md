# Exercise 2 - JWT Authentication

## Overview

A signed token can carry a subject identifier and an expiry. You will verify those claims before using them. JWT is a **format**; bearer describes how a credential is used. A signed JWT payload can normally be decoded by its holder: signing protects integrity, not confidentiality.

**Time:** 30 minutes core; challenge 10 minutes extra.
**Learning objectives:** verify signature, expiry, issuer and audience; use a verified subject; reject altered or incomplete tokens.

## Endpoint contract

All requests below use **no body**. Send credentials in `Authorization: Bearer <token>`. A valid token has a verified signature and the required valid `sub`, `exp`, `iss` and `aud` claims. In Swagger's Authorize box, enter only the token.

| Method and endpoint | Request data / credential | Successful response data shape | Protected? | Expected statuses |
|---|---|---|---|---|
| `GET /public` | None | `{message: string}` | **No** | 200 |
| `GET /me` | Bearer token | `{subject: string}` | **Yes — valid JWT** | 200; 401 missing/invalid token |
| `GET /token-info` | Bearer token | `{issuer: string, audience: string}` | **Yes — valid JWT** | 200; 401 missing/invalid token |
| `GET /badge` | Bearer token | Verified subject plus a message, e.g. `{subject: string, badge: string}`; choose and document your field names | **Yes — valid JWT** | 200; 401 missing, expired, incomplete or wrongly signed token |
| `GET /preview` | Bearer token with `scope` containing the exact space-delimited value `read:preview` | `{preview: string}` | **Yes — valid JWT and required scope** | 200; 401 missing/invalid token; 403 valid token without required scope |

Error responses use `{detail: string}`. No response contains the raw token or signing secret. The local issuer is a command-line fixture, **not an API endpoint**. There is no login or CRUD route to implement.

## Before You Start

Complete the root README environment setup. Use a terminal in the repository root and ensure the virtual environment is active. Create the named folder in VS Code. All application files start empty; type or copy only the explained snippets below. Save each file before running it.

The examples use local HTTP only for a private development server. Real remote credentials require HTTPS. Never publish these teaching applications as production identity services.
## Part 1 - Guided Walkthrough (15 minutes)

Create `work/jwt-api/`. This is a new application with no database or CRUD. Change into that directory. Create `.env` with `JWT_SECRET=` followed by a newly generated `secrets.token_urlsafe(32)` value, and a blank `.env.example`. Use a different secret from Exercise 1.

Create `auth.py`:

```python
from pathlib import Path
import os
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
JWT_SECRET = os.environ.get("JWT_SECRET", "")
if len(JWT_SECRET) < 32:
    raise RuntimeError("Set JWT_SECRET to a random value of at least 32 characters")
ISSUER = "cloud-lab"
AUDIENCE = "training-api"
bearer = HTTPBearer(auto_error=False)

def verified_claims(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    error = HTTPException(401, "Invalid or missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    if credentials is None:
        raise error
    try:
        claims = jwt.decode(
            credentials.credentials, JWT_SECRET,
            algorithms=["HS256"], issuer=ISSUER, audience=AUDIENCE,
            options={"require": ["sub", "exp", "iss", "aud"]},
        )
        if not isinstance(claims["sub"], str) or not claims["sub"].strip():
            raise error
        return claims
    except jwt.InvalidTokenError:
        raise error
```

**Read the code:** `HTTPBearer` reads the Authorization header. `jwt.decode` verifies the signature with a server-chosen algorithm. We require four claims so that an absent expiry cannot silently be accepted. `issuer` and `audience` constrain who issued the token and which API should accept it. `sub` must identify a subject. All invalid credentials produce a generic **401** with a Bearer challenge; the response does not disclose validation internals. Do not use an unverified payload to decide access.

Create `main.py`:

```python
from fastapi import Depends, FastAPI
from auth import verified_claims

app = FastAPI(title="JWT verification lab")

@app.get("/public")
def public():
    return {"message": "Public information"}

@app.get("/me")
def me(claims: dict = Depends(verified_claims)):
    return {"subject": claims["sub"]}
```

The dependency supplies a verified dictionary. `/me` returns only its subject, not the token. Here `u1` is a synthetic identifier; the next exercise will resolve it to a database user.

Create `issue_demo_token.py` with the snippet below. This is a local **test-fixture utility**, not a login system. It can mint any supplied subject because the exercise operator controls the signing secret. Never expose this script as a web endpoint or give a production signing key to clients.

```python
"""LOCAL TEACHING FIXTURE ONLY: creates test tokens, never a web login endpoint."""
import argparse
from datetime import datetime, timedelta, timezone
import jwt
from auth import JWT_SECRET, ISSUER, AUDIENCE

parser = argparse.ArgumentParser()
parser.add_argument("--subject", default="u1")
parser.add_argument("--expired", action="store_true")
parser.add_argument("--scope", default="")
args = parser.parse_args()
now = datetime.now(timezone.utc)
claims = {"sub": args.subject, "iss": ISSUER, "aud": AUDIENCE,
          "iat": now, "exp": now + timedelta(minutes=-1 if args.expired else 30)}
if args.scope:
    claims["scope"] = args.scope
print(jwt.encode(claims, JWT_SECRET, algorithm="HS256"))
```

Run `python issue_demo_token.py`, copy the newly printed practice token, then run `python -m uvicorn main:app --reload`. In Swagger UI's Bearer Authorize box paste the token **without adding the word Bearer**. The UI adds it. `/me` should return **200** and `{"subject":"u1"}`. A raw HTTP client instead sends `Authorization: Bearer TOKEN`.

**Checkpoint:** clear Authorize and request `/me`: **401**. Generate an expired token using `python issue_demo_token.py --expired` in a second terminal, authorise with it and request again: **401**. Regenerate a valid token if 30 minutes have passed.

**Why does this work?** Which values come from the server, and which arrive inside the untrusted token? Why must the allowed algorithm come from the server?

## Part 2 - Guided Application (5 minutes)

Add `GET /token-info`. Use `Depends(verified_claims)` exactly as `/me` does, and return only `iss` and `aud` under readable field names. Do not expose the raw token. Check a valid token returns `cloud-lab` and `training-api`; an expired token must not reach the route.

## Part 3 - Supported Practice (5 minutes)

Create `test_security.py`. This example creates a fresh valid fixture at test time:

```python
import os
os.environ["JWT_SECRET"] = "test-only-" + "j" * 40
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.testclient import TestClient
from auth import JWT_SECRET, ISSUER, AUDIENCE
from main import app
client = TestClient(app)

def make_token():
    return jwt.encode({"sub":"u1", "iss":ISSUER, "aud":AUDIENCE,
        "exp":datetime.now(timezone.utc)+timedelta(minutes=5)},
        JWT_SECRET, algorithm="HS256")

def test_me():
    response = client.get("/me", headers={"Authorization":"Bearer " + make_token()})
    assert response.status_code == 200
    assert response.json()["subject"] == "u1"
```

Run `python -m pytest -q`. Extend your tests to cover a missing header and an expired token.

<details><summary>Hint 1: expiry</summary>

Build a second test token with `exp=0`. It represents a time long in the past. Keep signature verification enabled.
</details>
<details><summary>Hint 2: altering a payload</summary>

Signing a token using a different secret creates a syntactically valid JWT whose signature this API rejects. Do not merely modify the last Base64 character, which can have encoding edge cases.
</details>

## Part 4 - Independent Task (5 minutes)

Implement `GET /badge`: a valid token returns the verified subject and a short learner badge message. It must reject missing credentials, expired tokens and tokens signed with a different secret. Write automated tests; choose your own response format. Check that a token with `exp` omitted is rejected too. Explain the difference between decoding a payload and trusting it.

## Challenge Exercise

Add `GET /preview` requiring the additional verified scope `read:preview`. Use `python issue_demo_token.py --scope read:preview` to mint a test token. Valid token with correct scope: **200**; valid token without it: **403**; invalid token: **401**. A scope such as `read:preview-all` must not match. Allow 10 extra minutes.

## Troubleshooting

| Symptom | Recovery |
|---|---|
| All tokens get 401 | Same `.env` for issuer and API; check ISSUER/AUDIENCE; regenerate after changing signing secret |
| Token expires during class | Mint another; do not remove expiry verification |
| Import `jwt` behaves unexpectedly | Install **PyJWT** from the supplied requirements; do not install the different `jwt` package |
| Missing Bearer credentials | Swagger wants the token alone; raw headers need `Bearer ` before it |
| Startup cannot find secret | Check file location and restart; never add a default secret to code |

## Completion Checklist

- [ ] `/badge` uses only verified claims and has positive/negative tests.
- [ ] I can name the four required claims and the trust check for each.
- [ ] I can explain why the local issuer is only a fixture, and why users must not have a real signing key.

Return to the repository root. Continue to Exercise 3. If catching up, complete `/me` verification before starting database authorisation; database roles cannot repair invalid identity verification.
