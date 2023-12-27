from decimal import Decimal
from typing import Annotated
from models.enums import UserStatus
from db import Base

import datetime
from enum import Enum

from sqlalchemy import ForeignKey, String, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship


default_time = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False)
    phone: Mapped[str]
    created: Mapped[default_time]
    updated: Mapped[datetime.datetime] = mapped_column(
        onupdate=datetime.datetime.utcnow, server_default=text("TIMEZONE('utc', now())")
    )
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ANONYMOUS)

    worker: Mapped["Worker"] = relationship("Worker", back_populates="user")

    def __repr__(self) -> str:
        return f"{self.username} - {self.id}"


class Worker(Base):
    __tablename__ = "worker"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    salary: Mapped[Decimal | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    user: Mapped["User"] = relationship("User", back_populates="worker", uselist=False)
    companies: Mapped[list["Company"]] = relationship(
        "Company", back_populates="workers", secondary="company_worker"
    )
    
    def __eq__(self, other):
        if isinstance(other, Worker):
            return self.id == other.id
        return False

    def __repr__(self) -> str:
        return f"{self.id}#Worker"
