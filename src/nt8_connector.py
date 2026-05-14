import json
import socket
from pathlib import Path

from config import NT8_ACCOUNT, NT8_SYMBOL, NT8_ATI_HOST, NT8_ATI_PORT, NT8_FEED_FILE
from logger import log, err


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
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((NT8_ATI_HOST, NT8_ATI_PORT))

            # NT8 sends "2" as a ready signal immediately on connect
            buf = ""
            try:
                buf = s.recv(4096).decode("ascii", errors="ignore")
            except Exception:
                pass

            s.sendall((command + "\r\n").encode("ascii"))
            log(f"ATI -> {command}")

            # Read order response — skip second read if welcome already bundled it
            if "Orders|" not in buf:
                try:
                    buf = s.recv(4096).decode("ascii", errors="ignore")
                except Exception:
                    pass

            if buf.strip():
                log(f"ATI RESPONSE: {buf.strip()}")

            return True
    except ConnectionRefusedError:
        err(f"ATI CONNECTION REFUSED — is NT8 running with AT Interface enabled on port {NT8_ATI_PORT}?")
        return False
    except Exception as e:
        err(f"ATI FAILED: {e}")
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
