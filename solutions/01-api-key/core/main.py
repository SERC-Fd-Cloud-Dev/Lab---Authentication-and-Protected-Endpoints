from pathlib import Path
import os
import secrets
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
API_KEY = os.environ.get("LAB_API_KEY", "")
if len(API_KEY) < 32:
    raise RuntimeError("Set LAB_API_KEY to a random value of at least 32 characters")

app = FastAPI(title="Header key lab")
key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_key(value: str | None = Depends(key_header)):
    if value is None or not secrets.compare_digest(value.encode(), API_KEY.encode()):
        raise HTTPException(401, "Invalid or missing API key", headers={"WWW-Authenticate": "APIKey"})

@app.get("/public")
def public():
    return {"message": "Anyone can read this"}

@app.get("/protected", dependencies=[Depends(require_key)])
def protected():
    return {"message": "Valid key accepted"}

@app.get("/status", dependencies=[Depends(require_key)])
def status():
    return {"status": "ready"}

@app.get("/lab-info", dependencies=[Depends(require_key)])
def lab_info():
    return {"lab": "authentication", "access": "key required"}
