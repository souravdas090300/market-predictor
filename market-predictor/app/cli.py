"""Quick terminal check:  python -m app.cli AAPL BTC-USD EURUSD=X   (no args = whole watchlist)"""
import argparse

from . import config, predict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbols", nargs="*")
    ap.add_argument("--no-news", action="store_true")
    ap.add_argument("--retrain", action="store_true")
    args = ap.parse_args()

    symbols = args.symbols or [a["symbol"] for a in config.WATCHLIST]
    print(f"{'symbol':<10} {'signal':<8} {'P(up)':>6} {'news':>6}  {'oos acc':>8} {'baseline':>9}")
    for s in symbols:
        try:
            r = predict.get_signal(s, use_news=not args.no_news, retrain=args.retrain)
            b = r["backtest"]
            print(f"{s:<10} {r['signal']:<8} {r['probability_up']:>6.2f} "
                  f"{r['sentiment']['score']:>+6.2f}  {b['accuracy']:>8.1%} {b['baseline_accuracy']:>9.1%}")
        except Exception as e:
            print(f"{s:<10} error: {e}")


if __name__ == "__main__":
    main()


def history_cmd(symbol: str = None):
    """Show signal history for a symbol."""
    from . import history as hist
    entries = hist.get_history(symbol, days=90)
    if not entries:
        print(f"No history found for {symbol or 'all symbols'}")
        return
    for e in entries[-10:]:
        print(f"{e['timestamp'][:10]} {e['symbol']:<10} {e['signal']:<8} {e['probability_up']:.2f}")


def portfolio_cmd(symbols: str):
    """Show aggregate metrics for a list of symbols (comma-separated)."""
    from . import metrics
    syms = [s.strip().upper() for s in symbols.split(",")]
    m = metrics.portfolio_metrics(syms)
    print(f"Portfolio: {m['symbols']} symbols, {m['total_signals']} total signals")
    print(f"Bullish: {m['bullish_count']}, Bearish: {m['bearish_count']}, Neutral: {m['neutral_count']}")
    print(f"Avg probability: {m['avg_probability']:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", help="Command")
    
    sp_cli = sp.add_parser("cli", help="Auto signals (default)")
    sp_cli.add_argument("symbols", nargs="*")
    sp_cli.add_argument("--no-news", action="store_true")
    
    sp_hist = sp.add_parser("history", help="Signal history")
    sp_hist.add_argument("--symbol")
    
    sp_port = sp.add_parser("portfolio", help="Portfolio metrics")
    sp_port.add_argument("symbols", help="Comma-separated symbols")
    
    args = ap.parse_args()
    
    if args.cmd == "history":
        history_cmd(args.symbol)
    elif args.cmd == "portfolio":
        portfolio_cmd(args.symbols)
    else:
        main()
