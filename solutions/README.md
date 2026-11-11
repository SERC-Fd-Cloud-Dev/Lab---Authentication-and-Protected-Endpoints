# Lecturer solutions — keep private

This directory contains complete **core** solutions and separate optional **challenge** extensions for all four exercises. It must not be included in a student template, any student-accessible branch/history, or the Jekyll site.

## Run a core solution

Activate the environment installed from `lab/requirements.txt`. Change into one numbered solution's `core/` directory. Copy `.env.example` to `.env` and enter random local practice values; the movie solution also requires your own TMDB v3 key. Run `python seed.py` for the authorisation solution. Start `python -m uvicorn main:app --reload` and open `/docs`. Mint JWT fixtures using `python issue_demo_token.py --subject u1` (u3 is the lecturer).

Run `python -m pytest -q` **separately in each core directory**. Tests configure synthetic secrets and an isolated database. Movie tests mock HTTPX and do not require network/key access; they do not prove a live TMDB connection. Never run all four test folders in one process because the teaching applications deliberately share short module names such as `main` and `auth`.

## Optional challenges

Stop the core server. From its `core/` directory run `python -m uvicorn extension:app --app-dir ../challenge --reload`. This adds the extension to the core application. The key challenge requires LAB_API_KEY_NEXT in `.env`. The authorisation challenge also needs u5: from `core/`, run `python -c "import runpy; runpy.run_path('../challenge/add_reporter.py')"`. Mint u5 with the local fixture issuer. The game challenge adds POST `/movie/guess`.

**Core decisions:** explicit 401 credentials; 403 denied permissions; database role overrides client assertions; permission checks precede target lookup; fixed trusted JWT algorithm and required claims; safe field projections and upstream errors. The local issuer is a fixture, not production authentication. See each student exercise for exact acceptance criteria.

From each `core/` folder, run the extension tests separately with `python -m pytest ../challenge/test_challenge.py -q`. They set synthetic configuration and, where needed, an isolated database. Run this as a new process after the core tests because the key-rotation extension deliberately overrides the core verifier. These tests cover both successful challenge behaviour and retained access boundaries.

For the movie application, complete the TMDB Credits requirement using an approved logo before publishing a real application. The reference implementation is a local teaching solution; no TMDB logo or credential is fabricated here.
