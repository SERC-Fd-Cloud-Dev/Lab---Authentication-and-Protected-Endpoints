from fastapi import Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from main import app, current_user
from database import User, get_db

@app.get("/reports/summary")
def summary(user: User=Depends(current_user),db: Session=Depends(get_db)):
    if user.role not in {"reporter","lecturer"}:
        raise HTTPException(403,"Reporting access required")
    count=db.scalar(select(func.count()).select_from(User).where(User.is_active.is_(True)))
    return {"active_accounts":count}
