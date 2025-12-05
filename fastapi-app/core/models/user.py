from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .match import Match


class UserAuth(Base):
    __tablename__ = "users_auth"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]

    user_data: Mapped["UserData"] = relationship(
        cascade="all, delete-orphan", back_populates="user_auth", uselist=False
    )


class UserData(Base):
    __tablename__ = "users_data"

    id: Mapped[int] = mapped_column(ForeignKey("users_auth.id"), primary_key=True)
    first_name: Mapped[str]
    middle_name: Mapped[str]
    last_name: Mapped[str]

    user_auth: Mapped["UserAuth"] = relationship(
        back_populates="user_data",
    )

    matches_as_player1: Mapped[List["Match"]] = relationship(
        foreign_keys="Match.player1_id", back_populates="player1"
    )
    matches_as_player2: Mapped[List["Match"]] = relationship(
        foreign_keys="Match.player2_id", back_populates="player2"
    )
