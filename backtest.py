#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest — Système XAU/USD (PRD §9)
====================================
Rejoue la logique DÉTERMINISTE du bot sur l'historique et mesure l'edge,
NET DE COÛTS (§9.3), avec un split train / out-of-sample (§9.4).

Réutilise les MÊMES fonctions que `bot_xauusd.py` (RSI, divergence, sweep,
score de confluence, sizing) → test et live restent cohérents.

⚠️  LIMITES HONNÊTES de cette v1 (à connaître avant d'y croire) :
    • Backtest MONO-TIMEFRAME : il teste le cœur technique sur UNE série
      (ex. H1). Le live utilise plusieurs UT ; une version multi-UT fidèle
      demande d'aligner D/H4/H1/M15 par horodatage (TODO).
    • Les VETOS macro (DXY/US10Y) et news NE SONT PAS inclus (il faudrait
      l'historique DXY/US10Y + calendrier). Ils ne font que RETIRER des
      trades en live → ce backtest teste donc le déclencheur technique seul.
    • SL/TP à distance FIXE (le live vise un SL structurel). Proxy de
      "niveau de session" = plus-haut/bas glissant.
    ⇒ C'est un SANITY-CHECK du cœur, pas une simulation courtier exacte.
      Calibrer puis étendre avant toute décision de capital réel.

Usage :
    python backtest.py --demo                 # données synthétiques (vérif moteur)
    python backtest.py --csv mon_histo.csv    # CSV: time,open,high,low,close[,volume]
    python backtest.py --oanda H1 --count 5000
"""
from __future__ import annotations
import os
import argparse
import datetime as dt

import pandas as pd
import numpy as np

# Mêmes briques que le bot (cohérence test/live)
from bot_xauusd import compute_rsi, detect_divergence, detect_sweep, confluence_score

# ─────────────── Paramètres (À CALIBRER puis valider en out-of-sample, §9.4) ───────────────
SL_USD          = 5.0    # distance SL fixe ($) = 1 unité de risque (R)
RR              = 2.0    # objectif = 2R (PRD §8, R:R ≥ 1:2)
COST_USD        = 0.50   # coûts round-trip $ (spread+commission+slippage, §9.3) — À CALIBRER
MIN_SCORE       = 45     # seuil d'entrée sur le score partiel (max 75 : macro/news exclus)
SWEEP_LOOKBACK  = 24     # bougies pour le "niveau de session" proxy (offline)
WARMUP          = 60     # bougies ignorées au départ (indicateurs pas mûrs)
TRAIN_FRAC      = 0.70   # split train / out-of-sample (§9.4)


# ─────────────── Construction des signaux (réutilise le score du bot) ───────────────
def build_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = compute_rsi(df["close"])
    ema50 = df["close"].ewm(span=50, adjust=False).mean()
    prior_high = df["high"].rolling(SWEEP_LOOKBACK).max().shift(1)
    prior_low = df["low"].rolling(SWEEP_LOOKBACK).min().shift(1)

    dirs, scores = [], []
    for i in range(len(df)):
        if i < WARMUP:
            dirs.append(None); scores.append(0); continue
        c = df["close"].iat[i]; r = df["rsi"].iat[i]
        if c > ema50.iat[i] and r >= 50:
            trend = "up"
        elif c < ema50.iat[i] and r <= 50:
            trend = "down"
        else:
            trend = "flat"
        sub = df.iloc[:i + 1]
        div = detect_divergence(sub)
        ph = None if pd.isna(prior_high.iat[i]) else float(prior_high.iat[i])
        pl = None if pd.isna(prior_low.iat[i]) else float(prior_low.iat[i])
        sweep = detect_sweep(sub, ph, pl)
        structure_ok = False
        if ph is not None and pl is not None:
            band = max((ph - pl) * 0.10, 0.5)
            structure_ok = abs(c - ph) <= band or abs(c - pl) <= band
        cands = ["long", "short"] if trend == "flat" else (["long"] if trend == "up" else ["short"])
        # macro={"ok":False} ⇒ composante macro NON attribuée ; news_active=False (voir limites)
        best = max(cands, key=lambda d: confluence_score(d, {"ok": False}, trend, div, sweep, structure_ok, False))
        sc = confluence_score(best, {"ok": False}, trend, div, sweep, structure_ok, False)
        dirs.append(best); scores.append(sc)

    df["dir"] = dirs
    df["score"] = scores
    return df


# ─────────────── Simulation des trades (SL/TP en R, nets de coûts) ───────────────
def simulate(df: pd.DataFrame) -> pd.DataFrame:
    trades = []
    cost_R = COST_USD / SL_USD
    n = len(df)
    i = WARMUP
    while i < n - 1:
        d, sc = df["dir"].iat[i], df["score"].iat[i]
        if d is None or sc < MIN_SCORE:
            i += 1; continue
        E = df["close"].iat[i]
        sl = E - SL_USD if d == "long" else E + SL_USD
        tp = E + RR * SL_USD if d == "long" else E - RR * SL_USD
        outcome, exit_price, jexit = None, None, None
        for j in range(i + 1, n):
            hi, lo = df["high"].iat[j], df["low"].iat[j]
            if d == "long":
                if lo <= sl:  outcome, exit_price, jexit = "loss", sl, j; break   # SL d'abord (prudent)
                if hi >= tp:  outcome, exit_price, jexit = "win", tp, j; break
            else:
                if hi >= sl:  outcome, exit_price, jexit = "loss", sl, j; break
                if lo <= tp:  outcome, exit_price, jexit = "win", tp, j; break
        if outcome is None:  # non résolu en fin d'historique
            jexit = n - 1; exit_price = df["close"].iat[jexit]; outcome = "expired"
            R_gross = ((exit_price - E) if d == "long" else (E - exit_price)) / SL_USD
        else:
            R_gross = RR if outcome == "win" else -1.0
        trades.append({"entry_time": df.index[i], "exit_time": df.index[jexit], "dir": d,
                       "score": int(sc), "entry": round(E, 2), "exit": round(float(exit_price), 2),
                       "outcome": outcome, "R_gross": round(R_gross, 3),
                       "R_net": round(R_gross - cost_R, 3), "bars": jexit - i})
        i = jexit + 1  # une position à la fois
    return pd.DataFrame(trades)


# ─────────────── Métriques (§9.2, nettes de coûts) ───────────────
def metrics(tr: pd.DataFrame) -> dict:
    if tr is None or tr.empty:
        return {"trades": 0}
    R = tr["R_net"]
    wins, losses = tr[R > 0], tr[R <= 0]
    gwin, gloss = wins["R_net"].sum(), -losses["R_net"].sum()
    eq = R.cumsum()
    dd = float((eq - eq.cummax()).min()) if len(eq) else 0.0
    return {"trades": int(len(tr)),
            "win%": round(100 * len(wins) / len(tr), 1),
            "expectancy_R": round(float(R.mean()), 3),
            "avg_win_R": round(float(wins["R_net"].mean()), 3) if len(wins) else 0.0,
            "avg_loss_R": round(float(losses["R_net"].mean()), 3) if len(losses) else 0.0,
            "profit_factor": (round(gwin / gloss, 2) if gloss > 0 else float("inf")),
            "total_R": round(float(R.sum()), 2),
            "max_dd_R": round(dd, 2)}


def run_backtest(df: pd.DataFrame):
    df = build_signals(df)
    trades = simulate(df)
    split_time = df.index[int(len(df) * TRAIN_FRAC)]
    res = {"all": metrics(trades)}
    if not trades.empty:
        res["train"] = metrics(trades[trades["entry_time"] < split_time])
        res["oos"] = metrics(trades[trades["entry_time"] >= split_time])
    return trades, res


# ─────────────── Sorties ───────────────
def print_report(res: dict) -> None:
    order = ["trades", "win%", "expectancy_R", "avg_win_R", "avg_loss_R",
             "profit_factor", "total_R", "max_dd_R"]
    cols = [c for c in ("all", "train", "oos") if c in res]
    w = 16
    print("\n" + "métrique".ljust(w) + "".join(c.upper().rjust(12) for c in cols))
    print("-" * (w + 12 * len(cols)))
    for k in order:
        line = k.ljust(w)
        for c in cols:
            v = res[c].get(k, "")
            line += (f"{v}").rjust(12)
        print(line)
    print("\nRappel : expectancy_R > 0 NET est nécessaire (pas suffisant). "
          "Compare TRAIN vs OOS : si l'edge disparaît en OOS → sur-apprentissage (§9.4).")


def save_equity_png(trades: pd.DataFrame, path: str = "backtest_equity.png") -> bool:
    if trades is None or trades.empty:
        return False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        eq = trades["R_net"].cumsum()
        plt.figure(figsize=(9, 4))
        plt.plot(eq.values)
        plt.axhline(0, color="grey", lw=0.8, ls="--")
        plt.title("Courbe d'équité — R cumulés (net de coûts)")
        plt.xlabel("trade #"); plt.ylabel("R cumulés"); plt.grid(True, alpha=0.3)
        plt.tight_layout(); plt.savefig(path, dpi=120); plt.close()
        return True
    except Exception as e:
        print("Equity PNG non généré:", e)
        return False


# ─────────────── Chargement des données ───────────────
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    tcol = next((c for c in df.columns if c.lower() in ("time", "date", "datetime", "timestamp")), df.columns[0])
    df[tcol] = pd.to_datetime(df[tcol], utc=True)
    df = df.set_index(tcol).sort_index()
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close"] + (["volume"] if "volume" in df.columns else [])]


def fetch_history_oanda(gran: str = "H1", count: int = 5000) -> pd.DataFrame:
    """Récupère jusqu'à 5000 bougies OANDA (démo). TODO: pagination pour plus long."""
    from oandapyV20 import API
    from oandapyV20.endpoints.instruments import InstrumentsCandles
    client = API(access_token=os.environ["OANDA_TOKEN"], environment=os.environ.get("OANDA_ENV", "practice"))
    req = InstrumentsCandles(instrument="XAU_USD",
                             params={"granularity": gran, "count": min(count, 5000), "price": "M"})
    client.request(req)
    rows = [{"time": pd.to_datetime(c["time"]), "open": float(c["mid"]["o"]), "high": float(c["mid"]["h"]),
             "low": float(c["mid"]["l"]), "close": float(c["mid"]["c"]), "volume": int(c["volume"])}
            for c in req.response["candles"] if c["complete"]]
    return pd.DataFrame(rows).set_index("time")


def _demo_data(n: int = 1500, seed: int = 7) -> pd.DataFrame:
    """Marche aléatoire avec légère dérive (pour VÉRIFIER LE MOTEUR, pas la stratégie)."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC")
    steps = rng.normal(0, 1.0, n) + np.sin(np.linspace(0, 30, n)) * 0.3
    close = pd.Series(2400 + np.cumsum(steps), index=idx)
    return pd.DataFrame({"open": close.shift(1).fillna(close.iloc[0]),
                         "high": close + rng.uniform(0.3, 2.0, n),
                         "low": close - rng.uniform(0.3, 2.0, n),
                         "close": close, "volume": rng.integers(100, 500, n)}, index=idx)


def main() -> None:
    ap = argparse.ArgumentParser(description="Backtest XAU/USD (PRD §9)")
    ap.add_argument("--demo", action="store_true", help="données synthétiques (vérif moteur)")
    ap.add_argument("--csv", help="fichier CSV: time,open,high,low,close[,volume]")
    ap.add_argument("--oanda", metavar="GRAN", help="granularité OANDA (ex. H1)")
    ap.add_argument("--count", type=int, default=5000)
    a = ap.parse_args()

    if a.demo:
        df = _demo_data()
        print("Mode DÉMO (données synthétiques — sert à valider le moteur, pas la stratégie).")
    elif a.csv:
        df = load_csv(a.csv)
    elif a.oanda:
        df = fetch_history_oanda(a.oanda, a.count)
    else:
        ap.error("choisis --demo, --csv <fichier> ou --oanda <granularité>")

    print(f"{len(df)} bougies  |  {df.index[0]} → {df.index[-1]}")
    trades, res = run_backtest(df)
    print_report(res)
    if not trades.empty:
        trades.to_csv("backtest_trades.csv", index=False)
        ok = save_equity_png(trades)
        print(f"\n→ {len(trades)} trades écrits dans backtest_trades.csv"
              + ("  |  courbe: backtest_equity.png" if ok else ""))
    else:
        print("\nAucun trade généré (seuil trop haut ou historique trop court).")


if __name__ == "__main__":
    main()
