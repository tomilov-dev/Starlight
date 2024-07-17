import sys
from pathlib import Path
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))
from database.core import BaseORM


class UserORM(BaseORM):
    __tablename__ = "usermodel"

    username: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[bytes]
    active: Mapped[bool] = True

    __table_args__ = (
        UniqueConstraint("username"),
        UniqueConstraint("email"),
    )
