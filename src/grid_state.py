import json
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


def sync_closed_levels(levels: list, net_position: int) -> list:
    """
    Remove grid levels that were closed by their TP orders hitting.

    When net_position < len(levels), some SELL LIMIT (TP) orders filled.
    We assume the levels with the LOWEST tp_price fired first
    (price rises → lowest TP hits first).
    """
    if not levels or net_position >= len(levels):
        return levels

    closed_count = len(levels) - net_position
    sorted_levels = sorted(levels, key=lambda x: x["tp_price"])
    remaining = sorted_levels[closed_count:]

    log(f"SYNC: {closed_count} TP(s) filled -> {len(remaining)} level(s) remain")
    save_state(remaining)
    return remaining
