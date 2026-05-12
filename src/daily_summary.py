import MetaTrader5 as mt5
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG =================
SYMBOL = os.getenv("SYMBOL")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")

MT5_LOGIN = int(os.getenv("MT5_LOGIN"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")

# ================= CONNECT =================
if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
    print("MT5 connection failed")
    quit()

# ================= TIME RANGE =================
now = datetime.now()
start_of_day = datetime(now.year, now.month, now.day)

# ================= TODAY DEALS =================
deals_today = mt5.history_deals_get(start_of_day, now)

today_profit = 0
today_count = 0

if deals_today:
    for d in deals_today:
        if d.entry == 1:
            today_profit += d.profit
            today_count += 1

# ================= TOTAL PROFIT =================
all_deals = mt5.history_deals_get(datetime(2000, 1, 1), now)

total_profit = 0
if all_deals:
    for d in all_deals:
        if d.entry == 1:
            total_profit += d.profit

# ================= OPEN POSITIONS =================
positions = mt5.positions_get()

open_count = 0
floating_pl = 0

if positions:
    open_count = len(positions)
    floating_pl = sum(p.profit for p in positions)

# ================= MESSAGE =================
msg = (
    f"📊 *Trading Summary - {SYMBOL}*\n\n"
    f"📅 Date: {now.strftime('%Y-%m-%d')}\n\n"
    f"✅ Deals Today: {today_count}\n"
    f"💰 Profit Today: ${round(today_profit, 2)}\n"
    f"📈 Total Profit: ${round(total_profit, 2)}\n\n"
    f"📂 Open Positions: {open_count}\n"
    f"⚖️ Floating P/L: ${round(floating_pl, 2)}"
)

# ================= SEND TELEGRAM =================
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

for chat_id in CHAT_IDS:
    chat_id = chat_id.strip()
    if not chat_id:
        continue

    try:
        r = requests.post(url, json={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        })
        if r.status_code == 200:
            print(f"Sent to {chat_id}")
        else:
            print(f"Failed to {chat_id}: {r.text}")
    except Exception as e:
        print(f"Error sending to {chat_id}: {e}")

mt5.shutdown()
