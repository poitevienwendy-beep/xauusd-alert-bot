#!/usr/bin/env python3
"""Génère les silhouettes anatomiques (vue avant / arrière) de l'app d'entraînement.

Le corps est décrit une seule fois, en demi-figure (côté droit du dessin), puis
miroité par le script : la symétrie est exacte, et il n'y a qu'un seul jeu de
coordonnées à retoucher quand on affine un muscle.

Le dessin est empilé en quatre couches, dans cet ordre :

    1. silhouette du tronc (tête, buste, jambes) — un seul contour fermé
    2. muscles du tronc
    3. silhouette des bras — un volume fermé par bras, détaché du buste
    4. muscles des bras, puis les traits anatomiques fins

    python3 build_muscle_map.py  ->  assets/body-front.svg, assets/body-back.svg
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

CX = 100.0          # axe de symétrie
WIDTH = 200.0
HEIGHT = 540.0

Pt = tuple[float, float]


def mx(p: Pt) -> Pt:
    """Miroir d'un point autour de l'axe vertical."""
    return (2 * CX - p[0], p[1])


def fmt(p: Pt) -> str:
    def n(v: float) -> str:
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return f"{n(p[0])},{n(p[1])}"


@dataclass
class Curve:
    """Suite de courbes de Bézier cubiques partant d'un point de départ."""

    start: Pt
    segs: list[tuple[Pt, Pt, Pt]] = field(default_factory=list)

    def to(self, c1: Pt, c2: Pt, end: Pt) -> "Curve":
        self.segs.append((c1, c2, end))
        return self

    def body(self) -> str:
        return " ".join(f"C{fmt(a)} {fmt(b)} {fmt(e)}" for a, b, e in self.segs)

    def d(self, close: bool = False) -> str:
        return f"M{fmt(self.start)} {self.body()}" + (" Z" if close else "")

    def mirrored(self) -> "Curve":
        m = Curve(mx(self.start))
        m.segs = [(mx(a), mx(b), mx(e)) for a, b, e in self.segs]
        return m

    def mirrored_reversed_body(self) -> str:
        """Le même tracé, miroité et parcouru à l'envers.

        Sert à refermer une demi-silhouette en un contour unique : aucune
        couture sur l'axe, et le trait reste une polyligne continue.
        """
        out = []
        for idx in range(len(self.segs) - 1, -1, -1):
            c1, c2, _ = self.segs[idx]
            prev = self.segs[idx - 1][2] if idx > 0 else self.start
            out.append(f"C{fmt(mx(c2))} {fmt(mx(c1))} {fmt(mx(prev))}")
        return " ".join(out)


def closed_by_mirror(half: Curve) -> str:
    """Demi-contour (sommet du crâne -> entrejambe) refermé par son miroir."""
    return f"{half.d()} {half.mirrored_reversed_body()} Z"


def sym(half: Curve, close: bool = True) -> list[str]:
    """Une forme et son miroir — un tracé par côté."""
    return [half.d(close), half.mirrored().d(close)]


# --- Silhouettes -----------------------------------------------------------

def body_outline() -> Curve:
    """Demi-silhouette complète, du sommet du crâne à l'entrejambe.

    Un seul contour continu : tête, épaule, bras (aller par la face externe,
    retour par la face interne), creux de l'aisselle, flanc, jambe. Le vide
    entre le bras et le buste est donc exclu du tracé — pas de pièce rapportée
    et aucune couture visible.

    Repères (canon 8 têtes, athlétique) : menton y=77, ligne d'épaule y=116,
    coude y=221, entrejambe y=274, doigts à mi-cuisse y=336, plante y=526.
    """
    return (
        Curve((100, 18))
        .to((114, 18), (124, 29), (124, 45))        # crâne
        .to((124, 58), (121, 69), (115, 77))        # tempe -> mâchoire
        .to((114, 81), (114, 85), (114, 90))        # cou (court et épais)
        .to((115, 96), (118, 100), (124, 103))      # cou -> trapèze
        .to((134, 106), (144, 110), (151, 116))     # ligne d'épaule
        .to((156, 120), (161, 126), (164, 134))     # coiffe du deltoïde
        .to((169, 145), (171, 157), (170, 168))     # bas du deltoïde
        .to((173, 186), (176, 202), (177, 217))     # bras, face externe -> coude
        .to((180, 232), (182, 247), (182, 262))     # galbe de l'avant-bras
        .to((182, 274), (180, 286), (177, 295))     # poignet
        .to((182, 302), (185, 312), (185, 322))     # tranche de la main
        .to((185, 331), (180, 338), (174, 336))     # bout des doigts
        .to((169, 334), (166, 326), (165, 316))     # bord interne de la main
        .to((164, 309), (163, 302), (163, 296))     # poignet, face interne
        .to((159, 282), (156, 265), (153, 248))     # avant-bras, face interne
        .to((151, 237), (150, 228), (149, 221))     # pli du coude
        .to((148, 203), (147, 183), (146, 165))     # bras, face interne
        .to((145, 157), (144, 151), (142, 147))     # remontée vers l'aisselle
        .to((141, 146), (140, 145), (139, 146))     # creux de l'aisselle
        .to((138, 155), (137, 167), (136, 178))     # flanc / grand dorsal
        .to((134, 190), (133, 200), (132, 210))     # taille
        .to((132, 224), (135, 240), (140, 251))     # hanche
        .to((144, 259), (146, 268), (146, 280))     # hanche -> cuisse
        .to((147, 300), (146, 323), (143, 345))     # cuisse
        .to((141, 359), (138, 371), (136, 381))     # au-dessus du genou
        .to((134, 390), (133, 397), (133, 404))     # genou
        .to((136, 418), (138, 432), (137, 447))     # mollet
        .to((135, 463), (131, 478), (128, 489))     # bas du mollet
        .to((126, 496), (125, 501), (125, 506))     # cheville
        .to((128, 512), (132, 516), (132, 521))     # cou-de-pied
        .to((132, 525), (128, 526), (121, 526))     # plante
        .to((115, 526), (110, 526), (107, 525))     # bord interne du pied
        .to((105, 517), (106, 508), (106, 499))     # cheville interne
        .to((107, 483), (108, 465), (108, 448))     # mollet interne
        .to((109, 432), (110, 419), (110, 406))     # genou interne
        .to((110, 378), (107, 342), (104, 312))     # face interne de cuisse
        .to((102, 297), (101, 285), (100, 274))     # entrejambe
    )


# --- Muscles : vue avant ---------------------------------------------------

def front_muscles() -> list[dict]:
    m: list[dict] = []

    def add(key, label, curve):
        m.append({"key": key, "label": label, "paths": sym(curve)})

    # sterno-cléido-mastoïdien
    add("neck", "Cou", Curve((102, 80))
        .to((105, 80), (107, 84), (109, 90))
        .to((111, 97), (113, 102), (116, 107))
        .to((110, 110), (104, 111), (100, 110))
        .to((100, 100), (100, 90), (101, 81)))

    # trapèze supérieur (portion visible de face)
    add("traps", "Trapèzes", Curve((113, 94))
        .to((124, 97), (136, 102), (147, 110))
        .to((149, 113), (150, 117), (149, 122))
        .to((138, 124), (127, 123), (119, 120))
        .to((115, 115), (113, 104), (113, 96)))

    # grand pectoral
    add("chest", "Pectoraux", Curve((101, 122))
        .to((114, 119), (129, 121), (139, 127))
        .to((142, 139), (140, 153), (133, 163))
        .to((126, 171), (114, 175), (101, 175))
        .to((100, 158), (100, 140), (101, 122)))

    # grand droit de l'abdomen
    add("abs", "Abdominaux", Curve((100, 176))
        .to((108, 176), (114, 181), (117, 189))
        .to((119, 203), (118, 220), (114, 236))
        .to((111, 248), (106, 257), (100, 263))
        .to((100, 234), (100, 205), (100, 176)))

    # obliques + dentelé antérieur
    add("obliques", "Obliques", Curve((134, 176))
        .to((136, 188), (133, 200), (129, 210))
        .to((125, 220), (122, 232), (121, 244))
        .to((116, 238), (114, 226), (116, 212))
        .to((119, 195), (126, 182), (134, 176)))

    # quadriceps
    add("quads", "Quadriceps", Curve((107, 278))
        .to((121, 280), (134, 288), (141, 303))
        .to((145, 320), (143, 343), (137, 363))
        .to((133, 373), (125, 378), (118, 374))
        .to((111, 369), (107, 351), (106, 329))
        .to((106, 306), (105, 289), (107, 278)))

    # adducteurs
    add("adductors", "Adducteurs", Curve((100, 278))
        .to((106, 282), (110, 293), (111, 306))
        .to((111, 323), (108, 340), (104, 352))
        .to((101, 342), (100, 320), (100, 297)))

    # jambier antérieur / péroniers
    add("calves", "Mollets", Curve((111, 405))
        .to((120, 409), (127, 419), (129, 433))
        .to((130, 450), (127, 467), (122, 480))
        .to((118, 470), (115, 452), (114, 436))
        .to((113, 423), (111, 412), (111, 405)))

    # deltoïde antérieur
    add("shoulders", "Épaules", Curve((136, 104))
        .to((150, 107), (162, 117), (168, 130))
        .to((173, 142), (174, 156), (172, 170))
        .to((163, 176), (153, 171), (148, 162))
        .to((144, 150), (139, 126), (136, 104)))

    # biceps brachial
    add("biceps", "Biceps", Curve((146, 158))
        .to((155, 162), (163, 172), (167, 186))
        .to((172, 200), (174, 215), (173, 228))
        .to((163, 234), (154, 230), (150, 220))
        .to((147, 205), (145, 178), (146, 158)))

    # fléchisseurs de l'avant-bras
    add("forearms", "Avant-bras", Curve((152, 238))
        .to((163, 244), (172, 254), (177, 266))
        .to((181, 278), (183, 290), (183, 300))
        .to((176, 305), (169, 300), (165, 291))
        .to((159, 276), (154, 256), (152, 238)))

    return m


def front_lines() -> list[str]:
    """Traits fins : ce sont eux qui donnent le rendu « dessiné »."""
    L: list[str] = []
    # clavicules
    L += sym(Curve((101, 119)).to((113, 116), (127, 117), (141, 124)), close=False)
    # sternum, puis ligne blanche jusqu'au nombril
    L.append(Curve((100, 126)).to((100, 150), (100, 175), (100, 178)).d())
    L.append(Curve((100, 180)).to((100, 205), (100, 228), (100, 245)).d())
    # bords externes du grand droit + intersections tendineuses (le « six-pack »)
    L += sym(Curve((113, 182)).to((117, 194), (117, 212), (114, 230)), close=False)
    for y, w in ((194, 14), (212, 13.5), (229, 12)):
        L.append(Curve((100 - w, y)).to((100 - w / 2, y + 2.5), (100 + w / 2, y + 2.5), (100 + w, y)).d())
    # nombril
    L.append(Curve((97.5, 247)).to((99, 249), (101, 249), (102.5, 247)).d())
    # pli sous-pectoral (mêmes points que le bord bas du pectoral)
    L += sym(Curve((101, 175)).to((114, 175), (126, 171), (133, 163)), close=False)
    # aine
    L += sym(Curve((127, 254)).to((120, 261), (113, 267), (107, 271)), close=False)
    # séparation vaste externe / droit fémoral
    L += sym(Curve((129, 298)).to((134, 318), (134, 342), (129, 362)), close=False)
    # vaste interne
    L += sym(Curve((111, 336)).to((113, 350), (117, 361), (122, 369)), close=False)
    # rotule
    L += sym(Curve((116, 385)).to((124, 383), (130, 388), (131, 395)), close=False)
    # bord interne puis insertion basse du deltoïde (mêmes points que le muscle)
    L += sym(Curve((136, 104)).to((139, 126), (144, 150), (148, 162))
             .to((153, 171), (163, 176), (172, 170)), close=False)
    # pli du coude
    L += sym(Curve((151, 224)).to((159, 228), (169, 227), (176, 221)), close=False)
    # poignet
    L += sym(Curve((165, 296)).to((170, 300), (175, 300), (179, 296)), close=False)
    # pouce puis doigts
    L += sym(Curve((181, 305)).to((177, 310), (175, 316), (175, 322)), close=False)
    for i in range(3):
        L += sym(Curve((172 + i * 4, 316)).to((173 + i * 4.2, 323), (174 + i * 4.2, 329), (174 + i * 4, 335)), close=False)
    # malléoles
    L += sym(Curve((109, 502)).to((114, 506), (120, 506), (125, 503)), close=False)
    return L


# --- Muscles : vue arrière -------------------------------------------------

def back_muscles() -> list[dict]:
    m: list[dict] = []

    def add(key, label, curve):
        m.append({"key": key, "label": label, "paths": sym(curve)})

    add("neck", "Cou", Curve((100, 80))
        .to((106, 80), (111, 85), (113, 92))
        .to((115, 99), (115, 105), (114, 111))
        .to((108, 110), (103, 107), (100, 104)))

    # trapèze supérieur : la chape nuque -> acromion (mouvement de shrug)
    add("traps", "Trapèzes", Curve((100, 101))
        .to((107, 101), (113, 103), (118, 106))
        .to((128, 110), (140, 116), (151, 124))
        .to((150, 129), (146, 133), (140, 136))
        .to((130, 139), (119, 142), (111, 145))
        .to((107, 146), (103, 145), (100, 143)))

    # rhomboïdes + trapèze moyen/inférieur (mouvement de tirage)
    add("rhomboids", "Rhomboïdes", Curve((100, 147))
        .to((109, 148), (117, 152), (122, 158))
        .to((123, 168), (120, 178), (114, 187))
        .to((108, 190), (104, 190), (100, 189)))

    # infra-épineux / petit rond
    add("upper_back", "Haut du dos", Curve((122, 144))
        .to((130, 142), (137, 145), (140, 151))
        .to((141, 159), (138, 166), (132, 170))
        .to((126, 171), (121, 167), (119, 160))
        .to((118, 153), (119, 146), (122, 144)))

    # grand dorsal
    add("lats", "Grand dorsal", Curve((137, 161))
        .to((136, 180), (133, 198), (128, 214))
        .to((124, 226), (119, 234), (113, 239))
        .to((109, 232), (107, 222), (106, 210))
        .to((112, 196), (122, 176), (130, 164)))

    # érecteurs du rachis
    add("lower_back", "Lombaires", Curve((100, 196))
        .to((107, 199), (112, 206), (115, 215))
        .to((117, 226), (116, 238), (112, 248))
        .to((107, 250), (103, 249), (100, 247)))

    # fessiers
    add("glutes", "Fessiers", Curve((100, 252))
        .to((111, 251), (122, 255), (130, 264))
        .to((136, 273), (137, 285), (133, 294))
        .to((127, 303), (115, 306), (104, 301))
        .to((101, 298), (100, 276), (100, 252)))

    # ischio-jambiers
    add("hamstrings", "Ischio-jambiers", Curve((106, 304))
        .to((120, 304), (132, 309), (139, 319))
        .to((142, 335), (140, 353), (135, 368))
        .to((131, 377), (123, 380), (116, 376))
        .to((110, 370), (107, 350), (107, 328)))

    # jumeaux (gastrocnémiens)
    add("calves", "Mollets", Curve((110, 401))
        .to((120, 404), (127, 413), (130, 427))
        .to((132, 444), (129, 462), (123, 476))
        .to((118, 468), (114, 450), (113, 432))
        .to((112, 419), (109, 408), (110, 401)))

    # deltoïde postérieur
    add("shoulders", "Épaules", Curve((136, 104))
        .to((150, 107), (162, 117), (168, 130))
        .to((173, 142), (174, 156), (172, 170))
        .to((163, 176), (153, 171), (148, 162))
        .to((144, 150), (139, 126), (136, 104)))

    # triceps brachial
    add("triceps", "Triceps", Curve((147, 158))
        .to((157, 163), (165, 174), (169, 189))
        .to((172, 203), (173, 218), (172, 231))
        .to((164, 237), (156, 232), (152, 222))
        .to((148, 206), (146, 180), (147, 158)))

    # extenseurs de l'avant-bras
    add("forearms", "Avant-bras", Curve((153, 240))
        .to((164, 246), (173, 256), (178, 268))
        .to((182, 280), (184, 292), (184, 302))
        .to((177, 307), (170, 302), (166, 293))
        .to((160, 278), (155, 258), (153, 240)))

    return m


def back_lines() -> list[str]:
    L: list[str] = []
    # colonne vertébrale
    L.append(Curve((100, 108)).to((100, 150), (100, 200), (100, 250)).d())
    # bord inférieur du trapèze supérieur (mêmes points que le muscle)
    L += sym(Curve((100, 143)).to((103, 145), (107, 146), (111, 145))
             .to((119, 142), (130, 139), (140, 136)), close=False)
    # épine de l'omoplate
    L += sym(Curve((120, 152)).to((128, 146), (135, 145), (141, 149)), close=False)
    # grand dorsal : du creux de l'aisselle au bas du dos
    L += sym(Curve((137, 161)).to((136, 180), (133, 198), (128, 214))
             .to((124, 226), (119, 234), (113, 239)), close=False)
    # bord interne puis insertion basse du deltoïde (mêmes points que le muscle)
    L += sym(Curve((136, 104)).to((139, 126), (144, 150), (148, 162))
             .to((153, 171), (163, 176), (172, 170)), close=False)
    # crête iliaque
    L += sym(Curve((100, 248)).to((112, 248), (124, 251), (133, 258)), close=False)
    # pli fessier
    L += sym(Curve((106, 301)).to((116, 306), (127, 302), (135, 293)), close=False)
    # sillon des ischio-jambiers
    L += sym(Curve((122, 312)).to((123, 332), (122, 352), (119, 368)), close=False)
    # creux poplité
    L += sym(Curve((114, 390)).to((121, 393), (128, 392), (132, 388)), close=False)
    # séparation des jumeaux
    L += sym(Curve((121, 410)).to((123, 430), (122, 450), (119, 468)), close=False)
    # tendon d'Achille
    L += sym(Curve((119, 474)).to((121, 484), (122, 494), (121, 502)), close=False)
    # olécrane
    L += sym(Curve((151, 228)).to((159, 233), (169, 232), (176, 226)), close=False)
    # nuque
    L += sym(Curve((100, 82)).to((107, 82), (113, 78), (116, 72)), close=False)
    # pouce puis doigts
    L += sym(Curve((181, 305)).to((177, 310), (175, 316), (175, 322)), close=False)
    for i in range(3):
        L += sym(Curve((172 + i * 4, 316)).to((173 + i * 4.2, 323), (174 + i * 4.2, 329), (174 + i * 4, 335)), close=False)
    return L


# --- Rendu SVG -------------------------------------------------------------

STYLE = """
.s-skin-a{stop-color:var(--mm-skin-a)}.s-skin-b{stop-color:var(--mm-skin-b)}
.mm-figure{--mm-skin-a:#fdfefe;--mm-skin-b:#e6ebf2;--mm-edge:#a7b1bf;--mm-line:#c3ccd8;
  --mm-l1:#ffc9a9;--mm-l1-b:#f3a97f;--mm-l2:#fb8b70;--mm-l2-b:#e2614a;
  --mm-l3:#e8483f;--mm-l3-b:#c02733;--mm-line-w:.85;--mm-edge-w:1.3}
.mm-silhouette{stroke:var(--mm-edge);stroke-width:var(--mm-edge-w);stroke-linejoin:round}
.mm-lines path{fill:none;stroke:var(--mm-line);stroke-width:var(--mm-line-w);
  stroke-linecap:round;stroke-linejoin:round}
.mm-muscle path{fill:var(--mm-fill,transparent);stroke:var(--mm-stroke,transparent);
  stroke-width:.85;stroke-linejoin:round;
  transition:fill .28s ease,stroke .28s ease}
.mm-muscle[data-level="1"]{--mm-fill:var(--mm-l1);--mm-stroke:var(--mm-l1-b)}
.mm-muscle[data-level="2"]{--mm-fill:var(--mm-l2);--mm-stroke:var(--mm-l2-b)}
.mm-muscle[data-level="3"]{--mm-fill:var(--mm-l3);--mm-stroke:var(--mm-l3-b)}
.mm-figure[data-interactive="true"] .mm-muscle{cursor:pointer}
.mm-figure[data-interactive="true"] .mm-muscle:hover path{stroke:var(--mm-l2-b)}
.mm-muscle:focus-visible{outline:none}
.mm-muscle:focus-visible path{stroke:var(--mm-l3-b);stroke-width:1.6}
@media (prefers-reduced-motion:reduce){.mm-muscle path{transition:none}}
"""

DEFS = """
  <linearGradient id="mm-skin" x1=".25" y1="0" x2=".85" y2="1">
    <stop class="s-skin-a" offset="0"/><stop class="s-skin-b" offset="1"/>
  </linearGradient>
"""


def muscle_group(mus: dict) -> str:
    paths = "".join(f'<path d="{d}"/>' for d in mus["paths"])
    return (
        f'<g class="mm-muscle" data-muscle="{mus["key"]}" data-level="0" '
        f'role="button" tabindex="-1" aria-label="{mus["label"]}">'
        f'<title>{mus["label"]}</title>{paths}</g>'
    )


def render(view: str, muscles: list[dict], lines: list[str]) -> str:
    label = "Vue de face" if view == "front" else "Vue de dos"
    # Les deux figures peuvent cohabiter dans une même page : on suffixe les id.
    style = STYLE.replace("url(#mm-", f"url(#mm-{view}-")
    defs = DEFS.replace('id="mm-', f'id="mm-{view}-')
    shape = closed_by_mirror(body_outline())
    groups = "".join(muscle_group(m) for m in muscles)
    detail = "".join(f'<path d="{d}"/>' for d in lines)
    clip = f"mm-{view}-clip"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH:.0f} {HEIGHT:.0f}"
     class="mm-figure" data-view="{view}" role="img" aria-label="Schéma musculaire — {label}">
  <style>{style}</style>
  <defs>{defs}
  <clipPath id="{clip}"><path d="{shape}"/></clipPath>
  </defs>
  <path class="mm-silhouette" fill="url(#mm-{view}-skin)" d="{shape}"/>
  <g class="mm-muscles" clip-path="url(#{clip})">{groups}</g>
  <g class="mm-lines" clip-path="url(#{clip})">{detail}</g>
  <path class="mm-silhouette mm-edge-top" fill="none" d="{shape}"/>
</svg>
"""


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "assets")
    os.makedirs(out, exist_ok=True)

    svgs: dict[str, str] = {}
    labels: dict[str, str] = {}
    for view, muscles, lines in (
        ("front", front_muscles(), front_lines()),
        ("back", back_muscles(), back_lines()),
    ):
        svgs[view] = render(view, muscles, lines)
        labels.update({m["key"]: m["label"] for m in muscles})
        path = os.path.join(out, f"body-{view}.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svgs[view])
        print(f"écrit {path}")

    # Même contenu exposé en JS : la page de démo s'ouvre alors en double-clic,
    # sans serveur (fetch() est refusé sur file://).
    def js_string(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        return f"`{escaped}`"

    entries = ",\n  ".join(f"{k}: {js_string(v)}" for k, v in svgs.items())
    label_entries = ", ".join(f'{k}: "{v}"' for k, v in labels.items())
    figures = os.path.join(out, "figures.js")
    with open(figures, "w", encoding="utf-8") as fh:
        fh.write(
            "/* Généré par build_muscle_map.py — ne pas éditer à la main. */\n"
            "(function (root) {\n"
            "  var figures = {\n  " + entries + "\n  };\n"
            "  var labels = {" + label_entries + "};\n"
            "  var api = { figures: figures, labels: labels };\n"
            "  if (typeof module === 'object' && module.exports) module.exports = api;\n"
            "  else root.MuscleMapFigures = api;\n"
            "})(typeof globalThis !== 'undefined' ? globalThis : this);\n"
        )
    print(f"écrit {figures}")


if __name__ == "__main__":
    main()
