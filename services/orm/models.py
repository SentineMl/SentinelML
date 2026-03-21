from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    customer_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    card_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    transaction_timestamp: Mapped[dt.datetime] = mapped_column(
        "timestamp",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    merchant_category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    merchant_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(128), nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    city_size: Mapped[str | None] = mapped_column(String(32), nullable=True)
    card_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    card_present: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    device: Mapped[str | None] = mapped_column(String(64), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_fingerprint: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    distance_from_home: Mapped[float | None] = mapped_column(Float, nullable=True)
    high_risk_merchant: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    transaction_hour: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weekend_transaction: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
    )
    customer_aggregate: Mapped["CustomerAggregate | None"] = relationship(
        "CustomerAggregate",
        primaryjoin="foreign(Transaction.customer_id) == CustomerAggregate.customer_id",
        viewonly=True,
        uselist=False,
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("transactions.transaction_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    prediction_timestamp: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    transaction: Mapped["Transaction"] = relationship(back_populates="predictions")


class CustomerAggregate(Base):
    __tablename__ = "customer_aggregates"

    customer_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    txn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    last_transaction_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        primaryjoin="foreign(Transaction.customer_id) == CustomerAggregate.customer_id",
        viewonly=True,
    )