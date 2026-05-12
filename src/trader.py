import MetaTrader5 as mt5
from config import SYMBOL, LOT_SIZE, GRID_GAP
from logger import log, err
import time


def place_buy(price):
    # Step 1: Send BUY without TP
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "deviation": 50,
        "magic": 10001,
        "comment": "grid buy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)

    if not result or result.retcode != mt5.TRADE_RETCODE_DONE:
        err(f"BUY FAILED: {result}")
        return result

    # Step 2: Get actual filled position
    time.sleep(0.2)  # small delay to ensure MT5 updates

    positions = mt5.positions_get(ticket=result.order)

    if not positions:
        err("ERROR: Position not found after buy")
        return result

    pos = positions[0]
    filled_price = pos.price_open

    # Step 3: Calculate exact TP
    tp_price = filled_price + GRID_GAP

    # Step 4: Modify position to add TP
    modify_request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": pos.ticket,
        "tp": tp_price,
        "symbol": SYMBOL,
    }

    modify_result = mt5.order_send(modify_request)

    if modify_result and modify_result.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"BUY FILLED @ {filled_price} | TP SET @ {tp_price}")
    else:
        err(f"TP SET FAILED: {modify_result}")

    return result