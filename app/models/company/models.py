from decimal import Decimal
from db import Base

import datetime
from enum import Enum

from sqlalchemy import String, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    name: Mapped[str] = mapped_column(unique=True)
    technical_map: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"{self.id}#{self.name}"


class CompanyState(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    grams_of_tobacco: Mapped[int]
    summa: Mapped[Decimal]
    photo1: Mapped[str]
    photo2: Mapped[str]
    photo3: Mapped[str]
    photo4: Mapped[str]
    created: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    worker_id: Mapped[int] = mapped_column(ForeignKey("worker.id", ondelete="SET NULL"))
    company_id: Mapped[int] = mapped_column(
        ForeignKey("company.id", ondelete="CASCADE")
    )


class BeginShift(CompanyState):
    __tablename__ = "begin_shift"

    live: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"{self.id}#{self.summa} рублей"


class EndShift(CompanyState):
    __tablename__ = "end_shift"

    quantity_of_sold: Mapped[int]
    promo_quantity: Mapped[int]
    card: Mapped[int]
    cash: Mapped[int]
    in_club: Mapped[int]
    in_club_card: Mapped[int]
    in_club_cash: Mapped[int]
    tips: Mapped[Decimal]
    begin_shift_id: Mapped[int] = mapped_column(
        ForeignKey("begin_shift.id", ondelete="SET NULL")
    )

    def __repr__(self) -> str:
        return f"{self.id}#{self.summa}"
