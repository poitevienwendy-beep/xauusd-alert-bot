#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Starter GRATUIT — Alertes XAU/USD à la clôture de bougie
=========================================================
Aligné sur le PRD v2.2 (01 Projets/Trading XAU-USD).

⚠️  À LIRE — ceci est un SQUELETTE de départ, PAS un bot rentable :
    • ALERTE uniquement — n'exécute AUCUN ordre, ne déplace aucun argent.
    • La détection des motifs (divergence / sweep) et le score sont des
      implémentations SIMPLIFIÉES, à CALIBRER puis à BACKTESTER (PRD §9)
      avant tout capital réel.
    • Données de démo OANDA : gratuites et en temps réel, mais non garanties
      au tick près.
    • Respecte le PRD : données manquantes → NEUTRE (§3.3) ; tous les
      calculs sont faits par CODE, jamais « à l'œil » (§3.4).

Stack 100% gratuit :
    OANDA démo (données)  +  Forex Factory (calendrier news)  +  mplfinance (PNG)
    +  Telegram (push)  +  Oracle Cloud (24/7)

Config via variables d'environnement — voir .env.example.
Les imports externes (oandapyV20, mplfinance, yfinance, requests) sont chargés
à la demande, pour que --selftest tourne avec seulement pandas + numpy.
"""
from __future__ import annotations
import os
import io
import csv
import json
import time
import datetime as dt

import pandas as pd
import numpy as np

# ─────────────────────────── PARAMÈTRES (à calibrer PUIS backtester) ───────────────────────────
INSTRUMENT          = "XAU_USD"
RSI_PERIOD          = 14
DIV_WINDOW_N        = 20        # §3.5 — fenêtre de détection de divergence
SWEEP_BUFFER_X      = 0.50      # §3.5 — dépassement min. de l'extrême de session ($) — À CALIBRER
SWEEP_REINT_M       = 3         # §3.5 — nb de bougies pour la réintégration
SCORE_WEIGHTS       = {"macro": 25, "htf": 25, "rsi_div": 20, "sweep": 20, "structure": 10}  # §7.2
SCORE_ACTIONABLE    = 70        # §7.2 — seuil d'alerte
POINT_VALUE_PER_LOT = 100       # XAU/USD : 1 lot = 100 oz ⇒ 1 $ = 100 $/lot (§8.3)
MONITORED_TFS       = ["M5", "M15", "H1", "H4", "D"]
GRAN_SECONDS        = {"M5": 300, "M15": 900, "H1": 3600, "H4": 14400, "D": 86400}

# ─── Calendrier news (Forex Factory via Faireconomy — gratuit, sans clé) ───
NEWS_URL            = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
NEWS_CACHE          = "calendar.json"   # cache local — téléchargé ~1×/semaine
NEWS_MAX_AGE_DAYS   = 6                  # re-télécharge SEULEMENT si le cache est plus vieux
NEWS_CURRENCIES     = {"USD"}            # devises qui déclenchent le veto (l'or = USD)
NEWS_IMPACTS        = {"High"}           # niveaux d'impact retenus
NEWS_WINDOW_MIN     = 30                 # ±30 min autour de l'annonce (PRD §2A)


# ══════════════════════════ CALCULS DÉTERMINISTES (PRD §3.4) ══════════════════════════

def compute_rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """RSI de Wilder (lissage exponentiel alpha = 1/period)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


def detect_divergence(df: pd.DataFrame, n: int = DIV_WINDOW_N) -> str:
    """Divergence RSI (PRD §3.5), approximée par 2 demi-fenêtres.
    Retourne 'bearish' / 'bullish' / 'none'.
    TODO prod : remplacer par une vraie détection de swings (pivots)."""
    if len(df) < n:
        return "none"
    w = df.tail(n)
    half = n // 2
    prev, recent = w.iloc[:half], w.iloc[half:]
    # Baissière : prix fait un plus-haut plus haut, RSI fait un plus-haut plus bas
    if recent["high"].max() > prev["high"].max() and recent["rsi"].max() < prev["rsi"].max():
        return "bearish"
    # Haussière : prix fait un plus-bas plus bas, RSI fait un plus-bas plus haut
    if recent["low"].min() < prev["low"].min() and recent["rsi"].min() > prev["rsi"].min():
        return "bullish"
    return "none"


def detect_sweep(df: pd.DataFrame, session_high, session_low,
                 buffer_x: float = SWEEP_BUFFER_X, m: int = SWEEP_REINT_M) -> str:
    """Sweep de liquidité + réintégration (PRD §3.5).
    'bearish' = sweep des hauts puis clôture repassée dessous ;
    'bullish' = sweep des bas puis clôture repassée dessus ; sinon 'none'."""
    if len(df) < m or session_high is None or session_low is None:
        return "none"
    last = df.tail(m)
    if (last["high"] > session_high + buffer_x).any() and last["close"].iloc[-1] < session_high:
        return "bearish"
    if (last["low"] < session_low - buffer_x).any() and last["close"].iloc[-1] > session_low:
        return "bullish"
    return "none"


def htf_trend(df: pd.DataFrame) -> str:
    """Tendance HTF simple : EMA(50) + ligne RSI 50. 'up' / 'down' / 'flat'."""
    if len(df) < 50:
        return "flat"
    ema = df["close"].ewm(span=50, adjust=False).mean().iloc[-1]
    price = df["close"].iloc[-1]
    rsi = df["rsi"].iloc[-1]
    if price > ema and rsi >= 50:
        return "up"
    if price < ema and rsi <= 50:
        return "down"
    return "flat"


def position_size(capital: float, risk_pct: float, sl_distance: float) -> float:
    """Taille en lots (PRD §8.3). Ex. 10 000 $ · 1% · SL 5 $ ⇒ 0,20 lot."""
    if sl_distance <= 0:
        return 0.0
    risk_amount = capital * (risk_pct / 100.0)
    return round(risk_amount / (sl_distance * POINT_VALUE_PER_LOT), 2)


def breakeven_winrate(r: float) -> float:
    """Win% d'équilibre pour un R:R donné (PRD §8.1) : 1/(1+R)."""
    return 1.0 / (1.0 + r)


# ══════════════════════════ CALENDRIER NEWS (PRD §2A / §7.1 veto) ══════════════════════════
# Principe : on TÉLÉCHARGE la liste hebdo ~1×/semaine (elle est fixe), puis on la
# CONSULTE en local à chaque bougie. Télécharger ≠ consulter (voir docstring du bot).

def _download_calendar(path: str = NEWS_CACHE) -> bool:
    """Télécharge le calendrier hebdo Forex Factory (Faireconomy) → cache local.
    À n'appeler qu'~1×/semaine (sinon Faireconomy bloque). True si succès."""
    import requests
    try:
        r = requests.get(NEWS_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        r.raise_for_status()
        with open(path, "w", encoding="utf-8") as f:
            f.write(r.text)
        print("News: calendrier hebdo téléchargé.")
        return True
    except Exception as e:
        print("News: échec du téléchargement:", e)
        return False


def _refresh_calendar_if_stale(path: str = NEWS_CACHE, max_age_days: int = NEWS_MAX_AGE_DAYS) -> None:
    """Re-télécharge SEULEMENT si le cache manque ou dépasse max_age_days.
    ⇒ en pratique 1 téléchargement/semaine, lecture locale le reste du temps."""
    fresh = os.path.exists(path) and (time.time() - os.path.getmtime(path) < max_age_days * 86400)
    if not fresh:
        _download_calendar(path)


def _parse_events(raw_text: str) -> list:
    """Transforme le JSON FF en liste {dt(UTC), currency, impact, title}."""
    events = []
    for e in json.loads(raw_text):
        cur = e.get("country") or e.get("currency")      # FF met le code devise dans 'country'
        imp = (e.get("impact") or "").title()
        ts = e.get("date") or e.get("time")
        if not (cur and ts):
            continue
        try:
            dtv = pd.to_datetime(ts, utc=True).to_pydatetime()
        except Exception:
            continue
        events.append({"dt": dtv, "currency": cur, "impact": imp, "title": e.get("title", "")})
    return events


def load_calendar_events(path: str = NEWS_CACHE):
    """Charge les événements depuis le cache local. Retourne (events, ok)."""
    if not os.path.exists(path):
        return [], False
    try:
        with open(path, encoding="utf-8") as f:
            return _parse_events(f.read()), True
    except Exception as e:
        print("News: cache illisible:", e)
        return [], False


def is_in_news_window(events: list, now_utc: dt.datetime, minutes: int = NEWS_WINDOW_MIN) -> bool:
    """PUR (testable) : True si now est à ±minutes d'un événement retenu (devise + impact)."""
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=dt.timezone.utc)
    win = dt.timedelta(minutes=minutes)
    for e in events:
        if e["currency"] in NEWS_CURRENCIES and e["impact"] in NEWS_IMPACTS:
            if abs(e["dt"] - now_utc) <= win:
                return True
    return False


def in_news_window(now_utc: dt.datetime | None = None) -> bool:
    """Veto news (PRD §2A). Rafraîchit le cache ~1×/semaine, puis lit en local.
    Si le calendrier est indisponible : fail-open (False) + avertissement."""
    now_utc = now_utc or dt.datetime.now(dt.timezone.utc)
    _refresh_calendar_if_stale()
    events, ok = load_calendar_events()
    if not ok:
        print("News: calendrier indisponible → veto non appliqué (à vérifier manuellement).")
        return False
    return is_in_news_window(events, now_utc)


# ══════════════════════════ CONTEXTE MACRO (PRD §2A / §7.1 veto) ══════════════════════════

def macro_state() -> dict:
    """DXY & US10Y via yfinance (gratuit, journalier).
    Règle PRD : DXY↑ ET US10Y↑ ⇒ défavorable aux Longs sur l'or (et inversement)."""
    try:
        import yfinance as yf
        dxy = yf.download("DX-Y.NYB", period="5d", interval="1d", progress=False)["Close"].dropna()
        tnx = yf.download("^TNX", period="5d", interval="1d", progress=False)["Close"].dropna()
        dxy_up = bool(dxy.iloc[-1] > dxy.iloc[-2])
        tnx_up = bool(tnx.iloc[-1] > tnx.iloc[-2])
    except Exception:
        return {"ok": False}  # pas de données fiables → NEUTRE (§3.3)
    return {"ok": True, "dxy_up": dxy_up, "tnx_up": tnx_up,
            "veto_long": (dxy_up and tnx_up), "veto_short": (not dxy_up and not tnx_up)}


# ══════════════════════════ SCORE DE CONFLUENCE (PRD §7.2) ══════════════════════════

def confluence_score(direction: str, macro: dict, trend: str, div: str, sweep: str,
                     structure_ok: bool, news_active: bool = False) -> int:
    w = SCORE_WEIGHTS
    s = 0
    if macro.get("ok") and not macro.get(f"veto_{direction}", False) and not news_active:
        s += w["macro"]
    if (direction == "long" and trend == "up") or (direction == "short" and trend == "down"):
        s += w["htf"]
    want = "bullish" if direction == "long" else "bearish"
    if div == want:
        s += w["rsi_div"]
    if sweep == want:
        s += w["sweep"]
    if structure_ok:
        s += w["structure"]
    return s


# ══════════════════════════ SESSIONS ══════════════════════════

def current_session(now_utc: dt.datetime | None = None) -> str:
    """Session approximative par heure UTC (TODO : ajuster au DST)."""
    h = (now_utc or dt.datetime.utcnow()).hour
    if 0 <= h < 7:
        return "ASIE"
    if 7 <= h < 13:
        return "LONDRES"
    if 13 <= h < 21:
        return "NEW YORK"
    return "HORS-SESSION"


def previous_session_levels(intraday: pd.DataFrame):
    """Plus-haut / plus-bas de la SESSION précédente à partir de bougies intraday (ex. M15).
    Best-effort par fenêtres UTC fixes. TODO : gérer le DST et les week-ends."""
    if intraday is None or intraday.empty:
        return None, None
    df = intraday.copy()
    def block(h):
        if 0 <= h < 7:  return "ASIE"
        if 7 <= h < 13: return "LONDRES"
        return "NEW YORK"
    df["sess"] = [block(h) for h in df.index.hour]
    df["day"] = df.index.date
    df["key"] = df["day"].astype(str) + "-" + df["sess"]
    keys = list(dict.fromkeys(df["key"].tolist()))
    if len(keys) < 2:
        return float(df["high"].max()), float(df["low"].min())
    prev = df[df["key"] == keys[-2]]
    return float(prev["high"].max()), float(prev["low"].min())


# ══════════════════════════ ENTRÉES / SORTIES ══════════════════════════

def fetch_candles(granularity: str, count: int = 200) -> pd.DataFrame:
    """Bougies CLÔTURÉES depuis OANDA (démo). Requiert OANDA_TOKEN."""
    from oandapyV20 import API
    from oandapyV20.endpoints.instruments import InstrumentsCandles
    client = API(access_token=os.environ["OANDA_TOKEN"],
                 environment=os.environ.get("OANDA_ENV", "practice"))
    req = InstrumentsCandles(instrument=INSTRUMENT,
                             params={"granularity": granularity, "count": count, "price": "M"})
    client.request(req)
    rows = []
    for c in req.response["candles"]:
        if not c["complete"]:
            continue  # §3.3 : on ignore la bougie en cours
        m = c["mid"]
        rows.append({"time": pd.to_datetime(c["time"]),
                     "open": float(m["o"]), "high": float(m["h"]),
                     "low": float(m["l"]), "close": float(m["c"]),
                     "volume": int(c["volume"])})
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).set_index("time")
    df["rsi"] = compute_rsi(df["close"])
    return df


def render_chart(df: pd.DataFrame, tf: str, levels: dict) -> bytes:
    """Redessine bougies + panneau RSI en PNG (mplfinance). Aucun screenshot de site."""
    import mplfinance as mpf
    d = df.tail(120).rename(columns={"open": "Open", "high": "High", "low": "Low",
                                     "close": "Close", "volume": "Volume"})
    apds = [mpf.make_addplot(d["rsi"], panel=1, ylabel="RSI")]
    hl = [v for v in levels.values() if v]
    buf = io.BytesIO()
    mpf.plot(d[["Open", "High", "Low", "Close", "Volume"]], type="candle", volume=False,
             addplot=apds, style="charles", title=f"{INSTRUMENT} {tf}",
             hlines=dict(hlines=hl, linestyle="--", linewidths=0.7) if hl else None,
             savefig=dict(fname=buf, format="png", dpi=120))
    buf.seek(0)
    return buf.read()


def send_telegram(text: str, png: bytes | None = None) -> None:
    import requests
    tok = os.environ["TELEGRAM_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    if png:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendPhoto",
                          data={"chat_id": chat, "caption": text[:1024]},
                          files={"photo": ("chart.png", png)}, timeout=30)
    else:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                          data={"chat_id": chat, "text": text}, timeout=30)
    r.raise_for_status()  # sans ça, un token/chat_id invalide échoue en silence (alerte jamais reçue, rien dans les logs)


def journal(row: dict, path: str = "journal.csv") -> None:
    """Journal de trades (PRD §9.5)."""
    cols = ["date", "session", "tf", "direction", "score", "entry", "sl", "tp",
            "r_planned", "macro", "news", "div", "sweep", "note", "disconfirm"]
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in cols})


# ══════════════════════════ ÉVALUATION & FORMAT DE SORTIE (PRD §10) ══════════════════════════

def evaluate() -> dict:
    """Lecture contextuelle complète selon la hiérarchie du PRD (§7.1).
    Biais NEUTRE si données insuffisantes (§3.3) ou fenêtre news active (§2A)."""
    dfs = {tf: fetch_candles(tf) for tf in ("D", "H4", "H1", "M15")}
    if any(dfs[tf].empty for tf in ("H4", "H1", "M15")):
        return {"bias": "NEUTRE", "reason": "DONNÉES INSUFFISANTES (§3.3)", "score": 0}

    trend = htf_trend(dfs["H4"])
    div = detect_divergence(dfs["H1"])
    sess_hi, sess_lo = previous_session_levels(dfs["M15"])
    sweep = detect_sweep(dfs["M15"], sess_hi, sess_lo)
    macro = macro_state()
    news_active = in_news_window()          # 1 seul appel (refresh hebdo + lecture cache)
    price = float(dfs["H1"]["close"].iloc[-1])

    # Structure : prix proche d'un extrême de session (heuristique — TODO calibrer)
    structure_ok = False
    if sess_hi and sess_lo:
        band = max((sess_hi - sess_lo) * 0.10, 0.5)
        structure_ok = (abs(price - sess_hi) <= band) or (abs(price - sess_lo) <= band)

    candidates = ["long", "short"] if trend == "flat" else (["long"] if trend == "up" else ["short"])
    best = max(candidates, key=lambda d: confluence_score(d, macro, trend, div, sweep,
                                                          structure_ok, news_active))
    score = confluence_score(best, macro, trend, div, sweep, structure_ok, news_active)

    if best == "long":
        sl = (sess_lo - SWEEP_BUFFER_X) if sess_lo else price - 5
        risk = max(price - sl, 0.01); tp = price + 2 * risk
    else:
        sl = (sess_hi + SWEEP_BUFFER_X) if sess_hi else price + 5
        risk = max(sl - price, 0.01); tp = price - 2 * risk

    # VETO (§7.1) : macro défavorable OU fenêtre de news active
    veto = (macro.get("ok") and macro.get(f"veto_{best}", False)) or news_active
    bias = "NEUTRE"
    if not veto and score >= SCORE_ACTIONABLE:
        bias = "HAUSSIER" if best == "long" else "BAISSIER"

    return {"bias": bias, "direction": best, "score": score, "trend": trend, "div": div,
            "sweep": sweep, "macro": macro, "news": news_active, "session": current_session(),
            "price": price, "sl": round(sl, 2), "tp": round(tp, 2), "risk": round(risk, 2),
            "sess_hi": sess_hi, "sess_lo": sess_lo, "structure_ok": structure_ok,
            "veto": bool(veto)}


def build_report(rep: dict, trigger: str) -> str:
    """Format de sortie strict du PRD §10 (version condensée pour Telegram)."""
    if rep["bias"] == "NEUTRE" and rep.get("reason"):
        return f"🏛️ XAU/USD [{trigger}] — NEUTRE\n{rep['reason']}"
    m = rep["macro"]
    macro_txt = ("Défavorable" if (m.get("ok") and (m.get("veto_long") or m.get("veto_short")))
                 else ("Favorable/Neutre" if m.get("ok") else "Inconnu→NEUTRE"))
    news_txt = "⚠️ fenêtre active (VETO)" if rep.get("news") else "ok"
    r = rep["risk"]; rr = 2.0
    lots = position_size(float(os.environ.get("CAPITAL", 10000)),
                         float(os.environ.get("RISK_PCT", 1.0)), r)
    return (
        f"🏛️ BIAIS : {rep['bias']}  |  Score {rep['score']}/100  |  déclencheur {trigger}\n"
        f"Session : {rep['session']}  |  Macro DXY/US10Y : {macro_txt}"
        f"{'  (VETO)' if (m.get('ok') and m.get('veto_'+rep['direction'])) else ''}\n"
        f"News : {news_txt}\n"
        f"Tendance HTF(4h) : {rep['trend']}  |  Divergence(1h) : {rep['div']}  |  "
        f"Sweep(15m) : {rep['sweep']}\n"
        f"— Plan {rep['direction'].upper()} —\n"
        f"Entrée ≈ {rep['price']}  |  SL {rep['sl']}  |  TP {rep['tp']}  (R:R≈{rr:g})\n"
        f"Taille ≈ {lots} lot  |  Win% requis ≈ {breakeven_winrate(rr)*100:.1f}%\n"
        f"🔎 Invalidation : clôture au-delà du SL. (Alerte — pas d'ordre auto.)"
    )


# ══════════════════════════ ORCHESTRATION ══════════════════════════

def run_once(trigger: str) -> None:
    rep = evaluate()
    text = build_report(rep, trigger)
    if rep["bias"] != "NEUTRE":
        png = None
        try:
            df_h1 = fetch_candles("H1")
            png = render_chart(df_h1, "H1",
                               {"SL": rep.get("sl"), "TP": rep.get("tp"),
                                "hi": rep.get("sess_hi"), "lo": rep.get("sess_lo")})
        except Exception as e:  # le graphique ne doit jamais bloquer l'alerte
            text += f"\n(graphique indisponible : {e})"
        send_telegram(text, png)
        journal({"date": dt.datetime.utcnow().isoformat(timespec="minutes"),
                 "session": rep["session"], "tf": trigger, "direction": rep["direction"],
                 "score": rep["score"], "entry": rep["price"], "sl": rep["sl"], "tp": rep["tp"],
                 "r_planned": 2, "macro": rep["macro"].get("ok"), "news": rep.get("news"),
                 "div": rep["div"], "sweep": rep["sweep"], "note": "auto-alert",
                 "disconfirm": "clôture au-delà du SL"})
    else:
        print(f"[{dt.datetime.utcnow():%H:%M}] NEUTRE ({trigger}) — pas d'alerte.")


def seconds_to_next(gran_s: int) -> float:
    return gran_s - (time.time() % gran_s)


def tick() -> None:
    """Vérifie les UT en clôture MAINTENANT et alerte si besoin (un seul passage).
    Utilisé par la boucle main() (VM/systemd) ET par le mode --once (GitHub Actions,
    où le scheduler externe rappelle le script toutes les ~5 min au lieu d'une boucle)."""
    ts = int(time.time())
    due = [tf for tf in MONITORED_TFS if ts % GRAN_SECONDS[tf] < 300]
    if due:
        try:
            run_once(",".join(due))
        except Exception as e:
            print("Erreur run_once:", e)
    else:
        print(f"[{dt.datetime.utcnow():%H:%M}] Rien à évaluer (aucune UT en clôture).")


def main() -> None:
    print("Bot XAU/USD démarré (alerte seulement). Ctrl-C pour arrêter.")
    while True:
        time.sleep(seconds_to_next(300) + 5)  # se caler sur la clôture des 5 min
        tick()


# ══════════════════════════ TEST TELEGRAM (avec credentials, sans données marché) ══════════════════════════

def _test_telegram() -> None:
    """Envoie un message de confirmation unique — vérifie juste que TELEGRAM_TOKEN/CHAT_ID
    sont valides, sans attendre un vrai signal actionnable (qui peut rester NEUTRE longtemps)."""
    send_telegram("✅ Test bot XAU/USD — connexion Telegram OK.")
    print("Message de test envoyé — vérifie ton Telegram.")


# ══════════════════════════ AUTOTEST (sans credentials ni réseau) ══════════════════════════

def _selftest() -> None:
    """Teste les fonctions déterministes sur données synthétiques (aucun réseau)."""
    rng = np.random.default_rng(42)
    n = 120
    idx = pd.date_range("2026-01-01", periods=n, freq="15min", tz="UTC")
    close = pd.Series(2400 + np.cumsum(rng.normal(0, 1.2, n)), index=idx)
    df = pd.DataFrame({"open": close.shift(1).fillna(close.iloc[0]),
                       "high": close + rng.uniform(0.2, 1.5, n),
                       "low": close - rng.uniform(0.2, 1.5, n),
                       "close": close, "volume": rng.integers(100, 500, n)}, index=idx)
    df["rsi"] = compute_rsi(df["close"])
    assert df["rsi"].between(0, 100).all(), "RSI hors bornes"
    div = detect_divergence(df)
    hi, lo = previous_session_levels(df)
    sweep = detect_sweep(df, hi, lo)
    trend = htf_trend(df)
    macro = {"ok": True, "veto_long": False, "veto_short": False}
    sc_long = confluence_score("long", macro, trend, div, sweep, True, news_active=False)
    lots = position_size(10000, 1.0, 5.0)

    # Calendrier news — fonctions PURES, sans réseau
    now = dt.datetime(2026, 7, 29, 12, 30, tzinfo=dt.timezone.utc)
    ev = [{"dt": now + dt.timedelta(minutes=10), "currency": "USD", "impact": "High", "title": "CPI"},
          {"dt": now + dt.timedelta(hours=5),    "currency": "USD", "impact": "High", "title": "FOMC"}]
    in10 = is_in_news_window(ev, now)                                # CPI à +10 min → True
    out2h = is_in_news_window(ev, now + dt.timedelta(hours=2))       # loin → False
    sample = ('[{"title":"Non-Farm Payrolls","country":"USD",'
              '"date":"2026-07-31T12:30:00+00:00","impact":"High"}]')
    parsed = _parse_events(sample)

    print("✓ RSI dernier      :", round(float(df['rsi'].iloc[-1]), 2))
    print("✓ Divergence       :", div)
    print("✓ Session hi/lo    :", round(hi, 2), "/", round(lo, 2))
    print("✓ Sweep            :", sweep)
    print("✓ Tendance HTF     :", trend)
    print("✓ Score long       :", sc_long, "/100")
    print("✓ Sizing (10k,1%,5):", lots, "lot   (attendu 0.2)")
    print("✓ Breakeven 1:2    :", f"{breakeven_winrate(2)*100:.1f}%   (attendu 33.3%)")
    print("✓ News window      :", f"CPI+10min={in10} (True), +2h={out2h} (False)")
    print("✓ News parsing     :", parsed[0]["currency"], parsed[0]["impact"], "(USD High)")

    assert lots == 0.20 and abs(breakeven_winrate(2) - 1/3) < 1e-9
    assert in10 is True and out2h is False
    assert parsed and parsed[0]["currency"] == "USD" and parsed[0]["impact"] == "High"
    print("\nAutotest OK — fonctions déterministes + calendrier news valides.")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    elif "--test-telegram" in sys.argv:
        _test_telegram()
    elif "--once" in sys.argv:
        tick()  # un seul passage puis sortie — pour un scheduler externe (GitHub Actions)
    else:
        main()
