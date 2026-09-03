#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Historique Nomade — outil portable de navigation et de nettoyage de l'historique
=================================================================================

Outil autonome (100 % bibliotheque standard Python 3, aucune installation)
concu pour etre copie sur une cle USB. Il :

  * detecte TOUS les navigateurs installes pour l'utilisateur courant
    (Chrome, Edge, Brave, Opera, Vivaldi, Chromium, Yandex, Firefox...) ;
  * lit l'historique de navigation de TOUS les profils / sessions de chaque
    navigateur ;
  * regroupe le tout dans une interface web locale (recherche, tri, filtres) ;
  * permet de NAVIGUER dans les liens et d'EN SUPPRIMER (une entree, une
    selection, ou tout l'historique d'un profil / de tous les profils).

IMPORTANT — usage responsable
-----------------------------
Cet outil lit uniquement les fichiers auxquels la session Windows/macOS/Linux
ouverte a deja acces : il n'y a ni contournement de mot de passe, ni elevation
de privileges, ni vol d'identifiants, ni envoi de donnees sur Internet. Tout
reste en local. Utilisez-le seulement sur des ordinateurs et des comptes qui
vous appartiennent ou que vous etes autorise a gerer.

Lancement rapide
----------------
    python3 history_tool.py            # ouvre l'interface web dans le navigateur
    python3 history_tool.py --cli      # mode terminal (liste)
    python3 history_tool.py --help     # toutes les options
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import platform
import shutil
import socket
import sqlite3
import sys
import tempfile
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from secrets import token_urlsafe
from urllib.parse import urlparse, parse_qs

APP_NAME = "Historique Nomade"
VERSION = "1.0.0"

# =====================================================================
#  Conversion des horodatages
# =====================================================================
# Chromium stocke le temps en microsecondes depuis le 1601-01-01 (epoque
# Windows) ; Firefox en microsecondes depuis le 1970-01-01 (epoque Unix).
_CHROME_EPOCH_OFFSET = 11644473600  # secondes entre 1601-01-01 et 1970-01-01


def chromium_to_unix(value) -> float:
    if not value:
        return 0.0
    return value / 1_000_000 - _CHROME_EPOCH_OFFSET


def firefox_to_unix(value) -> float:
    if not value:
        return 0.0
    return value / 1_000_000


# =====================================================================
#  Localisation des navigateurs et des profils
# =====================================================================
def _home() -> str:
    return os.path.expanduser("~")


def _chromium_bases() -> "dict[str, str]":
    """Retourne {nom du navigateur: dossier racine des profils} pour les
    navigateurs bases sur Chromium reellement presents sur la machine."""
    system = platform.system()
    home = _home()
    candidates: "dict[str, str]" = {}

    if system == "Windows":
        local = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
        roaming = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        candidates = {
            "Chrome": os.path.join(local, "Google", "Chrome", "User Data"),
            "Chrome Beta": os.path.join(local, "Google", "Chrome Beta", "User Data"),
            "Chrome Canary": os.path.join(local, "Google", "Chrome SxS", "User Data"),
            "Edge": os.path.join(local, "Microsoft", "Edge", "User Data"),
            "Brave": os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data"),
            "Vivaldi": os.path.join(local, "Vivaldi", "User Data"),
            "Chromium": os.path.join(local, "Chromium", "User Data"),
            "Yandex": os.path.join(local, "Yandex", "YandexBrowser", "User Data"),
            # Opera range son unique profil directement dans ces dossiers.
            "Opera": os.path.join(roaming, "Opera Software", "Opera Stable"),
            "Opera GX": os.path.join(roaming, "Opera Software", "Opera GX Stable"),
        }
    elif system == "Darwin":
        app = os.path.join(home, "Library", "Application Support")
        candidates = {
            "Chrome": os.path.join(app, "Google", "Chrome"),
            "Chrome Beta": os.path.join(app, "Google", "Chrome Beta"),
            "Chrome Canary": os.path.join(app, "Google", "Chrome Canary"),
            "Edge": os.path.join(app, "Microsoft Edge"),
            "Brave": os.path.join(app, "BraveSoftware", "Brave-Browser"),
            "Vivaldi": os.path.join(app, "Vivaldi"),
            "Chromium": os.path.join(app, "Chromium"),
            "Yandex": os.path.join(app, "Yandex", "YandexBrowser"),
            "Opera": os.path.join(app, "com.operasoftware.Opera"),
            "Opera GX": os.path.join(app, "com.operasoftware.OperaGX"),
        }
    else:  # Linux et assimiles
        cfg = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))
        var = os.path.join(home, ".var", "app")
        candidates = {
            "Chrome": os.path.join(cfg, "google-chrome"),
            "Chromium": os.path.join(cfg, "chromium"),
            "Chromium (Snap)": os.path.join(home, "snap", "chromium", "common", "chromium"),
            "Edge": os.path.join(cfg, "microsoft-edge"),
            "Brave": os.path.join(cfg, "BraveSoftware", "Brave-Browser"),
            "Brave (Flatpak)": os.path.join(var, "com.brave.Browser", "config", "BraveSoftware", "Brave-Browser"),
            "Vivaldi": os.path.join(cfg, "vivaldi"),
            "Yandex": os.path.join(cfg, "yandex-browser"),
            "Opera": os.path.join(cfg, "opera"),
        }

    return {name: path for name, path in candidates.items() if os.path.isdir(path)}


def _chromium_profiles(base: str) -> "list[tuple[str, str]]":
    """Retourne [(nom du profil, chemin du fichier History)] pour un dossier
    racine Chromium. Gere les profils multiples (Default, Profile 1, ...) et le
    cas Opera ou le fichier History est directement dans le dossier racine."""
    found: "list[tuple[str, str]]" = []
    seen: "set[str]" = set()

    def add(name: str, path: str) -> None:
        real = os.path.realpath(path)
        if os.path.isfile(path) and real not in seen:
            seen.add(real)
            found.append((name, path))

    # Cas Opera : History a la racine.
    add("Default", os.path.join(base, "History"))

    # Cas standard : sous-dossiers de profils.
    try:
        for entry in sorted(os.listdir(base)):
            full = os.path.join(base, entry)
            if not os.path.isdir(full):
                continue
            if entry in ("Default", "Guest Profile", "System Profile") or entry.startswith("Profile "):
                add(entry, os.path.join(full, "History"))
    except OSError:
        pass

    return found


def _firefox_bases() -> "list[str]":
    system = platform.system()
    home = _home()
    if system == "Windows":
        roaming = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        return [os.path.join(roaming, "Mozilla", "Firefox", "Profiles")]
    if system == "Darwin":
        return [os.path.join(home, "Library", "Application Support", "Firefox", "Profiles")]
    # Linux : installation classique, Snap et Flatpak.
    return [
        os.path.join(home, ".mozilla", "firefox"),
        os.path.join(home, "snap", "firefox", "common", ".mozilla", "firefox"),
        os.path.join(home, ".var", "app", "org.mozilla.firefox", ".mozilla", "firefox"),
    ]


def _firefox_profiles() -> "list[tuple[str, str]]":
    found: "list[tuple[str, str]]" = []
    seen: "set[str]" = set()
    for base in _firefox_bases():
        if not os.path.isdir(base):
            continue
        try:
            for entry in sorted(os.listdir(base)):
                places = os.path.join(base, entry, "places.sqlite")
                real = os.path.realpath(places)
                if os.path.isfile(places) and real not in seen:
                    seen.add(real)
                    # Nom lisible : on retire le suffixe aleatoire "xxxx.".
                    label = entry.split(".", 1)[-1] if "." in entry else entry
                    found.append((label or entry, places))
        except OSError:
            pass
    return found


def discover_sources() -> "list[dict]":
    """Detecte toutes les sources d'historique disponibles et leur attribue un
    identifiant stable pour la duree de la session."""
    sources: "list[dict]" = []
    for browser, base in _chromium_bases().items():
        for profile, db_path in _chromium_profiles(base):
            sources.append(
                {"engine": "chromium", "browser": browser, "profile": profile, "db_path": db_path}
            )
    for profile, db_path in _firefox_profiles():
        sources.append(
            {"engine": "firefox", "browser": "Firefox", "profile": profile, "db_path": db_path}
        )
    for index, source in enumerate(sources):
        source["id"] = index
    return sources


# =====================================================================
#  Lecture de l'historique
# =====================================================================
def _copy_db(db_path: str) -> "tuple[str, str]":
    """Copie la base (plus ses journaux -wal / -shm) dans un dossier temporaire
    afin de pouvoir la lire meme quand le navigateur est ouvert et verrouille le
    fichier original."""
    tmpdir = tempfile.mkdtemp(prefix="histnomade_")
    copy = os.path.join(tmpdir, "copy.sqlite")
    shutil.copy2(db_path, copy)
    for ext in ("-wal", "-shm"):
        extra = db_path + ext
        if os.path.isfile(extra):
            try:
                shutil.copy2(extra, copy + ext)
            except OSError:
                pass
    return tmpdir, copy


def read_source(source: dict) -> "list[dict]":
    """Retourne la liste des entrees d'historique d'une source."""
    tmpdir, copy = _copy_db(source["db_path"])
    entries: "list[dict]" = []
    try:
        con = sqlite3.connect(copy)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        if source["engine"] == "chromium":
            rows = cur.execute(
                "SELECT id, url, title, visit_count, last_visit_time "
                "FROM urls ORDER BY last_visit_time DESC"
            )
            for row in rows:
                entries.append(
                    {
                        "src": source["id"],
                        "rowid": row["id"],
                        "url": row["url"] or "",
                        "title": row["title"] or "",
                        "visits": row["visit_count"] or 0,
                        "ts": chromium_to_unix(row["last_visit_time"]),
                    }
                )
        else:  # firefox
            rows = cur.execute(
                "SELECT id, url, title, visit_count, last_visit_date "
                "FROM moz_places WHERE last_visit_date IS NOT NULL "
                "ORDER BY last_visit_date DESC"
            )
            for row in rows:
                entries.append(
                    {
                        "src": source["id"],
                        "rowid": row["id"],
                        "url": row["url"] or "",
                        "title": row["title"] or "",
                        "visits": row["visit_count"] or 0,
                        "ts": firefox_to_unix(row["last_visit_date"]),
                    }
                )
        con.close()
    except sqlite3.Error as exc:
        raise RuntimeError(str(exc))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return entries


def read_all(sources: "list[dict]") -> "tuple[list[dict], list[dict]]":
    """Lit toutes les sources. Retourne (entrees, erreurs)."""
    entries: "list[dict]" = []
    errors: "list[dict]" = []
    for source in sources:
        try:
            entries.extend(read_source(source))
        except Exception as exc:  # noqa: BLE001 - on veut degrader proprement
            errors.append({"src": source["id"], "error": str(exc)})
    return entries, errors


# =====================================================================
#  Suppression de l'historique
# =====================================================================
class BrowserLockedError(RuntimeError):
    """Levee quand la base est verrouillee (navigateur ouvert)."""


def _delete_chromium(cur: sqlite3.Cursor, rowids) -> None:
    if rowids is None:  # tout effacer
        for table in ("visits", "keyword_search_terms", "urls", "segment_usage", "segments"):
            try:
                cur.execute(f"DELETE FROM {table}")
            except sqlite3.OperationalError:
                pass
        return
    if not rowids:
        return
    placeholders = ",".join("?" * len(rowids))
    for table, column in (("visits", "url"), ("keyword_search_terms", "url_id")):
        try:
            cur.execute(f"DELETE FROM {table} WHERE {column} IN ({placeholders})", rowids)
        except sqlite3.OperationalError:
            pass
    cur.execute(f"DELETE FROM urls WHERE id IN ({placeholders})", rowids)


def _delete_firefox(cur: sqlite3.Cursor, rowids) -> None:
    # places.sqlite possede des declencheurs (triggers) de frecence/origines qui
    # referencent des tables temporaires creees uniquement par Firefox a
    # l'execution. Hors de Firefox, ils echoueraient. On les retire donc le
    # temps de l'operation puis on les recree a l'identique : le tout dans la
    # meme transaction, donc atomique (aucune perte possible en cas d'incident).
    triggers = cur.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='trigger' AND sql IS NOT NULL"
    ).fetchall()
    for name, _sql in triggers:
        cur.execute(f'DROP TRIGGER IF EXISTS "{name}"')

    related = ("moz_historyvisits", "moz_annos", "moz_inputhistory",
               "moz_places_metadata", "moz_places_metadata_snapshots")

    if rowids is None:  # tout effacer
        for table in related:
            try:
                cur.execute(f"DELETE FROM {table}")
            except sqlite3.OperationalError:
                pass
        # On conserve les pages en favori (juste remise a zero des visites).
        try:
            bookmarked = [r[0] for r in cur.execute("SELECT DISTINCT fk FROM moz_bookmarks WHERE fk IS NOT NULL")]
        except sqlite3.OperationalError:
            bookmarked = []
        if bookmarked:
            ph = ",".join("?" * len(bookmarked))
            cur.execute(
                f"UPDATE moz_places SET visit_count=0, last_visit_date=NULL WHERE id IN ({ph})",
                bookmarked,
            )
            cur.execute(f"DELETE FROM moz_places WHERE id NOT IN ({ph})", bookmarked)
        else:
            cur.execute("DELETE FROM moz_places")
    elif rowids:
        placeholders = ",".join("?" * len(rowids))
        for table in related:
            try:
                cur.execute(f"DELETE FROM {table} WHERE place_id IN ({placeholders})", rowids)
            except sqlite3.OperationalError:
                pass
        try:
            bookmarked = {
                r[0]
                for r in cur.execute(
                    f"SELECT fk FROM moz_bookmarks WHERE fk IN ({placeholders})", rowids
                )
            }
        except sqlite3.OperationalError:
            bookmarked = set()
        to_delete = [r for r in rowids if r not in bookmarked]
        to_keep = [r for r in rowids if r in bookmarked]
        if to_keep:
            ph = ",".join("?" * len(to_keep))
            cur.execute(
                f"UPDATE moz_places SET visit_count=0, last_visit_date=NULL WHERE id IN ({ph})",
                to_keep,
            )
        if to_delete:
            ph = ",".join("?" * len(to_delete))
            cur.execute(f"DELETE FROM moz_places WHERE id IN ({ph})", to_delete)

    # Recreation des declencheurs a l'identique.
    for _name, sql in triggers:
        cur.execute(sql)


def delete_from_source(source: dict, rowids) -> int:
    """Supprime des entrees d'une source. `rowids=None` efface tout l'historique
    de la source. Retourne le nombre d'entrees ciblees. Leve BrowserLockedError
    si le navigateur est ouvert."""
    count = 0 if rowids is None else len(rowids)
    if rowids is not None and not rowids:
        return 0
    try:
        con = sqlite3.connect(source["db_path"], timeout=4)
    except sqlite3.OperationalError as exc:
        raise BrowserLockedError(str(exc))
    try:
        con.isolation_level = None  # transaction manuelle
        cur = con.cursor()
        cur.execute("PRAGMA busy_timeout=3000")
        try:
            cur.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            raise BrowserLockedError(str(exc))
        try:
            if source["engine"] == "chromium":
                _delete_chromium(cur, rowids)
            else:
                _delete_firefox(cur, rowids)
            cur.execute("COMMIT")
        except sqlite3.OperationalError as exc:
            cur.execute("ROLLBACK")
            if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                raise BrowserLockedError(str(exc))
            raise
        except Exception:
            cur.execute("ROLLBACK")
            raise
        # Compacte le fichier apres un gros nettoyage.
        if rowids is None:
            try:
                cur.execute("VACUUM")
            except sqlite3.OperationalError:
                pass
    finally:
        con.close()
    return count


def delete_items(sources_by_id: dict, items: "list[dict]") -> dict:
    """items = [{"src": id, "rowid": n}, ...]. Regroupe par source puis supprime.
    Retourne un rapport {"deleted": n, "locked": [noms], "errors": [..]}."""
    grouped: "dict[int, list[int]]" = {}
    for item in items:
        try:
            grouped.setdefault(int(item["src"]), []).append(int(item["rowid"]))
        except (KeyError, ValueError, TypeError):
            continue
    deleted = 0
    locked: "list[str]" = []
    errors: "list[str]" = []
    for src_id, rowids in grouped.items():
        source = sources_by_id.get(src_id)
        if not source:
            continue
        label = f'{source["browser"]} — {source["profile"]}'
        try:
            deleted += delete_from_source(source, rowids)
        except BrowserLockedError:
            locked.append(label)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{label}: {exc}")
    return {"deleted": deleted, "locked": locked, "errors": errors}


# =====================================================================
#  Export
# =====================================================================
def export_entries(entries: "list[dict]", sources_by_id: dict, fmt: str) -> str:
    fmt = (fmt or "csv").lower()
    enriched = []
    for e in entries:
        source = sources_by_id.get(e["src"], {})
        enriched.append(
            {
                "date": datetime.fromtimestamp(e["ts"]).isoformat() if e["ts"] else "",
                "browser": source.get("browser", ""),
                "profile": source.get("profile", ""),
                "title": e["title"],
                "url": e["url"],
                "visits": e["visits"],
            }
        )
    if fmt == "json":
        return json.dumps(enriched, ensure_ascii=False, indent=2)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["date", "browser", "profile", "title", "url", "visits"])
    writer.writeheader()
    writer.writerows(enriched)
    return buffer.getvalue()


# =====================================================================
#  Interface web locale
# =====================================================================
HTML_PAGE = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__APPNAME__</title>
<style>
  :root {
    --bg:#0f1420; --panel:#171d2b; --panel2:#1e2636; --line:#2a3346;
    --text:#e7ecf5; --muted:#93a0b8; --accent:#4f8cff; --accent2:#2f6bd6;
    --danger:#ff5c6c; --danger2:#d63a4a; --ok:#37c281; --chip:#22304a;
  }
  * { box-sizing:border-box; }
  body { margin:0; font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
         background:var(--bg); color:var(--text); }
  a { color:var(--accent); text-decoration:none; }
  a:hover { text-decoration:underline; }
  header { padding:14px 20px; background:var(--panel); border-bottom:1px solid var(--line);
           display:flex; align-items:center; gap:16px; flex-wrap:wrap; position:sticky; top:0; z-index:5; }
  header h1 { font-size:17px; margin:0; font-weight:650; }
  header .count { color:var(--muted); font-size:13px; }
  header .grow { flex:1; }
  .btn { background:var(--panel2); color:var(--text); border:1px solid var(--line);
         padding:7px 12px; border-radius:8px; cursor:pointer; font-size:13px; }
  .btn:hover { border-color:var(--accent); }
  .btn.primary { background:var(--accent2); border-color:var(--accent2); }
  .btn.primary:hover { background:var(--accent); }
  .btn.danger { background:transparent; border-color:var(--danger2); color:var(--danger); }
  .btn.danger:hover { background:var(--danger2); color:#fff; }
  .btn:disabled { opacity:.45; cursor:not-allowed; }
  .toolbar { padding:12px 20px; display:flex; gap:10px; align-items:center; flex-wrap:wrap;
             background:var(--panel); border-bottom:1px solid var(--line); position:sticky; top:52px; z-index:4; }
  input[type=search], select { background:var(--panel2); color:var(--text); border:1px solid var(--line);
         padding:8px 10px; border-radius:8px; font-size:13px; }
  input[type=search] { min-width:240px; flex:1; }
  .wrap { padding:0 20px 40px; }
  table { width:100%; border-collapse:collapse; margin-top:8px; }
  th, td { text-align:left; padding:9px 10px; border-bottom:1px solid var(--line); vertical-align:top; }
  th { position:sticky; top:104px; background:var(--bg); color:var(--muted); font-weight:600;
       font-size:12px; text-transform:uppercase; letter-spacing:.03em; cursor:pointer; z-index:3; }
  td.title { max-width:520px; }
  td.title .t { font-weight:550; }
  td.title .u { color:var(--muted); font-size:12px; word-break:break-all; }
  td.when { white-space:nowrap; color:var(--muted); font-size:12.5px; }
  .chip { display:inline-block; padding:2px 8px; border-radius:20px; background:var(--chip);
          color:#bcd0f0; font-size:11.5px; white-space:nowrap; }
  td.visits { text-align:right; color:var(--muted); }
  tr:hover td { background:var(--panel); }
  .rowbtn { background:transparent; border:none; color:var(--danger); cursor:pointer; font-size:15px; padding:2px 6px; border-radius:6px; }
  .rowbtn:hover { background:var(--danger2); color:#fff; }
  .pager { display:flex; gap:10px; align-items:center; justify-content:center; margin:18px 0; color:var(--muted); }
  .empty { text-align:center; color:var(--muted); padding:60px 20px; }
  .empty h2 { color:var(--text); }
  #toast { position:fixed; bottom:22px; left:50%; transform:translateX(-50%); background:var(--panel2);
           border:1px solid var(--line); padding:12px 18px; border-radius:10px; max-width:90vw;
           box-shadow:0 8px 30px rgba(0,0,0,.5); opacity:0; transition:opacity .2s; pointer-events:none; }
  #toast.show { opacity:1; }
  #toast.err { border-color:var(--danger2); }
  #toast.ok { border-color:var(--ok); }
  .selbar { display:flex; align-items:center; gap:10px; }
  .selbar b { color:var(--accent); }
  .foot { color:var(--muted); font-size:12px; text-align:center; padding:20px; }
  .hint { color:var(--muted); font-size:12px; }
</style>
</head>
<body>
<header>
  <h1>__APPNAME__</h1>
  <span class="count" id="count">chargement…</span>
  <span class="grow"></span>
  <button class="btn" id="refresh">↻ Actualiser</button>
  <button class="btn" id="exportCsv">Export CSV</button>
  <button class="btn" id="exportJson">Export JSON</button>
</header>

<div class="toolbar">
  <input type="search" id="search" placeholder="Rechercher un titre ou une URL…  (plusieurs mots = ET)">
  <select id="srcFilter"><option value="">Tous les navigateurs / profils</option></select>
  <select id="sort">
    <option value="ts">Plus récent d'abord</option>
    <option value="ts_asc">Plus ancien d'abord</option>
    <option value="visits">Plus visité d'abord</option>
    <option value="title">Titre (A→Z)</option>
    <option value="url">URL (A→Z)</option>
  </select>
  <span class="grow"></span>
  <div class="selbar">
    <label class="hint"><input type="checkbox" id="selAll"> Tout cocher (page)</label>
    <b id="selCount">0</b>
    <button class="btn danger" id="delSel" disabled>Supprimer la sélection</button>
    <button class="btn danger" id="clearAll">Tout effacer…</button>
  </div>
</div>

<div class="wrap">
  <table id="tbl">
    <thead>
      <tr>
        <th style="width:26px"></th>
        <th data-sort="ts" style="width:150px">Date</th>
        <th data-sort="title">Titre / URL</th>
        <th style="width:170px">Source</th>
        <th data-sort="visits" style="width:70px">Visites</th>
        <th style="width:36px"></th>
      </tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>
  <div id="emptyState"></div>
  <div class="pager" id="pager"></div>
</div>

<div class="foot">
  Tout se passe en local, rien n'est envoyé sur Internet. Fermez le navigateur
  concerné avant de supprimer si une suppression échoue (fichier verrouillé).
  · v__VERSION__
</div>

<div id="toast"></div>

<script>
const TOKEN = "__TOKEN__";
const state = { offset:0, limit:100, total:0, search:"", src:"", sort:"ts", rows:[], selected:new Set() };

function api(path, opts={}) {
  opts.headers = Object.assign({ "X-Token": TOKEN, "Content-Type":"application/json" }, opts.headers||{});
  return fetch(path, opts).then(r => r.ok ? r.json() : r.json().then(e=>Promise.reject(e)));
}
function toast(msg, kind="") {
  const t = document.getElementById("toast");
  t.textContent = msg; t.className = "show " + kind;
  clearTimeout(t._h); t._h = setTimeout(()=>{ t.className=""; }, 3800);
}
function fmtDate(ts) {
  if (!ts) return "—";
  try { return new Date(ts*1000).toLocaleString("fr-FR", {dateStyle:"medium", timeStyle:"short"}); }
  catch(e){ return new Date(ts*1000).toLocaleString(); }
}
function esc(s){ return (s||"").replace(/[&<>"]/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }

function loadSources() {
  return api("/api/sources").then(d => {
    const sel = document.getElementById("srcFilter");
    sel.innerHTML = '<option value="">Tous les navigateurs / profils (' + d.total + ')</option>';
    d.sources.forEach(s => {
      const o = document.createElement("option");
      o.value = s.id;
      o.textContent = s.browser + " — " + s.profile + " (" + s.count + ")";
      sel.appendChild(o);
    });
    if (d.sources.length === 0 && d.errors.length === 0) {
      // rien : message gere dans load()
    }
  });
}

function load() {
  const q = new URLSearchParams({ offset:state.offset, limit:state.limit,
     search:state.search, src:state.src, sort:state.sort });
  return api("/api/history?"+q.toString()).then(d => {
    state.total = d.total; state.rows = d.items;
    document.getElementById("count").textContent =
      d.total.toLocaleString("fr-FR") + " entrée" + (d.total>1?"s":"");
    render();
  }).catch(e => toast("Erreur de chargement: "+(e.error||e.message||e), "err"));
}

function render() {
  const tb = document.getElementById("rows");
  const empty = document.getElementById("emptyState");
  tb.innerHTML = "";
  if (state.total === 0) {
    empty.innerHTML = state.search || state.src
      ? '<div class="empty"><h2>Aucun résultat</h2><p>Essayez d\'élargir la recherche.</p></div>'
      : '<div class="empty"><h2>Aucun historique détecté</h2><p>Aucun navigateur pris en charge n\'a été trouvé pour cet utilisateur.</p></div>';
    document.getElementById("pager").innerHTML = "";
    updateSel();
    return;
  }
  empty.innerHTML = "";
  const frag = document.createDocumentFragment();
  state.rows.forEach(r => {
    const key = r.src + ":" + r.rowid;
    const tr = document.createElement("tr");
    tr.innerHTML =
      '<td><input type="checkbox" data-k="'+key+'" '+(state.selected.has(key)?"checked":"")+'></td>' +
      '<td class="when">'+fmtDate(r.ts)+'</td>' +
      '<td class="title"><div class="t"><a href="'+esc(r.url)+'" target="_blank" rel="noreferrer noopener">'+
        esc(r.title || r.url || "(sans titre)")+'</a></div><div class="u">'+esc(r.url)+'</div></td>' +
      '<td><span class="chip">'+esc(r.browser)+' · '+esc(r.profile)+'</span></td>' +
      '<td class="visits">'+r.visits+'</td>' +
      '<td><button class="rowbtn" title="Supprimer cette entrée" data-del="'+key+'">✕</button></td>';
    frag.appendChild(tr);
  });
  tb.appendChild(frag);
  renderPager();
  updateSel();
}

function renderPager() {
  const p = document.getElementById("pager");
  const from = state.offset+1, to = Math.min(state.offset+state.limit, state.total);
  const pages = Math.max(1, Math.ceil(state.total/state.limit));
  const cur = Math.floor(state.offset/state.limit)+1;
  p.innerHTML =
    '<button class="btn" id="prev" '+(state.offset<=0?"disabled":"")+'>← Précédent</button>' +
    '<span>'+from+'–'+to+' sur '+state.total.toLocaleString("fr-FR")+'  (page '+cur+'/'+pages+')</span>' +
    '<button class="btn" id="next" '+(to>=state.total?"disabled":"")+'>Suivant →</button>';
  document.getElementById("prev").onclick = ()=>{ state.offset=Math.max(0,state.offset-state.limit); load(); window.scrollTo(0,0); };
  document.getElementById("next").onclick = ()=>{ state.offset+=state.limit; load(); window.scrollTo(0,0); };
}

function updateSel() {
  document.getElementById("selCount").textContent = state.selected.size;
  document.getElementById("delSel").disabled = state.selected.size === 0;
}

function delItems(items, label) {
  return api("/api/delete", { method:"POST", body: JSON.stringify({items}) }).then(rep => {
    let msg = rep.deleted + " entrée(s) supprimée(s).";
    if (rep.locked && rep.locked.length) msg += " ⚠ Fermez d'abord : " + rep.locked.join(", ") + ".";
    if (rep.errors && rep.errors.length) msg += " Erreur: " + rep.errors.join("; ");
    toast(msg, (rep.locked && rep.locked.length) || (rep.errors && rep.errors.length) ? "err" : "ok");
    state.selected.clear();
    return loadSources().then(load);
  }).catch(e => toast("Échec: "+(e.error||e.message||e), "err"));
}

// Evenements
document.getElementById("rows").addEventListener("click", ev => {
  const del = ev.target.closest("[data-del]");
  if (del) {
    const [src, rowid] = del.dataset.del.split(":");
    delItems([{src:+src, rowid:+rowid}]);
    return;
  }
  const cb = ev.target.closest('input[type=checkbox][data-k]');
  if (cb) {
    if (cb.checked) state.selected.add(cb.dataset.k); else state.selected.delete(cb.dataset.k);
    updateSel();
  }
});
document.getElementById("selAll").addEventListener("change", ev => {
  document.querySelectorAll('#rows input[type=checkbox][data-k]').forEach(cb => {
    cb.checked = ev.target.checked;
    if (ev.target.checked) state.selected.add(cb.dataset.k); else state.selected.delete(cb.dataset.k);
  });
  updateSel();
});
document.getElementById("delSel").addEventListener("click", () => {
  if (state.selected.size === 0) return;
  if (!confirm("Supprimer définitivement "+state.selected.size+" entrée(s) sélectionnée(s) ?")) return;
  const items = [...state.selected].map(k => { const [s,r]=k.split(":"); return {src:+s, rowid:+r}; });
  delItems(items);
});
document.getElementById("clearAll").addEventListener("click", () => {
  const scope = state.src ? "de ce profil" : "de TOUS les navigateurs et profils";
  if (!confirm("Effacer TOUT l'historique "+scope+" ?\n\nCette action est irréversible.")) return;
  if (!confirm("Dernière confirmation : effacer tout l'historique "+scope+" ?")) return;
  api("/api/clear", { method:"POST", body: JSON.stringify({ src: state.src === "" ? null : +state.src }) })
    .then(rep => {
      let msg = "Historique effacé (" + rep.deleted + " entrée(s)).";
      if (rep.locked && rep.locked.length) msg += " ⚠ Fermez d'abord : " + rep.locked.join(", ") + ".";
      if (rep.errors && rep.errors.length) msg += " Erreur: " + rep.errors.join("; ");
      toast(msg, (rep.locked && rep.locked.length) ? "err" : "ok");
      state.selected.clear(); state.offset = 0;
      return loadSources().then(load);
    })
    .catch(e => toast("Échec: "+(e.error||e.message||e), "err"));
});

let searchTimer;
document.getElementById("search").addEventListener("input", ev => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { state.search = ev.target.value.trim(); state.offset = 0; load(); }, 250);
});
document.getElementById("srcFilter").addEventListener("change", ev => {
  state.src = ev.target.value; state.offset = 0; load();
});
document.getElementById("sort").addEventListener("change", ev => {
  state.sort = ev.target.value; state.offset = 0; load();
});
document.querySelectorAll("th[data-sort]").forEach(th => th.addEventListener("click", () => {
  const s = th.dataset.sort;
  state.sort = (s === "ts") ? (state.sort === "ts" ? "ts_asc" : "ts") : s;
  document.getElementById("sort").value = state.sort.startsWith("ts") ? state.sort : s;
  state.offset = 0; load();
}));
document.getElementById("refresh").addEventListener("click", () => loadSources().then(load));
document.getElementById("exportCsv").addEventListener("click", () => window.location = "/api/export?format=csv&token="+encodeURIComponent(TOKEN));
document.getElementById("exportJson").addEventListener("click", () => window.location = "/api/export?format=json&token="+encodeURIComponent(TOKEN));

loadSources().then(load);
</script>
</body>
</html>
"""


def _matches(entry: dict, terms: "list[str]", browser: str, profile: str) -> bool:
    if not terms:
        return True
    haystack = (entry["title"] + " " + entry["url"] + " " + browser + " " + profile).lower()
    return all(term in haystack for term in terms)


class HistoryServer:
    """Serveur web local minimal (bibliotheque standard)."""

    def __init__(self, sources: "list[dict]"):
        self.sources = sources
        self.sources_by_id = {s["id"]: s for s in sources}
        self.token = token_urlsafe(24)
        self._cache: "list[dict] | None" = None
        self._lock = threading.Lock()

    # --- donnees ---
    def entries(self, refresh: bool = False) -> "list[dict]":
        with self._lock:
            if self._cache is None or refresh:
                data, _errors = read_all(self.sources)
                self._cache = data
            return self._cache

    def invalidate(self) -> None:
        with self._lock:
            self._cache = None

    def source_summary(self) -> dict:
        entries = self.entries()
        counts: "dict[int, int]" = {}
        for e in entries:
            counts[e["src"]] = counts.get(e["src"], 0) + 1
        out = []
        for s in self.sources:
            out.append(
                {
                    "id": s["id"],
                    "browser": s["browser"],
                    "profile": s["profile"],
                    "engine": s["engine"],
                    "count": counts.get(s["id"], 0),
                }
            )
        return {"sources": out, "total": len(entries), "errors": []}

    def query(self, search: str, src: str, sort: str, offset: int, limit: int) -> dict:
        entries = self.entries()
        terms = [t for t in (search or "").lower().split() if t]
        src_id = None
        if src not in ("", None):
            try:
                src_id = int(src)
            except ValueError:
                src_id = None

        filtered = []
        for e in entries:
            source = self.sources_by_id.get(e["src"], {})
            if src_id is not None and e["src"] != src_id:
                continue
            if not _matches(e, terms, source.get("browser", ""), source.get("profile", "")):
                continue
            filtered.append(e)

        reverse = True
        if sort == "ts_asc":
            keyfn, reverse = (lambda e: e["ts"]), False
        elif sort == "visits":
            keyfn = lambda e: e["visits"]
        elif sort == "title":
            keyfn, reverse = (lambda e: (e["title"] or e["url"]).lower()), False
        elif sort == "url":
            keyfn, reverse = (lambda e: e["url"].lower()), False
        else:  # ts
            keyfn = lambda e: e["ts"]
        filtered.sort(key=keyfn, reverse=reverse)

        total = len(filtered)
        page = filtered[offset : offset + limit]
        items = []
        for e in page:
            source = self.sources_by_id.get(e["src"], {})
            items.append(
                {
                    "src": e["src"],
                    "rowid": e["rowid"],
                    "url": e["url"],
                    "title": e["title"],
                    "visits": e["visits"],
                    "ts": e["ts"],
                    "browser": source.get("browser", ""),
                    "profile": source.get("profile", ""),
                }
            )
        return {"total": total, "offset": offset, "limit": limit, "items": items}


def make_handler(server: HistoryServer):
    app = server

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_args):  # silence
            pass

        # --- helpers ---
        def _ok_host(self) -> bool:
            host = (self.headers.get("Host") or "").split(":")[0]
            return host in ("localhost", "127.0.0.1", "[::1]", "::1", "")

        def _check_token(self, params=None) -> bool:
            token = self.headers.get("X-Token")
            if not token and params:
                token = (params.get("token") or [None])[0]
            return token == app.token

        def _send_json(self, obj, status=200):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_bytes(self, body: bytes, content_type: str, status=200, download=None):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            if download:
                self.send_header("Content-Disposition", f'attachment; filename="{download}"')
            self.end_headers()
            self.wfile.write(body)

        def _read_body(self):
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            raw = self.rfile.read(length)
            try:
                return json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return {}

        # --- routes ---
        def do_GET(self):
            if not self._ok_host():
                self._send_json({"error": "hote non autorise"}, 403)
                return
            parsed = urlparse(self.path)
            path = parsed.path
            params = parse_qs(parsed.query)

            if path == "/":
                page = (
                    HTML_PAGE.replace("__TOKEN__", app.token)
                    .replace("__APPNAME__", APP_NAME)
                    .replace("__VERSION__", VERSION)
                )
                self._send_bytes(page.encode("utf-8"), "text/html; charset=utf-8")
                return

            if path == "/api/sources":
                if not self._check_token(params):
                    self._send_json({"error": "jeton invalide"}, 403)
                    return
                self._send_json(app.source_summary())
                return

            if path == "/api/history":
                if not self._check_token(params):
                    self._send_json({"error": "jeton invalide"}, 403)
                    return
                try:
                    offset = max(0, int((params.get("offset") or [0])[0]))
                    limit = min(1000, max(1, int((params.get("limit") or [100])[0])))
                except ValueError:
                    offset, limit = 0, 100
                result = app.query(
                    (params.get("search") or [""])[0],
                    (params.get("src") or [""])[0],
                    (params.get("sort") or ["ts"])[0],
                    offset,
                    limit,
                )
                self._send_json(result)
                return

            if path == "/api/export":
                if not self._check_token(params):
                    self._send_json({"error": "jeton invalide"}, 403)
                    return
                fmt = (params.get("format") or ["csv"])[0]
                text = export_entries(app.entries(), app.sources_by_id, fmt)
                ext = "json" if fmt == "json" else "csv"
                ctype = "application/json" if fmt == "json" else "text/csv"
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                self._send_bytes(
                    text.encode("utf-8"),
                    f"{ctype}; charset=utf-8",
                    download=f"historique-{stamp}.{ext}",
                )
                return

            self._send_json({"error": "introuvable"}, 404)

        def do_POST(self):
            if not self._ok_host():
                self._send_json({"error": "hote non autorise"}, 403)
                return
            if not self._check_token():
                self._send_json({"error": "jeton invalide"}, 403)
                return
            path = urlparse(self.path).path
            data = self._read_body()

            if path == "/api/delete":
                items = data.get("items") or []
                report = delete_items(app.sources_by_id, items)
                app.invalidate()
                self._send_json(report)
                return

            if path == "/api/clear":
                src = data.get("src", None)
                if src is None:
                    targets = app.sources
                else:
                    try:
                        targets = [app.sources_by_id[int(src)]]
                    except (KeyError, ValueError, TypeError):
                        targets = []
                deleted, locked, errors = 0, [], []
                for source in targets:
                    label = f'{source["browser"]} — {source["profile"]}'
                    # nombre d'entrees avant suppression, pour le rapport
                    before = sum(1 for e in app.entries() if e["src"] == source["id"])
                    try:
                        delete_from_source(source, None)
                        deleted += before
                    except BrowserLockedError:
                        locked.append(label)
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{label}: {exc}")
                app.invalidate()
                self._send_json({"deleted": deleted, "locked": locked, "errors": errors})
                return

            self._send_json({"error": "introuvable"}, 404)

    return Handler


def _free_port(preferred=8731) -> int:
    for port in range(preferred, preferred + 40):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 0  # laisse l'OS choisir


def run_web(sources: "list[dict]", port: int = 0, open_browser: bool = True) -> None:
    server = HistoryServer(sources)
    if port == 0:
        port = _free_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(server))
    real_port = httpd.server_address[1]
    url = f"http://127.0.0.1:{real_port}/"

    print("=" * 60)
    print(f"  {APP_NAME}  v{VERSION}")
    print("=" * 60)
    print(f"  {len(sources)} source(s) d'historique detectee(s).")
    print(f"  Interface ouverte sur : {url}")
    print("  (Tout reste en local. Ctrl+C pour quitter.)")
    print("=" * 60)

    if open_browser:
        threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArret. Au revoir !")
    finally:
        httpd.server_close()


# =====================================================================
#  Mode terminal (CLI)
# =====================================================================
def run_cli(sources: "list[dict]", search: str, limit: int, export_path: str, fmt: str) -> None:
    sources_by_id = {s["id"]: s for s in sources}
    entries, errors = read_all(sources)

    print(f"{APP_NAME} v{VERSION}")
    print(f"{len(sources)} source(s), {len(entries)} entree(s) au total.\n")
    for s in sources:
        n = sum(1 for e in entries if e["src"] == s["id"])
        print(f"  · {s['browser']} — {s['profile']}: {n}")
    for err in errors:
        s = sources_by_id.get(err["src"], {})
        print(f"  ! {s.get('browser','?')} — {s.get('profile','?')}: {err['error']}")
    print()

    if export_path:
        text = export_entries(entries, sources_by_id, fmt)
        with open(export_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print(f"Export ecrit dans : {export_path} ({fmt})")
        return

    terms = [t for t in (search or "").lower().split() if t]
    shown = 0
    for e in sorted(entries, key=lambda x: x["ts"], reverse=True):
        s = sources_by_id.get(e["src"], {})
        if not _matches(e, terms, s.get("browser", ""), s.get("profile", "")):
            continue
        when = datetime.fromtimestamp(e["ts"]).strftime("%Y-%m-%d %H:%M") if e["ts"] else "----------  ---"
        title = (e["title"] or e["url"])[:70]
        print(f"{when}  [{s.get('browser','?')[:8]:<8}] {title}")
        print(f"                    {e['url']}")
        shown += 1
        if shown >= limit:
            print(f"\n… ({limit} affichees ; utilisez --limit pour en voir plus)")
            break
    if shown == 0:
        print("Aucune entree.")


# =====================================================================
#  Point d'entree
# =====================================================================
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} — navigation et nettoyage portable de l'historique des navigateurs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemples:\n"
        "  python3 history_tool.py                 interface web\n"
        "  python3 history_tool.py --cli           liste dans le terminal\n"
        "  python3 history_tool.py --cli --search youtube\n"
        "  python3 history_tool.py --cli --export histo.csv\n",
    )
    parser.add_argument("--cli", action="store_true", help="mode terminal (pas d'interface web)")
    parser.add_argument("--search", default="", help="filtre de recherche (mode --cli)")
    parser.add_argument("--limit", type=int, default=50, help="nombre d'entrees affichees en --cli")
    parser.add_argument("--export", default="", metavar="FICHIER", help="exporte tout l'historique (--cli)")
    parser.add_argument("--format", default="csv", choices=["csv", "json"], help="format d'export")
    parser.add_argument("--port", type=int, default=0, help="port du serveur web (defaut: auto)")
    parser.add_argument("--no-browser", action="store_true", help="ne pas ouvrir le navigateur automatiquement")
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {VERSION}")
    args = parser.parse_args(argv)

    sources = discover_sources()

    if not sources and not args.cli:
        print(f"{APP_NAME}: aucun navigateur pris en charge n'a ete detecte pour cet utilisateur.")
        print("Lancez tout de meme l'interface ? Elle affichera un message d'aide.")

    if args.cli:
        run_cli(sources, args.search, args.limit, args.export, args.format)
        return 0

    run_web(sources, port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
