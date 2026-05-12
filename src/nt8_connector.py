import json
import os
from datetime import datetime, timezone
from pathlib import Path

from config import NT8_ACCOUNT, NT8_SYMBOL, NT8_INCOMING_DIR, NT8_FEED_FILE
from logger import log, err


def _incoming_dir() -> Path:
    p = Path(NT8_INCOMING_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_feed() -> dict | None:
    try:
        with open(NT8_FEED_FILE) as f:
            return json.load(f)
    except Exception:
        return None


def get_price() -> dict | None:
    feed = read_feed()
    if feed is None:
        return None
    return {"ask": feed["ask"], "bid": feed["bid"]}


def is_market_open() -> bool:
    feed = read_feed()
    if feed is None:
        return False
    return bool(feed.get("market_open", False))


def get_net_position() -> int:
    feed = read_feed()
    if feed is None:
        return 0
    return int(feed.get("net_position", 0))


def _send(command: str) -> bool:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = _incoming_dir() / f"aurum_{ts}.txt"
    try:
        path.write_text(command + "\n", encoding="utf-8")
        log(f"ATI -> {command}")
        return True
    except Exception as e:
        err(f"ATI WRITE FAILED: {e}")
        return False


def place_market_buy(order_id: str) -> bool:
    cmd = f"PLACE;{NT8_ACCOUNT};{NT8_SYMBOL};BUY;1;MARKET;0;0;DAY;;{order_id};"
    return _send(cmd)


def place_limit_sell(order_id: str, price: float) -> bool:
    cmd = f"PLACE;{NT8_ACCOUNT};{NT8_SYMBOL};SELL;1;LIMIT;{price:.2f};0;GTC;;{order_id};"
    return _send(cmd)


def cancel_order(order_id: str) -> bool:
    cmd = f"CANCEL;{NT8_ACCOUNT};{order_id}"
    return _send(cmd)
