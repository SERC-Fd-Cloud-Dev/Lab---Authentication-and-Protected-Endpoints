from sqlalchemy.orm import Session
from database import User,engine
with Session(engine) as s:
    if s.get(User,"u5") is None:
        s.add(User(id="u5",username="reporting-service",role="reporter",is_active=True));s.commit()
