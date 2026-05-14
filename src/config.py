import os
from dotenv import load_dotenv

load_dotenv()

# NinjaTrader 8 account / symbol
NT8_ACCOUNT = os.getenv("NT8_ACCOUNT", "Sim101")
NT8_SYMBOL  = os.getenv("NT8_SYMBOL", "MGC 06-26")   # update each roll

# ATI socket (NT8 listens on this port — see Tools > Options > Automated trading interface)
NT8_ATI_HOST = os.getenv("NT8_ATI_HOST", "localhost")
NT8_ATI_PORT = int(os.getenv("NT8_ATI_PORT", 36973))

# Price/position feed written by AurumFeed.cs indicator
NT8_FEED_FILE = os.path.expandvars(
    os.getenv("NT8_FEED_FILE",
              r"%USERPROFILE%\Documents\NinjaTrader 8\aurum_feed.json")
)

# Grid parameters
LOT_SIZE      = int(float(os.getenv("LOT_SIZE", 1)))   # contracts (MGC)
GRID_GAP      = float(os.getenv("GRID_GAP", 5.0))      # dollars per oz
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", 1.0))
