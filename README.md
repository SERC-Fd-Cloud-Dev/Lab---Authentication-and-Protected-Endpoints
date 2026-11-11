# Lab - Authentication and Protected Endpoints

Build small FastAPI applications from blank files. First verify API keys and JWTs; then use a database to decide what an authenticated user may read. There is no CRUD API to build. Every exercise moves from an explained walkthrough to a mandatory independent task. Challenges are optional.

**Time**: 45 min API keys, 30 min JWTs, 55 min authorisation, plus 60 min homework. Tutor explanation, discussion and breaks sit outside these practical estimates. Challenges take additional time.
**Prerequisites**: Python functions, imports and virtual environments; FastAPI routes and dependencies; HTTP headers/status codes; basic SQLAlchemy sessions and pytest.

[skip to exercises](#exercises)

---

### Learning Objectives
- Verify credentials before allowing access to a protected endpoint.
- Resolve a verified identity to a database user and enforce role/ownership rules.
- Test accepted and rejected requests without exposing secrets.
- Use separate credentials for incoming game requests and outgoing TMDB requests.

---

## Getting Started

<details>
<summary>Option if starting from the template repo</summary>

If your lecturer supplies a GitHub template, select **Use this template → Create a new repository** and create your own repository as instructed. Use the default branch. Do not fork or copy the staff solutions. If you received these files directly, put the contents of this `lab` folder in your own repository before using Codespaces. The repository contains instructions and environment support, but no completed application files.

</details>

### Option 1: GitHub Codespace (Recommended)
1. Open your lab repository on GitHub.
2. Click Code → Codespaces → Create codespace on main.
3. Wait for the environment to start and the dependency installation to finish.
4. Verify you are at the repository root: `pwd` and `ls` should show this README and `requirements.txt`.
5. Run `source .venv/bin/activate`. If creation failed, use the environment commands below.
6. Follow the exercise instructions in this README. Keep port 8000 **private**. Open the forwarded port from the Ports panel and add `/docs` to its address.

Codespaces requires account access and available quota. Stop the Codespace when finished; use local setup if it is unavailable. The devcontainer is supplied, but launch must be checked in your institutional GitHub environment.

### Option 2: Local Setup (Clone)
<details>
<summary>Before starting, ensure you have the required tools installed.</summary>

- Runtime: Python 3.12 (tested version family).
- Database: SQLite, included with standard Python; no database server.
- Other tools: Git, VS Code, a terminal and a browser. Postman is optional.
- Environment variables: each application uses its own `.env`; names are documented in each exercise. No real values belong in `.env.example`.

</details>

1. Clone your student repository using its URL from GitHub's Code menu (`git clone` followed by that URL).
2. Confirm you are at the repository root.
3. Open the folder in VS Code.
4. Create and activate an environment:

```bash
python -m venv .venv
# Linux, macOS or Codespaces:
source .venv/bin/activate
# Windows PowerShell, instead of the line above:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -c "import fastapi, jwt, sqlalchemy, httpx; print('Dependencies ready')"
```

If PowerShell activation is restricted, use `.venv\Scripts\python.exe` wherever instructions say `python`; you do not need to change execution policy. On systems that use `python3`, substitute it when creating the environment. All later commands use the activated environment.

5. Follow the exercise instructions. Use `http://127.0.0.1:8000/docs` locally.

**Prerequisite refresher:** a route decorator connects an HTTP path to a Python function. `Depends` runs another function before the route. Raising `HTTPException` ends that request. A pytest test calls the API through `TestClient` and asserts an expected result. In SQLAlchemy, a `Session` performs database work; `session.get(User, id)` retrieves a primary-key record.

---

## Exercises

1. [Exercise 1](exercise-1.md): Header API keys, protected routes and secrets.
2. [Exercise 2](exercise-2.md): Signed JWT verification and protected identity endpoints.
3. [Exercise 3](exercise-3.md): Database users, roles, ownership and automated access tests.

★ [Homework](homework/README.md): Movie Guessing Game using TMDB.

Complete the core stages in order. A student who missed class can follow these same instructions; no tutor demonstration is a hidden prerequisite.

---

## General Tips
- **One server**: stop Uvicorn with Ctrl+C before starting another exercise on port 8000.
- **One working folder**: run each application from the folder containing its `main.py`; return to the repository root before the next exercise.
- **Secrets**: keep `.env` local, use random lab-only credentials, and never paste keys/tokens into issues, AI prompts, screenshots or logs.
- **Checks**: first predict the response, then run it. Record status and a redacted result, not credentials.
- **Endpoint tables**: use each exercise's contract to check method, path, request/response shape, protected/public status and error cases. Keep your independent response choices documented beside your tests.
- **Catch-up**: complete guided stages, then the independent core tasks. Defer challenges. Record the first failing checkpoint and its non-sensitive error if you need help.
- **Reset safely**: keep your previous work. Make a new practice directory and repeat the relevant walkthrough; do not delete your repository.

---

## Submitting Your Work

This is formative practice. Commit your source, tests and blank `.env.example` files to your own lab repository. Before committing, run `git status --short` and `git diff --cached` and check that no secret, token, database or private evidence is staged. Bring your test results, access matrix and a short explanation of one access decision to the homework review. Follow any separate hand-in instructions given by your lecturer; this README does not create a Moodle submission requirement.

---

> **AI use notice**: Attempt each task and use the hints before seeking automated help. If AI assistance is permitted by your lecturer for this formative lab, ask for explanations or debugging clues, verify its advice and record what helped. Do not upload secrets or request a completed independent task. This notice does not change the separate assessed-work rules.

Spot any issues? Please [submit an issue](https://github.com/SERC-Fd-Cloud-Dev/Lab---Authentication-and-Protected-Endpoints/issues) or [pull request](https://github.com/SERC-Fd-Cloud-Dev/Lab---Authentication-and-Protected-Endpoints/pulls).
