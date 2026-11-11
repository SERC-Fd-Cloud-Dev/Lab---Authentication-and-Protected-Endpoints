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
