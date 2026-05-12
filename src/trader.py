import time
from datetime import datetime

from config import GRID_GAP
from nt8_connector import place_market_buy, place_limit_sell
from grid_state import load_state, save_state
from logger import log, err


def _order_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


def place_buy(ask: float) -> bool:
    buy_id = _order_id("BUY")
    tp_id  = _order_id("TP")
    tp_price = round(ask + GRID_GAP, 2)

    if not place_market_buy(buy_id):
        err("MARKET BUY FAILED")
        return False

    # Brief pause so NT8 processes the market order before we add the TP
    time.sleep(0.5)

    if not place_limit_sell(tp_id, tp_price):
        err(f"TP ORDER FAILED for {buy_id}")
        return False

    levels = load_state()
    levels.append({
        "entry_price":  ask,
        "tp_price":     tp_price,
        "buy_order_id": buy_id,
        "tp_order_id":  tp_id,
        "timestamp":    datetime.now().isoformat(),
    })
    save_state(levels)

    log(f"BUY PLACED @ ~{ask} | TP @ {tp_price} | levels: {len(levels)}")
    return True
