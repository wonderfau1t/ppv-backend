import datetime as dt
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .user import UserData


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now())
    type: Mapped[str] = mapped_column(default="Любительский")
    duration_in_minutes: Mapped[Optional[int]]
    player1_id: Mapped[int] = mapped_column(ForeignKey("users_data.id"))
    player2_id: Mapped[int] = mapped_column(ForeignKey("users_data.id"))
    player1_score: Mapped[Optional[int]]
    player2_score: Mapped[Optional[int]]
    # Победитель матча
    winner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users_data.id"), nullable=True
    )

    player1: Mapped["UserData"] = relationship(
        foreign_keys=[player1_id], back_populates="matches_as_player1"
    )
    player2: Mapped["UserData"] = relationship(
        foreign_keys=[player2_id], back_populates="matches_as_player2"
    )

    winner: Mapped["UserData"] = relationship(foreign_keys=[winner_id])
    sets: Mapped[List["MatchSet"]] = relationship(
        back_populates="match",
        order_by="MatchSet.set_number",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class MatchSet(Base):
    __tablename__ = "match_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    set_number: Mapped[int]  # 1, 2, 3 ...
    player1_score: Mapped[int]
    player2_score: Mapped[int]
    # Победитель сета
    winner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users_data.id"), nullable=True
    )

    match: Mapped["Match"] = relationship(
        foreign_keys=[match_id], back_populates="sets"
    )
    winner: Mapped["UserData"] = relationship(foreign_keys=[winner_id])
