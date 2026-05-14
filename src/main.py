import time

from nt8_connector import get_price, is_market_open, get_net_position
from trader import place_buy, recover_orphaned_positions
from grid_state import load_state, sync_closed_levels
from config import SLEEP_SECONDS, GRID_GAP
from logger import log, err


def run():
    log("Aurum Grid Bot starting (NinjaTrader / MGC)")

    while True:
        if not is_market_open():
            log("MARKET CLOSED -> waiting")
            time.sleep(5)
            continue

        tick = get_price()
        if tick is None:
            err("NO PRICE DATA — is AurumFeed indicator running on an MGC chart?")
            time.sleep(2)
            continue

        ask    = tick["ask"]
        bid    = tick["bid"]
        spread = round(ask - bid, 2)

        levels     = load_state()
        net_pos    = get_net_position()
        levels     = sync_closed_levels(levels, net_pos)

        log("========================================")
        log(f"PRICE -> ASK: {ask} | BID: {bid} | SPREAD: {spread}")
        log(f"GRID LEVELS: {len(levels)} | NET POSITION: {net_pos}")

        for lvl in levels:
            log(f"LEVEL -> entry: {lvl['entry_price']} | tp: {lvl['tp_price']}")

        # ---- FIRST BUY / ORPHAN RECOVERY ----
        if not levels:
            if net_pos > 0:
                log(f"DECISION -> ORPHAN RECOVERY ({net_pos} open position(s), no grid state)")
                recover_orphaned_positions(ask, net_pos)
                time.sleep(0.5)
                continue
            log("DECISION -> FIRST BUY")
            place_buy(ask)
            time.sleep(0.5)
            continue

        # ---- GRID BUY ----
        lowest_entry   = min(lvl["entry_price"] for lvl in levels)
        next_buy_level = round(lowest_entry - GRID_GAP, 2)

        log(f"LOWEST ENTRY: {lowest_entry} | NEXT BUY LEVEL: {next_buy_level}")

        if ask <= next_buy_level:
            log("DECISION -> GRID BUY TRIGGERED")
            place_buy(ask)
            time.sleep(0.5)
            continue

        # ---- HOLD ----
        log("DECISION -> HOLD (price not low enough)")
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    run()
