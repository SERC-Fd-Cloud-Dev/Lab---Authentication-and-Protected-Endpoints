# Exercise 3 - Database-backed Authorisation

## Overview

Knowing who made a request is only the first decision. In a fictional training centre, Alice and Ben may read their own profile; Carol is a lecturer and may read other profiles. Use **users** to learn roles and ownership. A service account is also a principal, but it belongs to software; you will consider it in the challenge.

**Time:** 55 minutes core; challenge 15 minutes extra.
**Learning objectives:** resolve verified subjects to users; enforce current database permissions; prevent cross-user access; test an access matrix.

## Endpoint and data contracts

All requests use **no body**. Protected endpoints first verify `Authorization: Bearer <token>`, resolve its `sub` to a database user, and check the current account status. A role sent by the client never replaces the database role.

| Method and endpoint | Request data / credential | Successful response data shape | Protected? / access rule | Expected statuses |
|---|---|---|---|---|
| `GET /public` | None | `{message: string}` | **No** | 200 |
| `GET /me` | Bearer token | `{id: string, username: string, role: string}` | **Yes — known, active user** | 200; 401 missing/invalid token or unknown subject; 403 inactive account |
| `GET /staff` | Bearer token | `{message: string}` | **Yes — active lecturer** | 200; 401 as above; 403 inactive account or other role |
| `GET /profiles/{user_id}` | Path: `user_id` string, e.g. `u1`; Bearer token | `{id: string, username: string}` | **Yes — active owner OR lecturer** | 200; 401 as above; 403 inactive/forbidden; 404 target absent after permission succeeds |
|  `GET /reports/summary` | Bearer token | `{active_accounts: integer}` | **Yes — active reporter OR lecturer** | 200; 401 as above; 403 inactive account or other role |

Errors use `{detail: string}`. Check permission before looking up the requested profile: a student requesting another ID receives 403 whether or not that target exists. The profile response intentionally omits role and active status.

The local SQLite table has this shape. It is created and seeded locally; there are no user-management endpoints.

| Stored field | Type / constraint | Purpose |
|---|---|---|
| `id` | String, primary key | Stable subject identifier, e.g. `u1` |
| `username` | String, unique | Display/account name, e.g. `alice` |
| `role` | String | `student` or `lecturer`; `reporter` only in the challenge |
| `is_active` | Boolean | Current account permission to use protected routes |

## Before You Start

Complete the root README environment setup. Use a terminal in the repository root and ensure the virtual environment is active. Create the named folder in VS Code. All application files start empty; type or copy only the explained snippets below. Save each file before running it.

The examples use local HTTP only for a private development server. Real remote credentials require HTTPS. Never publish these teaching applications as production identity services.
## Part 1 - Guided Walkthrough (20 minutes)

Create `work/authorisation-api/`. Copy **your own** `auth.py` and `issue_demo_token.py` from Exercise 2 into it, plus your local `.env`. This reuses verification you built yourself. Create the remaining files empty. If you missed Exercise 2, its walkthrough contains all required code and checks; complete that first. The exercise never depends on staff solutions.

The trust sequence is: validate token → use verified `sub` → find the database user → check account/permissions → serve the allowed representation. A request body, query parameter, `X-Role` header or unverified JWT must never set the user's authority.

Create `database.py`:

```python
from pathlib import Path
import os
from sqlalchemy import Boolean, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    role: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

DB_PATH = Path(os.environ.get("LAB_DB_PATH", str(Path(__file__).with_name("users.db"))))
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

def get_db():
    with Session(engine) as session:
        yield session
```

This reuses SQLAlchemy from Week 6. `User` maps a small table; `id` is the stable identifier stored in `sub`. The role and active status live in the database. Each dependency invocation gets a session and closes it after the request. `check_same_thread=False` permits FastAPI's worker-thread use of SQLite; it does not disable authorisation. The file path is beside this module unless tests select another path.

Create `seed.py`:

```python
"""Creates synthetic teaching records if absent; does not reset existing work."""
from sqlalchemy.orm import Session
from database import Base, User, engine

Base.metadata.create_all(engine)
with Session(engine) as session:
    for ident, name, role, active in [
        ("u1", "alice", "student", True),
        ("u2", "ben", "student", True),
        ("u3", "carol", "lecturer", True),
        ("u4", "dana", "student", False),
    ]:
        if session.get(User, ident) is None:
            session.add(User(id=ident, username=name, role=role, is_active=active))
    session.commit()
print("Teaching users are ready")
```

Run `python seed.py` from this application folder. Expect **Teaching users are ready**. Running it again preserves existing rows. It creates local teaching data, not public user-management routes. We use table creation for this disposable lab; a changing production schema needs the migration practice taught previously.

Create `main.py`:

```python
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from auth import verified_claims
from database import User, get_db

app = FastAPI(title="Training centre access control")

def current_user(claims: dict = Depends(verified_claims), db: Session = Depends(get_db)):
    user = db.get(User, claims["sub"])
    if user is None:
        raise HTTPException(401, "Unknown identity", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(403, "Account inactive")
    return user

def lecturer(user: User = Depends(current_user)):
    if user.role != "lecturer":
        raise HTTPException(403, "Lecturer access required")
    return user

@app.get("/public")
def public():
    return {"message": "Training centre"}

@app.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}

@app.get("/staff", dependencies=[Depends(lecturer)])
def staff():
    return {"message": "Staff briefing"}
```

`current_user` binds the verified token to a real record. Unknown identity returns **401**; an authenticated inactive account is denied with **403**, the policy chosen for this lab. `lecturer` builds on that dependency. Client claims about roles are ignored; the current database role is authoritative.

Mint `u1` and `u3` tokens with `python issue_demo_token.py --subject u1` and `--subject u3`. Start the API. Expect `/me` with u1 → **200**; `/staff` with u1 → **403**; `/staff` with u3 → **200**. Missing token → **401**. `/public` needs no token.

**Why does this work?** Trace the functions that run before `/staff`. Explain why a valid signature alone cannot make u1 a lecturer.

## Part 2 - Guided Application (8 minutes)

Mint a u4 token and try `/me`. Expect **403** because Dana is inactive. Mint a token for an unknown subject; expect **401**. Record the distinction. Add a small automated test for the staff role rule using the token fixture pattern in Exercise 2.

Use a separate test database: before importing `database` or `main`, set `os.environ["LAB_DB_PATH"]` to a path in pytest's temporary directory. One simple module-level approach is `tempfile.TemporaryDirectory()` and `Path(temp.name) / "users.db"`; retain the temporary-directory object for the life of the test module. Import `seed` after selecting the path. Never run a test that alters your personal teaching database.

## Part 3 - Supported Practice (12 minutes)

Complete this access matrix **before coding**. Use it as your test plan.

| Request | No token | u1 Alice | u2 Ben | u3 Carol |
|---|---|---|---|---|
| `/me` | ? | ? | ? | ? |
| `/staff` | ? | ? | ? | ? |
| `/profiles/u1` | ? | ? | ? | ? |
| `/profiles/u2` | ? | ? | ? | ? |

For profile access, derive a boolean rule from: **the authenticated user owns the requested profile OR is a lecturer**. In pseudocode, reject when neither condition is true. Distinguish the requesting user from the target user.

<details><summary>Hint 1: the two identifiers</summary>

The requesting identity is `current_user.id`; the target is the URL's `user_id`. The target is a request to be authorised, not proof of identity.
</details>
<details><summary>Hint 2: combining rules</summary>

An owner who is not a lecturer must still pass. A lecturer who is not the owner must also pass. Reject only when both permission reasons are absent.
</details>
<details><summary>Check the first two matrix rows</summary>

`/me`: 401, 200, 200, 200. `/staff`: 401, 403, 403, 200. Use the policy to derive the profile rows yourself, then verify them against the acceptance cases below.
</details>

## Part 4 - Independent Task (15 minutes)

Implement `GET /profiles/{user_id}` without adding create, update or delete endpoints. Return only `id` and `username`. Requirements:

- An active user may read their own profile; an active lecturer may read any existing profile.
- Missing/invalid token → **401**; valid student trying another user's profile → **403**.
- An authorised lecturer requesting a nonexistent profile → **404**.
- Check permissions **before** looking up the target; a student probing another or nonexistent ID should get the same **403** response.
- `?role=lecturer`, `X-Role: lecturer` and an extra JWT `role` claim must not override the database.

Write tests proving u1→u1 **200**, u1→u2 **403**, u2→u1 **403**, u2→u2 **200**, u3→u1 **200**, and no-token→u1 **401**. Include the unknown-profile case above. These are requirements, not solution code.

**Transfer check:** after a database role change, should a previously issued token still grant its old permissions? Explain what your implementation reads on the next request. Use a test database to demonstrate.

## Challenge Exercise

Add a synthetic service account `u5` with role `reporter` using a local setup script. Add `GET /reports/summary`, allowed to reporters and lecturers, returning only a count of active accounts. A reporter may read its own `/me` but must not read Alice's profile or `/staff`. Demonstrate least privilege with tests. A real service would obtain a credential through an approved machine-to-machine process; the local issuer remains a classroom fixture. Allow 15 extra minutes.

## Troubleshooting

| Symptom | Check |
|---|---|
| `no such table: users` | Run `python seed.py` in this folder; check LAB_DB_PATH |
| Valid token gives 401 | `sub` must match a seeded ID such as u1, not the display name alice |
| Own-profile request gives 403 | Review boolean logic and compare string IDs consistently |
| Every profile is readable | Check the rule uses the authenticated user's ID and role, not the target's role |
| Re-running seed does not undo changes | Intended non-destructive behaviour; create a new test database for a clean check |

## Completion Checklist

- [ ] I completed and verified the access matrix.
- [ ] A second ordinary user cannot read the first user's private profile.
- [ ] Tests cover 401, 403 and successful requests using an isolated database.
- [ ] The client cannot promote itself to lecturer.
- [ ] I can explain one limitation: the demo issuer and shared signing secret are not production identity infrastructure.
