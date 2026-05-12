import time
import MetaTrader5 as mt5

from mt5_connector import connect, ensure_connection, get_price, is_market_open
from trader import place_buy
from config import SLEEP_SECONDS, GRID_GAP
from logger import log, err


def get_mt5_positions():
    positions = mt5.positions_get()

    if positions is None:
        return []

    return [
        {
            "ticket": p.ticket,
            "price": p.price_open,
            "volume": p.volume,
            "tp": p.tp
        }
        for p in positions
    ]


# 🔥 Add TP to old positions (one-time safety)
def add_tp_to_existing_positions():
    positions = mt5.positions_get()

    if positions is None:
        return

    for p in positions:
        if p.tp == 0.0:
            tp_price = p.price_open + GRID_GAP

            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": p.ticket,
                "tp": tp_price,
                "symbol": p.symbol,
            }

            result = mt5.order_send(request)
            log(f"TP ADDED -> ticket: {p.ticket} | TP: {tp_price}")


def run():
    connect()

    # Fix existing trades
    add_tp_to_existing_positions()

    while True:
        ensure_connection()

        if not is_market_open():
            log("MARKET CLOSED -> waiting")
            time.sleep(1)
            continue

        tick = get_price()
        if tick is None:
            err("NO TICK DATA")
            time.sleep(0.1)
            continue

        ask = tick["ask"]
        bid = tick["bid"]
        spread = round(ask - bid, 3)

        positions = get_mt5_positions()

        # ================= HEADER =================
        log("========================================")
        log(f"PRICE -> ASK: {ask} | BID: {bid} | SPREAD: {spread}")
        log(f"POSITIONS COUNT: {len(positions)}")

        if positions:
            log(f"HOLDINGS: {[p['price'] for p in positions]}")
        else:
            log("HOLDINGS: []")

        # ================= POSITION DETAILS =================
        for p in positions:
            log(f"POS -> ticket: {p['ticket']} | buy: {p['price']} | tp: {p['tp']}")

        # ================= FIRST BUY =================
        if not positions:
            log("DECISION -> FIRST BUY")

            place_buy(ask)
            time.sleep(0.2)
            continue

        # ================= GRID LOGIC =================
        lowest_price = min(p["price"] for p in positions)
        next_buy_level = lowest_price - GRID_GAP

        log(f"LOWEST PRICE: {lowest_price}")
        log(f"NEXT BUY LEVEL: {next_buy_level}")

        # ================= DECISION =================
        if ask <= next_buy_level:
            log("DECISION -> GRID BUY TRIGGERED")

            place_buy(ask)
            time.sleep(0.2)
            continue

        # ================= HOLD =================
        log("DECISION -> HOLD (price not low enough)")

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    run()