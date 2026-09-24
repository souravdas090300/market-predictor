"""Quick terminal check:  python -m scripts.cli AAPL BTC-USD EURUSD=X"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import config
from app.models import predict
from app.services import history as hist
from app.services import metrics


def run_signals(symbols, no_news=False, retrain=False):
    symbols = symbols or [a["symbol"] for a in config.WATCHLIST]
    print(f"{'symbol':<10} {'signal':<8} {'P(up)':>6} {'live':>10} {'news':>6}  {'oos acc':>8} {'baseline':>9}")
    for s in symbols:
        try:
            r = predict.get_signal(s, use_news=not no_news, retrain=retrain)
            b = r["backtest"]
            live = r.get("live") or {}
            live_s = f"{live['price']:.4f}" if live.get("price") is not None else "—"
            print(f"{s:<10} {r['signal']:<8} {r['probability_up']:>6.2f} {live_s:>10} "
                  f"{r['sentiment']['score']:>+6.2f}  {b['accuracy']:>8.1%} {b['baseline_accuracy']:>9.1%}")
        except Exception as e:
            print(f"{s:<10} error: {e}")


def history_cmd(symbol: str | None = None):
    entries = hist.get_history(symbol, days=90)
    if not entries:
        print(f"No history found for {symbol or 'all symbols'}")
        return
    for e in entries[-10:]:
        print(f"{e['timestamp'][:10]} {e['symbol']:<10} {e['signal']:<8} {e['probability_up']:.2f}")


def portfolio_cmd(symbols: str):
    syms = [s.strip().upper() for s in symbols.split(",")]
    m = metrics.portfolio_metrics(syms)
    print(f"Portfolio: {m['symbols']} symbols, {m.get('total_signals', 0)} total signals")
    if m.get("total_signals"):
        print(f"Bullish: {m['bullish_count']}, Bearish: {m['bearish_count']}, Neutral: {m['neutral_count']}")
        print(f"Avg probability: {m['avg_probability']:.2f}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")

    sp_sig = sp.add_parser("signal", help="Auto signals (default)")
    sp_sig.add_argument("symbols", nargs="*")
    sp_sig.add_argument("--no-news", action="store_true")
    sp_sig.add_argument("--retrain", action="store_true")

    sp_hist = sp.add_parser("history", help="Signal history")
    sp_hist.add_argument("--symbol")

    sp_port = sp.add_parser("portfolio", help="Portfolio metrics")
    sp_port.add_argument("symbols", help="Comma-separated symbols")

    args, rest = ap.parse_known_args()
    if args.cmd == "history":
        history_cmd(args.symbol)
    elif args.cmd == "portfolio":
        portfolio_cmd(args.symbols)
    elif args.cmd == "signal":
        run_signals(args.symbols, args.no_news, args.retrain)
    else:
        run_signals(rest, "--no-news" in rest, "--retrain" in rest)


if __name__ == "__main__":
    main()
