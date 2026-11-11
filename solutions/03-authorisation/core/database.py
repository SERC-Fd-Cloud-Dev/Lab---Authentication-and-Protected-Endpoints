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
