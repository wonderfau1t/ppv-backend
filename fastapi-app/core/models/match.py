import datetime as dt
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .user import UserData


class MatchStatus(str, Enum):
    IN_PROGRESS = "in progress"
    FINISHED = "finished"
    CANCELED = "cancled"
    REGISTERED = "registered"

    @property
    def label(self):
        return {
            MatchStatus.IN_PROGRESS: "В процессе",
            MatchStatus.FINISHED: "Закончен",
            MatchStatus.CANCELED: "Отменен",
            MatchStatus.REGISTERED: "Зарегистрирован",
        }[self]


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    datetime: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now)
    type: Mapped[str] = mapped_column(default="Любительский")
    duration_in_minutes: Mapped[Optional[int]]
    player1_id: Mapped[int] = mapped_column(ForeignKey("users_data.id"))
    player2_id: Mapped[int] = mapped_column(ForeignKey("users_data.id"))
    player1_score: Mapped[int] = mapped_column(default=0)
    player2_score: Mapped[int] = mapped_column(default=0)
    status: Mapped[MatchStatus] = mapped_column(
        SQLEnum(MatchStatus, name="match_status"), default=MatchStatus.REGISTERED
    )
    # Победитель матча
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users_data.id"), nullable=True)

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
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users_data.id"), nullable=True)

    match: Mapped["Match"] = relationship(foreign_keys=[match_id], back_populates="sets")
    winner: Mapped["UserData"] = relationship(foreign_keys=[winner_id])
