from fastapi import Depends, HTTPException
from main import app
from auth import verified_claims

@app.get("/preview")
def preview(claims: dict = Depends(verified_claims)):
    scope=claims.get("scope", "")
    if not isinstance(scope,str) or "read:preview" not in scope.split():
        raise HTTPException(403,"read:preview scope required")
    return {"preview":"Available to this token"}
