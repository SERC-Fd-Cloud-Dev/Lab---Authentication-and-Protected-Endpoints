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

@app.get("/profiles/{user_id}")
def profile(user_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    # Permission check precedes target lookup: other students always get 403.
    if user.id != user_id and user.role != "lecturer":
        raise HTTPException(403, "Owner or lecturer access required")
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(404, "Profile not found")
    return {"id": target.id, "username": target.username}
