#!/usr/bin/env python3
"""Modele d'unit economics pour une plateforme de livraison a Dakar.

Toutes les valeurs sont en FCFA (XOF), monnaie arrimee a l'euro
(1 EUR = 655,957 FCFA, parite fixe). Le modele est volontairement
transparent : chaque hypothese est un champ modifiable, et la sortie
montre la contribution par commande puis le seuil de rentabilite mensuel.

Usage :
    python3 unit_economics.py                # les 4 scenarios
    python3 unit_economics.py --sensibilite  # + table de sensibilite

Aucune dependance externe.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace

FCFA_PAR_USD = 565.0  # ~ 655,957 / 1,16 (EUR/USD). A reajuster si la parite bouge.


@dataclass(frozen=True)
class Hypotheses:
    """Hypotheses d'un scenario. Sources et justifications : voir etude-marche.md."""

    nom: str
    commentaire: str

    # --- Revenus par commande ---
    panier_moyen: float          # valeur des biens commandes (GMV hors livraison)
    taux_commission: float       # part du panier prelevee au commercant
    frais_livraison_client: float  # facture au client final
    frais_service_client: float    # frais de service / petite commande

    # --- Couts variables par commande ---
    remuneration_coursier: float   # ce que touche le livreur, hors carburant
    carburant_par_course: float    # essence consommee sur la course
    taux_psp: float                # commission de l'agregateur de paiement (% encaisse)
    cout_support: float            # support client + reconciliation, amorti par commande
    taux_echec: float              # part de commandes annulees/refusees, coutees a perte

    # --- Subvention commerciale ---
    taux_promo: float              # remises et codes promo, en % du panier

    # --- Structure mensuelle ---
    charges_fixes_mensuelles: float  # equipe, bureau, cloud, juridique
    budget_marketing_mensuel: float  # acquisition hors promos transactionnelles

    # --- Volume ---
    commandes_par_jour: int


def encaissement(h: Hypotheses) -> float:
    """Montant total transitant par le PSP pour une commande payee en ligne."""
    return h.panier_moyen + h.frais_livraison_client + h.frais_service_client


def revenu_net(h: Hypotheses) -> float:
    """Revenu reellement conserve par la plateforme (net revenue), avant couts."""
    commission = h.panier_moyen * h.taux_commission
    return commission + h.frais_livraison_client + h.frais_service_client


def couts_variables(h: Hypotheses) -> float:
    base = (
        h.remuneration_coursier
        + h.carburant_par_course
        + encaissement(h) * h.taux_psp
        + h.cout_support
    )
    # Une commande echouee coute la course sans generer de revenu.
    surcout_echec = h.taux_echec * (h.remuneration_coursier + h.carburant_par_course)
    return base + surcout_echec


def promo(h: Hypotheses) -> float:
    return h.panier_moyen * h.taux_promo


def contribution(h: Hypotheses) -> float:
    """Marge de contribution par commande, apres subvention commerciale."""
    return revenu_net(h) - couts_variables(h) - promo(h)


def seuil_commandes_jour(h: Hypotheses) -> float | None:
    """Commandes/jour necessaires pour couvrir les charges fixes. None si impossible."""
    c = contribution(h)
    if c <= 0:
        return None
    fixe = h.charges_fixes_mensuelles + h.budget_marketing_mensuel
    return fixe / c / 30.0


def resultat_mensuel(h: Hypotheses) -> float:
    volume = h.commandes_par_jour * 30
    return contribution(h) * volume - h.charges_fixes_mensuelles - h.budget_marketing_mensuel


def fcfa(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ")


def ligne(label: str, valeur: float, largeur: int = 48) -> str:
    """Une ligne 'label ......... valeur' alignee a droite sur 62 colonnes."""
    return f"  {label:<{largeur}}{fcfa(valeur):>12}"


def rapport(h: Hypotheses) -> str:
    volume = h.commandes_par_jour * 30
    enc = encaissement(h)
    lignes = [
        "=" * 64,
        f"SCENARIO : {h.nom}",
        f"           {h.commentaire}",
        "=" * 64,
        "",
        f"  {'Par commande':<48}{'FCFA':>12}",
        "  " + "-" * 60,
        ligne("Panier moyen (GMV)", h.panier_moyen),
        ligne(f"Commission commercant ({h.taux_commission:.0%})",
              h.panier_moyen * h.taux_commission),
        ligne("Frais de livraison factures", h.frais_livraison_client),
        ligne("Frais de service", h.frais_service_client),
        ligne("= Revenu net plateforme", revenu_net(h)),
        "",
        ligne("- Remuneration coursier", -h.remuneration_coursier),
        ligne("- Carburant", -h.carburant_par_course),
        ligne(f"- Commission PSP ({h.taux_psp:.1%} de {fcfa(enc)})", -enc * h.taux_psp),
        ligne("- Support / reconciliation", -h.cout_support),
        ligne(f"- Surcout commandes echouees ({h.taux_echec:.0%})",
              -h.taux_echec * (h.remuneration_coursier + h.carburant_par_course)),
        ligne(f"- Promotions ({h.taux_promo:.0%} du panier)", -promo(h)),
        "  " + "-" * 60,
        ligne("= CONTRIBUTION PAR COMMANDE", contribution(h)),
        f"    soit {contribution(h) / enc:+.1%} de l'encaissement"
        f"  ({contribution(h) / FCFA_PAR_USD:+.2f} USD)",
        "",
        f"  {'Mensuel':<48}{'FCFA':>12}",
        "  " + "-" * 60,
        ligne(f"Volume ({h.commandes_par_jour} commandes/jour)", volume),
        ligne("GMV encaissee", enc * volume),
        ligne("Marge de contribution totale", contribution(h) * volume),
        ligne("Charges fixes (equipe, bureau, tech)", -h.charges_fixes_mensuelles),
        ligne("Marketing d'acquisition", -h.budget_marketing_mensuel),
        "  " + "-" * 60,
        ligne("= RESULTAT MENSUEL", resultat_mensuel(h)),
        "",
    ]
    seuil = seuil_commandes_jour(h)
    if seuil is None:
        lignes += [
            "  >> SEUIL DE RENTABILITE : JAMAIS ATTEINT. La contribution par",
            "     commande est negative : chaque commande supplementaire creuse",
            "     la perte. Le volume n'est pas la solution.",
        ]
    else:
        ecart = seuil / h.commandes_par_jour
        etat = "deja franchi" if ecart <= 1 else f"soit {ecart:.1f}x le volume modelise"
        lignes += [
            f"  >> SEUIL DE RENTABILITE : {fcfa(seuil)} commandes/jour"
            f" ({fcfa(h.commandes_par_jour)} modelisees, {etat})",
        ]
    lignes.append("")
    return "\n".join(lignes)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

# Socle commun d'hypotheses de couts, documente dans etude-marche.md :
#  - carburant : super a 990 FCFA/L (bareme du 15 aout 2026), moto ~2,5 L/100 km,
#    course aller-retour ~12 km => ~0,30 L => ~300 FCFA
#  - PSP : 1,8 a 2,5 % chez les agregateurs locaux (PayDunya), retenu 2,2 %
#  - coursier : ~1 200 FCFA/course, coherent avec un objectif de revenu net
#    quotidien de 12 000 a 15 000 FCFA pour 12 a 14 courses

BASE = Hypotheses(
    nom="",
    commentaire="",
    panier_moyen=8_000,
    taux_commission=0.18,
    frais_livraison_client=1_200,
    frais_service_client=200,
    remuneration_coursier=1_200,
    carburant_par_course=300,
    taux_psp=0.022,
    cout_support=90,
    taux_echec=0.06,
    taux_promo=0.0,
    charges_fixes_mensuelles=4_300_000,
    budget_marketing_mensuel=1_500_000,
    commandes_par_jour=250,
)

SCENARIOS = [
    replace(
        BASE,
        nom="A1 - Marketplace repas, guerre des prix",
        commentaire="Nouvel entrant B2C face a une offre 0 % de commission",
        taux_commission=0.08,
        frais_livraison_client=900,
        taux_promo=0.15,
        budget_marketing_mensuel=4_000_000,
        commandes_par_jour=250,
    ),
    replace(
        BASE,
        nom="A2 - Marketplace repas, prix soutenables",
        commentaire="Commission 18 %, promos contenues : le cas 'discipline'",
        taux_promo=0.05,
        commandes_par_jour=250,
    ),
    replace(
        BASE,
        nom="B - Last-mile B2B e-commerce et PME",
        commentaire="Course facturee au chargeur, pas de commission sur panier",
        panier_moyen=25_000,
        taux_commission=0.0,
        frais_livraison_client=2_500,
        frais_service_client=0,
        remuneration_coursier=1_100,
        carburant_par_course=350,
        taux_psp=0.008,       # encaissement contre remboursement, pas de PSP sur le panier
        cout_support=120,
        taux_echec=0.10,      # taux de reprogrammation plus eleve en colis
        taux_promo=0.0,
        charges_fixes_mensuelles=3_200_000,
        budget_marketing_mensuel=600_000,
        commandes_par_jour=400,
    ),
    replace(
        BASE,
        nom="C - Niche premium / corporate et cantine",
        commentaire="Comptes entreprises, paniers groupes, zero promo",
        panier_moyen=35_000,
        taux_commission=0.12,
        frais_livraison_client=2_000,
        frais_service_client=0,
        remuneration_coursier=1_500,
        carburant_par_course=300,
        taux_psp=0.015,
        cout_support=150,
        taux_echec=0.02,
        taux_promo=0.0,
        charges_fixes_mensuelles=2_600_000,
        budget_marketing_mensuel=400_000,
        commandes_par_jour=90,
    ),
]


def table_sensibilite(h: Hypotheses) -> str:
    """Contribution par commande selon commission et promo, scenario repas."""
    commissions = [0.08, 0.12, 0.15, 0.18, 0.22, 0.25]
    promos = [0.0, 0.05, 0.10, 0.15, 0.20]
    lignes = [
        "=" * 64,
        "SENSIBILITE - contribution par commande (FCFA), marketplace repas",
        f"panier {fcfa(h.panier_moyen)} FCFA,"
        f" livraison {fcfa(h.frais_livraison_client)} FCFA",
        "=" * 64,
        "",
        "  promo \\ commission" + "".join(f"{c:>8.0%}" for c in commissions),
        "  " + "-" * 60,
    ]
    for p in promos:
        cellules = "".join(
            f"{fcfa(contribution(replace(h, taux_commission=c, taux_promo=p))):>8}"
            for c in commissions
        )
        lignes.append(f"  {p:>17.0%}" + cellules)
    lignes += [
        "  " + "-" * 60,
        "  Lecture : sous ~15 % de commission et au-dela de ~10 % de promo,",
        "  la contribution devient negative quel que soit le volume.",
        "",
    ]
    return "\n".join(lignes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sensibilite",
        action="store_true",
        help="affiche la table de sensibilite commission x promotions",
    )
    args = parser.parse_args()

    print()
    print("MODELE D'UNIT ECONOMICS - LIVRAISON A DAKAR")
    print(
        "Monnaie : FCFA (XOF), parite fixe 1 EUR = 655,957 FCFA"
        f" | 1 USD ~ {fcfa(FCFA_PAR_USD)} FCFA"
    )
    print("Hypotheses documentees dans etude-marche.md, section 8.")
    print()
    for h in SCENARIOS:
        print(rapport(h))
    if args.sensibilite:
        print(table_sensibilite(SCENARIOS[1]))


if __name__ == "__main__":
    main()
