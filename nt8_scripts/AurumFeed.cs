// ============================================================
// AurumFeed.cs — NinjaScript Indicator for Aurum Grid Bot
//
// INSTALL STEPS:
//   1. In NinjaTrader 8: New > NinjaScript Editor
//   2. Right-click Indicators > New > paste this file
//   3. Compile (F5), then close editor
//   4. Add "AurumFeed" to a MGC chart (any timeframe)
//   5. Set AccountName to match your NT8 account (e.g. "Sim101")
//
// OUTPUT FILE: %USERPROFILE%\Documents\NinjaTrader 8\aurum_feed.json
// ============================================================

#region Using declarations
using System;
using System.IO;
using System.Linq;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class AurumFeed : Indicator
    {
        private string feedPath;
        private string feedTmp;

        [NinjaScriptProperty]
        [Display(Name = "Account Name", Order = 1, GroupName = "Aurum Settings")]
        public string AccountName { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name            = "AurumFeed";
                Description     = "Writes price and position data for Aurum grid bot";
                Calculate       = Calculate.OnEachTick;
                IsOverlay       = true;
                DisplayInDataBox = false;
                AccountName     = "Sim101";
            }
            else if (State == State.DataLoaded)
            {
                string nt8Docs = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                    "NinjaTrader 8"
                );
                feedPath = Path.Combine(nt8Docs, "aurum_feed.json");
                feedTmp  = feedPath + ".tmp";
            }
        }

        protected override void OnMarketData(MarketDataEventArgs e)
        {
            if (e.MarketDataType == MarketDataType.Ask
                || e.MarketDataType == MarketDataType.Bid)
            {
                WriteFeed();
            }
        }

        private void WriteFeed()
        {
            double ask = GetCurrentAsk();
            double bid = GetCurrentBid();
            if (ask <= 0 || bid <= 0) return;

            int netPosition = 0;
            try
            {
                lock (Account.All)
                {
                    // Match by Name OR DisplayName to handle both live and sim accounts
                    var acct = Account.All.FirstOrDefault(a =>
                        a.Name == AccountName || a.DisplayName == AccountName);
                    if (acct != null)
                    {
                        lock (acct.Positions)
                        {
                            // Match by MasterInstrument.Name (e.g. "MGC") to avoid
                            // expiry month format mismatches (JUN26 vs 06-26)
                            var pos = acct.Positions.FirstOrDefault(p =>
                                p.Instrument.MasterInstrument.Name
                                    == Instrument.MasterInstrument.Name
                                && p.MarketPosition == MarketPosition.Long);
                            if (pos != null)
                                netPosition = pos.Quantity;
                        }
                    }
                }
            }
            catch { }

            string json = string.Format(
                "{{\"ask\":{0},\"bid\":{1},\"net_position\":{2},"
                + "\"market_open\":{3},\"timestamp\":\"{4}\"}}",
                ask, bid, netPosition,
                "true",
                DateTime.UtcNow.ToString("o")
            );

            try
            {
                File.WriteAllText(feedTmp, json);
                if (File.Exists(feedPath)) File.Delete(feedPath);
                File.Move(feedTmp, feedPath);
            }
            catch { }
        }
    }
}
