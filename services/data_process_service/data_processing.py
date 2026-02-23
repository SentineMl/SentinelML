# services/process-data/logic.py
# Purpose: take ONE raw transaction event (dict) and return a processed + ML-ready feature dict

from __future__ import annotations
import ast 
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple


#bech nconverti l clean string
def _to_str(x: Any) -> Optional[str]:
    if x is None:
        return None
    s = str(x).strip()
    return s if s else None


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
    
def _to_int(x: Any) -> Optional[int]:
    if x is None:
        return None
    try:
        return int(x)
    except (TypeError, ValueError):
        return None

def _parse_ts(ts: Any) -> Optional[datetime]:

    if ts is None:
        return None
    #ken deja timestamp jwha bahy
    if isinstance(ts, datetime):
        dt = ts
    #kenha unix  timestamp
    elif isinstance(ts, (int, float)):
      t = float(ts)
      if t > 1e12:   # treat as milliseconds
        t /= 1000.0
      dt = datetime.fromtimestamp(t, tz=timezone.utc)
    #kenha string
    else:
        s = str(ts).strip()
        if not s:
            return None
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _is_weekend(dt: datetime) -> int:
    return 1 if dt.weekday() >= 5 else 0


def _log1p_safe(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    if x < 0:
        return None
    return math.log1p(x)


def _norm_upper(x: Any) -> Optional[str]:
    s = _to_str(x)
    return s.upper() if s else None


def _norm_lower(x: Any) -> Optional[str]:
    s = _to_str(x)
    return s.lower() if s else None


def _bool_to_int(x: Any) -> Optional[int]:
    if x is None:
        return None
    if isinstance(x, bool):
        return 1 if x else 0
    if isinstance(x, (int, float)):
        return 1 if float(x) != 0 else 0
    s = str(x).strip().lower()
    if s in {"true", "t", "yes", "y", "1"}:
        return 1
    if s in {"false", "f", "no", "n", "0"}:
        return 0
    return None


def _flatten_velocity(v: Any) -> Dict[str, Optional[float]]:

    if not isinstance(v, dict):
        return {
            "velocity_num_transactions_1h": None,
            "velocity_total_amount_1h": None,
            "velocity_unique_merchants_1h": None,
            "velocity_unique_countries_1h": None,
            "velocity_max_single_amount_1h": None,
        }

    return {
        "velocity_num_transactions_1h": _to_int(v.get("num_transactions")),
        "velocity_total_amount_1h": _to_float(v.get("total_amount")),
        "velocity_unique_merchants_1h": _to_int(v.get("unique_merchants")),
        "velocity_unique_countries_1h": _to_int(v.get("unique_countries")),
        "velocity_max_single_amount_1h": _to_float(v.get("max_single_amount")),
    }

def _unwrap_features(raw: Dict[str, Any]) -> Dict[str, Any]:
    # raw can be {"features": {...}} or already flat
    feats = raw.get("features")
    return feats if isinstance(feats, dict) else raw


def _parse_velocity(v: Any) -> Any:
    # v may be dict OR a string that looks like a dict
    if isinstance(v, dict):
        return v
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            # your velocity is like "{'num_transactions': 1197, ...}" (single quotes)
            return ast.literal_eval(s)
        except Exception:
            return None
    return None

@dataclass(frozen=True)
class ProcessingConfig:
    high_risk_categories: Tuple[str, ...] = ("GAMING", "CRYPTO", "GAMBLING")



def process_event(raw: Dict[str, Any], cfg: ProcessingConfig = ProcessingConfig()) -> Dict[str, Any]:
    
    raw = _unwrap_features(raw)

    transaction_id = _to_str(raw.get("transaction_id"))
    customer_id = _to_str(raw.get("customer_id"))

    dt = _parse_ts(raw.get("timestamp"))
    if dt is not None:
        transaction_hour = dt.hour
        weekend_transaction = _is_weekend(dt)
        ts_iso = dt.isoformat().replace("+00:00", "Z")
    else:
        transaction_hour = None
        weekend_transaction = None
        ts_iso = None

    amount = _to_float(raw.get("amount"))
    amount_log = _log1p_safe(amount)
    currency = _norm_upper(raw.get("currency"))
    country = _norm_upper(raw.get("country"))
    city = _to_str(raw.get("city"))
    city_size = _norm_lower(raw.get("city_size"))

    merchant_category = _to_str(raw.get("merchant_category"))
    merchant_type = _norm_lower(raw.get("merchant_type"))
    merchant = _to_str(raw.get("merchant"))


    high_risk_merchant = _bool_to_int(raw.get("high_risk_merchant"))
    if high_risk_merchant is None:
        cat_norm = _norm_upper(merchant_category)
        high_risk_merchant = 1 if (cat_norm in cfg.high_risk_categories) else 0

    card_type = _to_str(raw.get("card_type"))
    card_present = _bool_to_int(raw.get("card_present"))
    device = _to_str(raw.get("device"))
    channel = _norm_lower(raw.get("channel"))
    distance_from_home = _bool_to_int(raw.get("distance_from_home"))

    velocity_dict = _parse_velocity(raw.get("velocity_last_hour"))  
    velocity = _flatten_velocity(velocity_dict)

    card_number = _to_str(raw.get("card_number"))
    device_fingerprint = _to_str(raw.get("device_fingerprint"))
    ip_address = _to_str(raw.get("ip_address"))



    processed: Dict[str, Any] = {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "timestamp": ts_iso,
        "transaction_hour": transaction_hour,
        "weekend_transaction": weekend_transaction,

        "amount": amount,
        "amount_log": amount_log,
        "currency": currency,
        "country": country,
        "city": city,
        "city_size": city_size,

        "merchant_category": merchant_category,
        "merchant_type": merchant_type,
        "merchant": merchant,
        "high_risk_merchant": high_risk_merchant,

        "card_type": card_type,
        "card_present": card_present,
        "channel": channel,
        "device": device,
        "distance_from_home": distance_from_home,

        **velocity,

        #we can hash them or remove them
        "card_number": card_number,
        "device_fingerprint": device_fingerprint,
        "ip_address": ip_address,


    }

    return processed
