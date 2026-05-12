# Aurum Trading Bot v2

An automated **grid trading bot** for MetaTrader 5 that executes mechanical buy/sell orders based on price levels and predefined profit targets.

## Overview

Aurum is a Python-based automated trading system designed to operate 24/7 on MetaTrader 5 accounts. It implements a grid trading strategy that:

- **Places buy orders** when price drops below the lowest held position
- **Sells positions** when price reaches take-profit levels
- **Manages risk** by setting stop-loss and take-profit on all trades
- **Auto-reconnects** to maintain stability during network disruptions
- **Logs all activity** for monitoring and debugging

## Features

✅ **Automated Grid Trading** - Systematic entry and exit management  
✅ **Auto-Reconnect** - Maintains MT5 connection stability  
✅ **Take-Profit Management** - Automatic TP setting on all positions  
✅ **Market Hours Detection** - Skips trading during market closure  
✅ **Configurable Parameters** - Lot size, grid gap, sleep intervals via environment variables  
✅ **Comprehensive Logging** - Track all trades and system events  
✅ **Auto-Restart on Crash** - Windows batch runner with recovery  

## Requirements

- Python 3.7+
- MetaTrader 5
- Active MT5 trading account
- Windows (for batch file runner)

## Installation

### 1. Clone or download this repository
```bash
git clone <repo-url>
cd Aurum-v2
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:

```env
# MetaTrader 5 Credentials
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_server_name

# Trading Configuration
SYMBOL=EURUSD          # Trading pair
LOT_SIZE=0.01          # Trade volume (microlots)
GRID_GAP=5             # Price distance between orders (in pips/cents)
SLEEP_SECONDS=1        # Loop sleep interval in seconds
```

**Important**: Keep your `.env` file secure and never commit it to version control.

## Usage

### Start the bot manually
```bash
python src/main.py
```

### Start with auto-restart (Windows)
```bash
run_bot.bat
```

The batch file will:
- Activate the Python virtual environment
- Run the trading bot
- Automatically restart if it crashes

## How It Works

### Grid Trading Strategy

1. **First Buy**: When no positions exist, the bot buys at the current market price
2. **Grid Entry**: If price drops below the lowest held position by `GRID_GAP`, place another buy
3. **Grid Exit**: Sell all positions with `+GRID_GAP` profit

### Example Flow
```
Price: 1.0900 → BUY 1 lot at 1.0900
Price: 1.0895 → BUY 1 lot at 1.0895 (1.0900 - 0.0005)
Price: 1.0905 → SELL both positions with +50 pips profit
```

### Position Management

- Each position automatically receives a **take-profit order** at `entry_price + GRID_GAP`
- Stop-loss protection is implemented at the strategy level
- Existing positions without TP are updated on bot startup

## Project Structure

```
Aurum-v2/
├── src/
│   ├── main.py              # Main trading loop
│   ├── mt5_connector.py      # MetaTrader 5 connection & market data
│   ├── trader.py            # Order placement and execution
│   ├── strategy.py          # Trading logic (buy/sell decisions)
│   ├── config.py            # Configuration from environment variables
│   └── logger.py            # Logging utilities
├── requirements.txt         # Python dependencies
├── run_bot.bat             # Windows runner with auto-restart
└── README.md               # This file
```

## Configuration Guide

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SYMBOL` | - | Trading instrument (e.g., EURUSD, GBPUSD) |
| `LOT_SIZE` | 0.01 | Trade volume in lots (0.01 = 1k units) |
| `GRID_GAP` | 5 | Grid spacing in pips (distance between orders) |
| `SLEEP_SECONDS` | 1 | Seconds between strategy checks |

### Adjusting Grid Gap

- **Smaller gap (e.g., 2 pips)**: More frequent trades, higher risk, more capital needed
- **Larger gap (e.g., 20 pips)**: Fewer trades, lower frequency, requires less capital

## Logging

All bot activity is logged to `logs/runner.log` (when using batch file) or console output.

Sample log:
```
========================================
PRICE → ASK: 1.0905 | BID: 1.0903 | SPREAD: 0.002
POSITIONS COUNT: 2
HOLDINGS: [1.0900, 1.0895]
POS → ticket: 123456 | buy: 1.0900 | tp: 1.0905
POS → ticket: 123457 | buy: 1.0895 | tp: 1.0900
DECISION → BUY
```

## Troubleshooting

### Connection Issues
- Verify MT5 login credentials in `.env`
- Ensure MetaTrader 5 platform is running
- Check internet connection
- Bot auto-reconnects every check cycle

### No Trades Executing
- Confirm market is open (check `MARKET CLOSED` in logs)
- Verify `SYMBOL` is correct for your account
- Check account has sufficient balance for `LOT_SIZE`
- Ensure account allows automated trading (review MT5 settings)

### High Slippage
- Increase `deviation` parameter in `trader.py` for market orders
- Trade during high-liquidity hours
- Reduce `LOT_SIZE` to prioritize execution speed

## Risk Disclaimer

⚠️ **This is a fully automated trading system.** Before using:

- **Start with small position sizes** to test strategy
- **Monitor trades regularly** during initial deployment
- **Understand grid trading risks**: positions can accumulate quickly in trending markets
- **Set account limits** in MetaTrader 5
- **This tool is provided AS-IS** with no guarantees of profitability or safety

## Development

### Adding New Features

The codebase is modular:
- Modify `strategy.py` to change trading logic
- Adjust `mt5_connector.py` for different data sources
- Update `trader.py` to customize order parameters

### Testing
Before live trading:
1. Test on a demo account first
2. Use backtesting tools within MetaTrader 5
3. Monitor one session manually before enabling auto-restart

## License

This project is provided for educational and personal use.

## Support

For issues or questions:
- Check the logs in `logs/runner.log`
- Review MetaTrader 5 terminal logs
- Verify all environment variables are set correctly
