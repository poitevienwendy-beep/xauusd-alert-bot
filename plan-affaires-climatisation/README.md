# Plan d'affaires — Nettoyage de climatiseurs muraux / thermopompes

Dossier créé en réponse à la demande « Montre-moi mon plan de affaires » : aucun plan
n'existait encore dans ce dépôt, ni ailleurs dans les issues/PR du dépôt. Ce dossier en
crée un, pour le projet identifié par l'utilisateur (nettoyage de climatiseurs muraux —
même secteur que le skill `devis-clim` déjà présent sur ce compte).

| Fichier | Contenu |
|---|---|
| `plan-affaires.md` | Le plan complet : sommaire exécutif, marché, prix, opérations, exigences légales, plan financier, risques, prochaines étapes. |
| `modele_financier.py` | Modèle chiffré exécutable — projection 3 ans, seuil de rentabilité, sensibilité prix. Toutes les hypothèses sont des variables nommées en haut du fichier. Aucune dépendance externe. |
| `sources.md` | Sources des données de marché utilisées, classées par fiabilité, avec les chiffres explicitement écartés et pourquoi. |

## Vérifier les chiffres

```bash
python3 modele_financier.py --sensibilite
```

## À savoir avant d'utiliser ce plan

- Les tarifs utilisés viennent de `references/tarifs.md` du skill `devis-clim`, qui sont
  encore marqués « EXEMPLE » à ce jour — donc les projections financières le sont aussi,
  par construction. La section 9 du plan montre justement l'impact financier important
  d'ajuster ces tarifs vers le marché réel observé au Québec.
- Le nom d'entreprise utilisé (« Thermo-Propre ») est un nom de travail, pas une
  proposition définitive — à remplacer partout par le vrai nom choisi.
- Le point réglementaire RBQ (licence requise ou non pour le nettoyage seul) est signalé
  comme étant à confirmer directement auprès de la Régie du bâtiment du Québec avant de
  démarrer — voir section 3 et 8 du plan, et la mise en garde dans `sources.md`.

Aucune modification du bot XAU/USD existant : l'ajout est entièrement contenu dans ce
nouveau dossier.
