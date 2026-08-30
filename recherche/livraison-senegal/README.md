# Recherche — le domaine de la livraison au Sénégal

Étude de marché finalisée le **30 août 2026**.

## Contenu

| Fichier | Description |
|---|---|
| [`etude-marche.md`](etude-marche.md) | L'étude complète : cadrage macro, marché adressable, concurrence, exécution physique, réglementation, unit economics, options stratégiques, risques, plan de terrain. |
| [`unit_economics.py`](unit_economics.py) | Modèle chiffré exécutable. Quatre scénarios + table de sensibilité. Sans dépendance externe. |
| [`sources.md`](sources.md) | Bibliographie complète, classée par niveau de fiabilité (A/B/C), avec la liste des chiffres **écartés** et le motif du rejet. |

## Lancer le modèle

```bash
python3 recherche/livraison-senegal/unit_economics.py               # les 4 scénarios
python3 recherche/livraison-senegal/unit_economics.py --sensibilite # + table commission × promotions
```

Toutes les hypothèses sont des champs de la dataclass `Hypotheses` — les modifier suffit à rejouer un scénario.

## Les trois conclusions

1. **La livraison de repas B2C à Dakar est un piège pour un nouvel entrant.** Marché adressable étroit (13 à 79 M USD de GMV/an, estimation ascendante), Jumia Food y a déjà échoué en 2023, et Yango y pratique 0 % de commission depuis février 2025. Sous 15 % de commission et au-delà de 10 % de promotions, la marge de contribution est négative : le volume aggrave la perte au lieu de la résorber.

2. **La valeur est dans le B2B et le corporate.** Le last-mile pour le e-commerce et les PME est rentable dès ~224 commandes/jour ; le segment premium/corporate l'est dès **27 commandes/jour** — atteignable sans levée de fonds.

3. **Le facteur décisif est réglementaire.** Le décret n° 2024-847 réserve l'agrément des plateformes aux sociétés de droit sénégalais détenues à **≥ 51 % par des ressortissants sénégalais**, et un décret sur la livraison à moto est en préparation. Pour un porteur de projet sénégalais, c'est une barrière à l'entrée favorable.

**Recommandation :** entrer par le corporate/premium, industrialiser ensuite le last-mile B2B, et construire en continu l'actif que personne ne possède — adressage géocodé, réconciliation du paiement à la livraison, conformité des livreurs. Ne pas entrer sur la livraison de repas grand public.

## Trois erreurs répandues que cette étude corrige

- **Glovo n'opère pas au Sénégal** (six pays africains : Nigeria, Kenya, Maroc, Tunisie, Ouganda, Côte d'Ivoire).
- **Jumia Food a fermé au Sénégal début 2023** — Jumia y reste actif sur le e-commerce et la logistique, ce sont deux métiers différents.
- Les « parts de marché » et volumes quotidiens circulant sur les blogs SEO sont **invérifiables et contredits** par les sources primaires. Détail en [`sources.md`](sources.md), section C.

## Avant d'engager du capital

L'étude s'appuie sur des sources publiques. Cinq inconnues ne se lèvent que sur le terrain — elles sont listées avec méthode et durée en section 12 de l'étude. Le critère de décision proposé : engager l'option corporate si et seulement si la prospection produit **au moins 3 lettres d'intention totalisant ≥ 30 commandes/jour**, soit le seuil de rentabilité modélisé, atteint avant le premier franc investi en flotte.
