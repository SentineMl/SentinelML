from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import CustomerAggregate, Prediction, Transaction


def _parse_timestamp(value: Any) -> dt.datetime:
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, str) and value:
        normalized = value.replace("Z", "+00:00")
        return dt.datetime.fromisoformat(normalized)
    return dt.datetime.now(dt.timezone.utc)


def add_transaction(session: Session, transaction_data: dict[str, Any], *, commit: bool = True) -> Transaction:
    """
    Insert one transaction and update customer aggregate (count, avg_amount, last_transaction_at).

    If the transaction_id already exists, the existing row is returned and aggregate is not updated.
    """
    transaction_id = str(transaction_data["transaction_id"])

    existing = session.scalar(
        select(Transaction).where(Transaction.transaction_id == transaction_id)
    )
    if existing is not None:
        return existing

    ts = _parse_timestamp(transaction_data.get("timestamp"))
    amount_value = float(transaction_data.get("amount") or 0.0)

    transaction = Transaction(
        transaction_id=transaction_id,
        customer_id=transaction_data.get("customer_id"),
        card_number=transaction_data.get("card_number"),
        transaction_timestamp=ts,
        merchant_category=transaction_data.get("merchant_category"),
        merchant_type=transaction_data.get("merchant_type"),
        merchant=transaction_data.get("merchant"),
        amount=amount_value,
        currency=transaction_data.get("currency"),
        country=transaction_data.get("country"),
        city=transaction_data.get("city"),
        city_size=transaction_data.get("city_size"),
        card_type=transaction_data.get("card_type"),
        card_present=transaction_data.get("card_present"),
        device=transaction_data.get("device"),
        channel=transaction_data.get("channel"),
        device_fingerprint=transaction_data.get("device_fingerprint"),
        ip_address=transaction_data.get("ip_address"),
        distance_from_home=transaction_data.get("distance_from_home"),
        high_risk_merchant=transaction_data.get("high_risk_merchant"),
        transaction_hour=transaction_data.get("transaction_hour"),
        weekend_transaction=transaction_data.get("weekend_transaction"),
    )
    session.add(transaction)

    customer_id = transaction.customer_id
    if customer_id:
        aggregate = session.get(CustomerAggregate, customer_id)
        if aggregate is None:
            aggregate = CustomerAggregate(
                customer_id=customer_id,
                txn_count=1,
                avg_amount=amount_value,
                last_transaction_at=ts,
            )
            session.add(aggregate)
        else:
            previous_count = int(aggregate.txn_count)
            previous_avg = float(aggregate.avg_amount)
            new_count = previous_count + 1
            aggregate.avg_amount = ((previous_avg * previous_count) + amount_value) / new_count
            aggregate.txn_count = new_count
            if aggregate.last_transaction_at is None or ts > aggregate.last_transaction_at:
                aggregate.last_transaction_at = ts

    if commit:
        session.commit()
        session.refresh(transaction)

    return transaction


def save_prediction(
    session: Session,
    *,
    transaction_id: str,
    score: float,
    prediction_timestamp: dt.datetime | None = None,
    commit: bool = True,
) -> Prediction:
    """
    Insert prediction for an existing transaction.
    """
    transaction = session.scalar(
        select(Transaction).where(Transaction.transaction_id == transaction_id)
    )
    if transaction is None:
        raise ValueError(f"Transaction not found for transaction_id='{transaction_id}'")

    prediction = Prediction(
        transaction_id=transaction_id,
        score=float(score),
        prediction_timestamp=prediction_timestamp or dt.datetime.now(dt.timezone.utc),
    )
    session.add(prediction)

    if commit:
        session.commit()
        session.refresh(prediction)

    return prediction