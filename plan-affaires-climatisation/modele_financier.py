#!/usr/bin/env python3
"""
Modèle financier — Plan d'affaires : nettoyage de climatiseurs muraux / thermopompes

Toutes les hypothèses sont regroupées ci-dessous. Remplace-les par tes vrais chiffres
(tarifs réels, coûts réels, capacité réelle) dès que tu les connais — tout le reste du
calcul se met à jour automatiquement.

Usage :
    python3 modele_financier.py                 -> projection 3 ans (scénario tarifs actuels)
    python3 modele_financier.py --sensibilite    -> ajoute la comparaison avec des tarifs alignés marché
"""

import sys

# ============================================================
# 1. GRILLE TARIFAIRE ACTUELLE
#    Source : references/tarifs.md du skill "devis-clim" (marquée EXEMPLE dans ce fichier).
# ============================================================
TARIF_1_UNITE = 139
TARIF_2_UNITES_CH = 129        # $ par unité, si 2 unités nettoyées la même visite
TARIF_3_4_UNITES_CH = 119      # $ par unité
TARIF_5_PLUS_CH = 109          # $ par unité
FRAIS_ZONE_B = 30              # $ forfait déplacement (20-40 km)
PART_VISITES_ZONE_B = 0.20     # hypothèse : 20% des visites hors zone incluse

# Scénario B — tarifs alignés sur le marché observé en 2026 pour ce service au Québec
# (fourchette générale 150-300$/unité, ~180-240$/unité en région de Québec ; voir sources.md).
# Positionnés légèrement sous le haut de fourchette pour rester compétitifs.
TARIF_MARCHE_1_UNITE = 190
TARIF_MARCHE_2_UNITES_CH = 170
TARIF_MARCHE_3_4_UNITES_CH = 155
TARIF_MARCHE_5_PLUS_CH = 140

# ============================================================
# 2. PROFIL DE CLIENTÈLE (répartition des visites selon le nombre d'unités)
#    Hypothèse à ajuster une fois les premières demandes réelles observées.
# ============================================================
MIX_CLIENTELE = {
    1: 0.35,     # 1 unité
    2: 0.35,     # 2 unités
    3.5: 0.20,   # moyenne pour "3 à 4 unités"
    6: 0.10,     # moyenne pour "5 unités et +"
}

# ============================================================
# 3. CAPACITÉ OPÉRATIONNELLE — 1 technicien (le propriétaire), solo
# ============================================================
VISITES_MAX_JOUR_PLEINE_SAISON = 3.5   # capacité technique par jour en pleine saison
JOURS_TRAVAILLES_SEMAINE_PLEINE_SAISON = 5
SEMAINES_PAR_MOIS = 52 / 12

# Indice de demande saisonnière au Québec (1.0 = pleine saison).
# Deux pics (avant-été et fin d'été / avant-saison de chauffe), creux en plein hiver
# et en plein été (unités en marche, moins de rendez-vous acceptés par les clients).
SAISONNALITE = {
    1: 0.3, 2: 0.3, 3: 0.6, 4: 1.3, 5: 1.5, 6: 1.2,
    7: 0.9, 8: 0.9, 9: 1.2, 10: 1.3, 11: 0.6, 12: 0.3,
}

# Taux de remplissage réel du calendrier vs capacité théorique (montée en puissance
# de la notoriété / des réservations, pas de la capacité technique elle-même).
TAUX_REMPLISSAGE = {
    "Année 1": 0.22,
    "Année 2": 0.50,
    "Année 3": 0.75,
}

# ============================================================
# 4. COÛTS
# ============================================================
COUT_FOURNITURE_PAR_UNITE = 6      # produit nettoyant, consommables, par unité nettoyée
COUT_TRANSPORT_PAR_VISITE = 12     # essence, moyenne toutes zones
COUT_USURE_EQUIPEMENT_VISITE = 5   # amortissement approximatif de l'équipement

FRAIS_FIXES_ANNUELS = {
    "Assurance responsabilité civile": 800,
    "Immatriculation / renouvellement REQ": 75,
    "Logiciel facturation / comptabilité": 480,
    "Téléphone / forfait affaires": 360,
    "Entretien véhicule / signalisation (allocation)": 300,
    "Marketing (annonces locales, site web)": 1500,
}
TAUX_CONTINGENCE_FIXES = 0.05

COUTS_DEMARRAGE = {
    "Kit d'équipement (housses de protection, pompe/pulvérisateur, produit serpentins, échelle, aspirateur, EPI)": 1200,
    "Immatriculation entreprise (REQ)": 75,
    "Lettrage / signalisation véhicule": 350,
    "Site web + image de marque (logo, cartes d'affaires)": 900,
    "Outils de gestion (appli de prise de rendez-vous / facturation, mise en place)": 200,
    "Fonds de roulement de départ (coussin ~2 mois de charges fixes + imprévus)": 1000,
}
TAUX_CONTINGENCE_DEMARRAGE = 0.10

REVENU_ANNUEL_CIBLE_PROPRIETAIRE = [40000, 50000, 60000]  # $ de revenu personnel visé, à titre indicatif


# ============================================================
# CALCULS — ne pas modifier au-delà de cette ligne (modifie les hypothèses ci-dessus)
# ============================================================

def tarif_visite(nb_unites, t1, t2, t34, t5):
    if nb_unites <= 1:
        return t1
    if nb_unites <= 2:
        return t2 * nb_unites
    if nb_unites <= 4:
        return t34 * nb_unites
    return t5 * nb_unites


def revenu_moyen_par_visite(t1, t2, t34, t5):
    base = sum(part * tarif_visite(n, t1, t2, t34, t5) for n, part in MIX_CLIENTELE.items())
    base += PART_VISITES_ZONE_B * FRAIS_ZONE_B
    return base


def unites_moyennes_par_visite():
    return sum(part * n for n, part in MIX_CLIENTELE.items())


def cout_variable_par_visite():
    return (
        unites_moyennes_par_visite() * COUT_FOURNITURE_PAR_UNITE
        + COUT_TRANSPORT_PAR_VISITE
        + COUT_USURE_EQUIPEMENT_VISITE
    )


def frais_fixes_annuels_total():
    sous_total = sum(FRAIS_FIXES_ANNUELS.values())
    return sous_total * (1 + TAUX_CONTINGENCE_FIXES)


def cout_demarrage_total():
    sous_total = sum(COUTS_DEMARRAGE.values())
    return sous_total * (1 + TAUX_CONTINGENCE_DEMARRAGE)


def capacite_pleine_par_mois():
    return VISITES_MAX_JOUR_PLEINE_SAISON * JOURS_TRAVAILLES_SEMAINE_PLEINE_SAISON * SEMAINES_PAR_MOIS


def visites_par_mois(taux_remplissage):
    cap = capacite_pleine_par_mois()
    return {mois: cap * indice * taux_remplissage for mois, indice in SAISONNALITE.items()}


def projection_annee(nom_annee, taux_remplissage, t1, t2, t34, t5):
    visites_mois = visites_par_mois(taux_remplissage)
    total_visites = sum(visites_mois.values())
    revenu_visite = revenu_moyen_par_visite(t1, t2, t34, t5)
    revenu_total = total_visites * revenu_visite
    cout_var_total = total_visites * cout_variable_par_visite()
    fixes = frais_fixes_annuels_total()
    marge_brute = revenu_total - cout_var_total
    resultat_avant_salaire = marge_brute - fixes
    return {
        "annee": nom_annee,
        "visites_mois": visites_mois,
        "total_visites": total_visites,
        "revenu_moyen_visite": revenu_visite,
        "revenu_total": revenu_total,
        "cout_variable_total": cout_var_total,
        "frais_fixes": fixes,
        "marge_brute": marge_brute,
        "resultat_avant_salaire": resultat_avant_salaire,
    }


def visites_pour_cible(cible_revenu_perso, t1, t2, t34, t5):
    revenu_visite = revenu_moyen_par_visite(t1, t2, t34, t5)
    cout_var = cout_variable_par_visite()
    marge_par_visite = revenu_visite - cout_var
    fixes = frais_fixes_annuels_total()
    return (cible_revenu_perso + fixes) / marge_par_visite


def afficher_projection(p):
    print(f"\n=== {p['annee']} ===")
    print(f"Visites totales                : {p['total_visites']:.0f}")
    print(f"Revenu moyen / visite           : {p['revenu_moyen_visite']:.2f} $")
    print(f"Revenu total                    : {p['revenu_total']:.0f} $")
    print(f"Coûts variables totaux          : {p['cout_variable_total']:.0f} $")
    print(f"Marge brute                     : {p['marge_brute']:.0f} $")
    print(f"Frais fixes annuels             : {p['frais_fixes']:.0f} $")
    print(f"Résultat avant salaire du propriétaire : {p['resultat_avant_salaire']:.0f} $")


def main():
    sensibilite = "--sensibilite" in sys.argv

    print("=" * 70)
    print("PLAN D'AFFAIRES — NETTOYAGE DE CLIMATISEURS MURAUX / THERMOPOMPES")
    print("=" * 70)

    print(f"\nUnités moyennes par visite      : {unites_moyennes_par_visite():.2f}")
    print(f"Coût variable moyen / visite    : {cout_variable_par_visite():.2f} $")
    print(f"Frais fixes annuels (avec {TAUX_CONTINGENCE_FIXES*100:.0f}% de contingence) : {frais_fixes_annuels_total():.0f} $")
    print(f"Coût de démarrage total (avec {TAUX_CONTINGENCE_DEMARRAGE*100:.0f}% de contingence)   : {cout_demarrage_total():.0f} $")

    print("\n--- Détail des coûts de démarrage ---")
    for poste, montant in COUTS_DEMARRAGE.items():
        print(f"  - {poste:70s} {montant:>6.0f} $")

    print("\n--- Détail des frais fixes annuels ---")
    for poste, montant in FRAIS_FIXES_ANNUELS.items():
        print(f"  - {poste:70s} {montant:>6.0f} $")

    projections = []
    for annee, taux in TAUX_REMPLISSAGE.items():
        p = projection_annee(annee, taux, TARIF_1_UNITE, TARIF_2_UNITES_CH, TARIF_3_4_UNITES_CH, TARIF_5_PLUS_CH)
        projections.append(p)
        afficher_projection(p)

    fixes = frais_fixes_annuels_total()
    marge_visite = revenu_moyen_par_visite(TARIF_1_UNITE, TARIF_2_UNITES_CH, TARIF_3_4_UNITES_CH, TARIF_5_PLUS_CH) - cout_variable_par_visite()
    seuil_rentabilite_visites = fixes / marge_visite
    print(f"\nSeuil de rentabilité (couvrir uniquement les frais fixes) : {seuil_rentabilite_visites:.1f} visites/an")

    print("\n--- Visites nécessaires pour atteindre un revenu personnel cible (avant impôt) ---")
    for cible in REVENU_ANNUEL_CIBLE_PROPRIETAIRE:
        n = visites_pour_cible(cible, TARIF_1_UNITE, TARIF_2_UNITES_CH, TARIF_3_4_UNITES_CH, TARIF_5_PLUS_CH)
        print(f"  Cible {cible:>6.0f} $/an -> {n:.0f} visites/an ({n/52:.1f}/semaine en moyenne)")

    if sensibilite:
        print("\n" + "=" * 70)
        print("SENSIBILITÉ — TARIFS ACTUELS vs TARIFS ALIGNÉS MARCHÉ")
        print("(voir sources.md : fourchette marché observée 150-300 $/unité, ~180-240 $ région de Québec)")
        print("=" * 70)
        revenu_actuel = revenu_moyen_par_visite(TARIF_1_UNITE, TARIF_2_UNITES_CH, TARIF_3_4_UNITES_CH, TARIF_5_PLUS_CH)
        revenu_marche = revenu_moyen_par_visite(TARIF_MARCHE_1_UNITE, TARIF_MARCHE_2_UNITES_CH, TARIF_MARCHE_3_4_UNITES_CH, TARIF_MARCHE_5_PLUS_CH)
        ecart = revenu_marche - revenu_actuel
        ecart_pct = ecart / revenu_actuel * 100
        print(f"\nRevenu moyen / visite - tarifs actuels  : {revenu_actuel:.2f} $")
        print(f"Revenu moyen / visite - tarifs marché    : {revenu_marche:.2f} $")
        print(f"Écart                                     : +{ecart:.2f} $/visite  (+{ecart_pct:.1f}%)")

        print("\nImpact sur le résultat annuel, à volume de visites égal :")
        for p in projections:
            taux = TAUX_REMPLISSAGE[p["annee"]]
            p_marche = projection_annee(p["annee"], taux, TARIF_MARCHE_1_UNITE, TARIF_MARCHE_2_UNITES_CH, TARIF_MARCHE_3_4_UNITES_CH, TARIF_MARCHE_5_PLUS_CH)
            delta_resultat = p_marche["resultat_avant_salaire"] - p["resultat_avant_salaire"]
            print(f"  {p['annee']:10s} : résultat actuel {p['resultat_avant_salaire']:>8.0f} $  ->  résultat tarifs marché {p_marche['resultat_avant_salaire']:>8.0f} $  (+{delta_resultat:.0f} $)")

    print("\nRappel : toutes les hypothèses (tarifs, mix de clientèle, capacité, coûts) sont")
    print("regroupées en haut de ce fichier. Ajuste-les dès que tu as des chiffres réels.")


if __name__ == "__main__":
    main()
