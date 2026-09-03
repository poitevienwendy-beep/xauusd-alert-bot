#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-test de « Historique Nomade ».

Ce script cree de FAUSSES bases SQLite (style Chrome et Firefox) dans un
dossier temporaire, puis verifie que la lecture, la suppression et l'export
fonctionnent. Il NE touche a AUCUN historique reel : c'est un simple controle
de bon fonctionnement, sans danger, que vous pouvez lancer avant d'utiliser
l'outil pour de vrai.

    python3 selftest.py
"""
import importlib.util
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "history_tool.py")

spec = importlib.util.spec_from_file_location("history_tool", TOOL)
ht = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ht)

fails = []


def check(name, cond):
    print(("  ok  " if cond else " FAIL") + "  " + name)
    if not cond:
        fails.append(name)


def main():
    workdir = tempfile.mkdtemp(prefix="histnomade_selftest_")

    # ---------- Conversions d'horodatage ----------
    check("firefox: microsecondes -> secondes", ht.firefox_to_unix(1_600_000_000_000_000) == 1_600_000_000.0)
    check("chromium: zero reste zero", ht.chromium_to_unix(0) == 0.0)
    check("chromium: decalage d'epoque 1601", abs(ht.chromium_to_unix(11644473600 * 1_000_000)) < 1e-6)

    # ---------- Base Chromium factice ----------
    chrome_db = os.path.join(workdir, "History")
    con = sqlite3.connect(chrome_db)
    con.executescript(
        "CREATE TABLE urls(id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INT,"
        " typed_count INT, last_visit_time INT, hidden INT);"
        "CREATE TABLE visits(id INTEGER PRIMARY KEY, url INT, visit_time INT);"
        "CREATE TABLE keyword_search_terms(keyword_id INT, url_id INT, term TEXT);"
    )
    base = (1_600_000_000 + 11644473600) * 1_000_000
    con.execute("INSERT INTO urls VALUES(1,'https://a.com','A',5,0,?,0)", (base,))
    con.execute("INSERT INTO urls VALUES(2,'https://b.com','B',3,0,?,0)", (base + 1_000_000,))
    con.execute("INSERT INTO visits VALUES(10,1,?)", (base,))
    con.execute("INSERT INTO keyword_search_terms VALUES(1,1,'a')")
    con.commit()
    con.close()

    src_c = {"id": 0, "engine": "chromium", "browser": "Chrome", "profile": "Default", "db_path": chrome_db}
    rows = ht.read_source(src_c)
    check("chromium: lecture de 2 entrees", len(rows) == 2)
    check("chromium: tri plus recent d'abord", rows[0]["rowid"] == 2)
    check("chromium: conversion de date", abs(rows[-1]["ts"] - 1_600_000_000) < 2)
    ht.delete_from_source(src_c, [1])
    after = ht.read_source(src_c)
    check("chromium: suppression d'une entree", len(after) == 1 and after[0]["rowid"] == 2)
    con = sqlite3.connect(chrome_db)
    orphans = con.execute("SELECT COUNT(*) FROM visits WHERE url=1").fetchone()[0]
    con.close()
    check("chromium: visites liees supprimees", orphans == 0)
    ht.delete_from_source(src_c, None)
    check("chromium: tout effacer", len(ht.read_source(src_c)) == 0)

    # ---------- Base Firefox factice (avec un trigger « piege ») ----------
    ff_db = os.path.join(workdir, "places.sqlite")
    con = sqlite3.connect(ff_db)
    con.executescript(
        "CREATE TABLE moz_places(id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INT,"
        " hidden INT DEFAULT 0, last_visit_date INT);"
        "CREATE TABLE moz_historyvisits(id INTEGER PRIMARY KEY, place_id INT, visit_date INT);"
        "CREATE TABLE moz_bookmarks(id INTEGER PRIMARY KEY, fk INT);"
        # Ce trigger reference une table temporaire que seul Firefox cree a
        # l'execution. Sans la technique « retirer/recreer les triggers », la
        # suppression echouerait ici.
        "CREATE TRIGGER moz_places_afterdelete_trigger AFTER DELETE ON moz_places "
        "BEGIN INSERT INTO moz_updateoriginsdelete_temp(place_id) VALUES(OLD.id); END;"
    )
    fb = 1_600_000_000 * 1_000_000
    con.execute("INSERT INTO moz_places VALUES(1,'https://x.com','X',4,0,?)", (fb,))
    con.execute("INSERT INTO moz_places VALUES(2,'https://y.com','Y',2,0,?)", (fb + 1_000_000,))
    con.execute("INSERT INTO moz_places VALUES(3,'https://z.com','Z favori',9,0,?)", (fb + 2_000_000,))
    con.execute("INSERT INTO moz_places VALUES(4,'https://nulle.com','sans visite',0,0,NULL)")
    con.execute("INSERT INTO moz_historyvisits VALUES(100,1,?)", (fb,))
    con.execute("INSERT INTO moz_bookmarks VALUES(50,3)")  # la page 3 est en favori
    con.commit()
    con.close()

    src_f = {"id": 1, "engine": "firefox", "browser": "Firefox", "profile": "main", "db_path": ff_db}
    frows = ht.read_source(src_f)
    check("firefox: exclut les pages jamais visitees", len(frows) == 3)
    ht.delete_from_source(src_f, [1, 3])
    con = sqlite3.connect(ff_db)
    exists1 = con.execute("SELECT COUNT(*) FROM moz_places WHERE id=1").fetchone()[0]
    place3 = con.execute("SELECT visit_count, last_visit_date FROM moz_places WHERE id=3").fetchone()
    trig = con.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name='moz_places_afterdelete_trigger'"
    ).fetchone()[0]
    con.close()
    check("firefox: page normale supprimee", exists1 == 0)
    check("firefox: page en favori conservee mais nettoyee", place3 == (0, None))
    check("firefox: trigger recree apres l'operation", trig == 1)
    check("firefox: il ne reste que la page 2", [r["rowid"] for r in ht.read_source(src_f)] == [2])

    # ---------- Export ----------
    sbid = {0: src_c, 1: src_f}
    entries = [{"src": 1, "rowid": 2, "url": "https://y.com", "title": "Y", "visits": 2, "ts": 1_600_001_000.0}]
    csv_text = ht.export_entries(entries, sbid, "csv")
    json_text = ht.export_entries(entries, sbid, "json")
    check("export CSV valide", "url" in csv_text.splitlines()[0] and "y.com" in csv_text)
    check("export JSON valide", json_text.strip().startswith("[") and "y.com" in json_text)

    # ---------- Recherche / tri via le serveur ----------
    srv = ht.HistoryServer([src_c, src_f])
    srv._cache = [
        {"src": 0, "rowid": 9, "url": "https://pomme.com", "title": "Pomme", "visits": 7, "ts": 100.0},
        {"src": 1, "rowid": 8, "url": "https://banane.com", "title": "Banane", "visits": 1, "ts": 200.0},
    ]
    q = srv.query(search="pomme", src="", sort="ts", offset=0, limit=10)
    check("recherche filtre correctement", q["total"] == 1 and q["items"][0]["title"] == "Pomme")
    q2 = srv.query(search="", src="1", sort="ts", offset=0, limit=10)
    check("filtre par source", q2["total"] == 1 and q2["items"][0]["rowid"] == 8)
    q3 = srv.query(search="", src="", sort="visits", offset=0, limit=10)
    check("tri par nombre de visites", q3["items"][0]["visits"] == 7)

    # nettoyage
    import shutil
    shutil.rmtree(workdir, ignore_errors=True)

    print()
    if fails:
        print(f"{len(fails)} test(s) en echec : {fails}")
        return 1
    print("Tous les tests sont passes. L'outil fonctionne correctement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
