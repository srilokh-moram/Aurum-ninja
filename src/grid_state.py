import json
from datetime import datetime
from pathlib import Path

from logger import log

STATE_FILE = Path("data/grid_state.json")


def load_state() -> list:
    if not STATE_FILE.exists():
        return []
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_state(levels: list) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(levels, f, indent=2)


_SETTLE_SECONDS = 5  # grace period after a buy before syncing


def sync_closed_levels(levels: list, net_position: int) -> list:
    """
    Remove grid levels whose TP orders have been filled.

    Skips sync entirely if any level was placed within the last
    _SETTLE_SECONDS seconds — gives NT8 time to update the position
    before we compare against net_position.
    """
    if not levels or net_position >= len(levels):
        return levels

    now = datetime.now()
    for lvl in levels:
        age = (now - datetime.fromisoformat(lvl["timestamp"])).total_seconds()
        if age < _SETTLE_SECONDS:
            return levels  # positions still settling, skip sync

    closed_count = len(levels) - net_position
    sorted_levels = sorted(levels, key=lambda x: x["tp_price"])
    remaining = sorted_levels[closed_count:]

    log(f"SYNC: {closed_count} TP(s) filled -> {len(remaining)} level(s) remain")
    save_state(remaining)
    return remaining
