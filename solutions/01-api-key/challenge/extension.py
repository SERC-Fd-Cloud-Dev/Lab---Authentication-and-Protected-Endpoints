import os
import secrets
from fastapi import Depends, HTTPException
from main import app, key_header, require_key, API_KEY
NEXT_KEY=os.environ.get("LAB_API_KEY_NEXT", "")
if len(NEXT_KEY)<32: raise RuntimeError("Configure a random LAB_API_KEY_NEXT")

def rotating_key(value: str | None = Depends(key_header)):
    supplied=(value or "").encode()
    accepted=False
    for allowed in (API_KEY,NEXT_KEY):
        accepted = secrets.compare_digest(supplied,allowed.encode()) or accepted
    if value is None or not accepted:
        raise HTTPException(401,"Invalid or missing API key",headers={"WWW-Authenticate":"APIKey"})
app.dependency_overrides[require_key]=rotating_key
