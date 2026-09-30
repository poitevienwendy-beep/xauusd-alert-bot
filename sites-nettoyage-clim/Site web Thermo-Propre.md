---
projet: Nettoyage de climatiseurs muraux
statut: en cours
mis-a-jour: 2026-09-29
tags: [site-web, thermo-propre, climatisation]
---

# Site web Thermo-Propre

Site vitrine pour l'entreprise de nettoyage de climatiseurs muraux et de thermopompes. « Thermo-Propre » est un nom de travail, pas encore le nom officiel.

## Version retenue : Air sain

- Fichier : `f-air-sain.html` (s'ouvre directement dans un navigateur ; garder le dossier `img/` à côté)
- Aperçu en ligne (privé) : https://claude.ai/artifact/ACvyfGRjqDUiUubey6QHxs
- Style : blanc et aqua, aéré, axé sur la santé de la famille. Titre : « L'air que votre famille respire passe par ici. »

### Contenu de la page
1. Accueil avec photo de la chambre d'enfant et carte « Une nuit plus saine » (placée pour ne jamais cacher l'enfant, sur ordinateur comme sur téléphone)
2. Ce qu'on retire de votre appareil : filtre saturé, turbine moisie, résultat après
3. Trois avantages avec illustrations à l'encre : air plus sain, moins d'électricité, fini les gouttes au mur
4. Comment se passe la visite : technicien sur escabeau, puis fin de visite avec la cliente sur la tablette (5 étapes)
5. Quand faire nettoyer : printemps (avant la clim) et automne (avant le chauffage)
6. Réservation en 3 étapes avec soumission calculée en direct (appareils, état et options, coordonnées et plage horaire)
7. Zone desservie, engagements, bande photo, prix, FAQ (8 questions), pied de page complet
8. Sur téléphone : barre « Appeler / Réserver » fixée en bas
9. Menu (trois barres) en haut à droite, sur ordinateur et mobile : accès direct à toutes les sections ; l'en-tête reste visible pendant le défilement

### Décisions prises
- Pas d'icônes génériques ni d'émojis : remplacés par des illustrations dessinées dans la palette du site
- Photos réalistes : la tête murale est installée près du plafond, le technicien travaille sur un escabeau
- La 2e photo du déroulement montre la fin de visite avec la cliente (photos avant/après sur tablette), pas le nettoyage une deuxième fois
- Inspiré de gorrie.com : « Comment se passe la visite » raconté au défilement (sur ordinateur, la photo reste fixe et change à chaque étape ; sur mobile, une photo par étape), bande des marques de thermopompes qui défile, et engagements en deux bandeaux inclinés
- Les photos du déroulement suivent le même appareil du début à la fin (filtre, rinçage, résultat)
- Inspiré de pureclim.com : rapport d'entretien daté avec photos avant/après remis après chaque visite (argument garantie du fabricant), section « Pour qui ? » avec bloc immeubles et copropriétés (soumission de volume dès 10 unités), bannière « Tarifs de lancement », engagements concrets (pas de vendeur, rappel dans la journée, rapport après chaque visite)
- « Ce qu'on retire » : les trois photos montrent le même appareil, avec une saleté légère et crédible (environ un an sans nettoyage professionnel) et une légende honnête. À remplacer par de vraies photos avant/après des premiers clients (avec leur accord)

## À compléter avant la mise en ligne
- [ ] Vrais prix (dans le vault) : le site utilise pour l'instant la grille du skill devis-clim, marquée EXEMPLE : 139 / 129 / 119 / 109 $ par appareil ; options +39 $ désinfection, +25 $ anti-moisissure, +25 $ accès difficile, +59 $ unité extérieure ; zone B +30 $ ; TPS + TVQ ; minimum 120 $
- [ ] Nom officiel de l'entreprise
- [ ] Vrai téléphone et courriel (514 555-0142 est fictif)
- [ ] Heures d'ouverture et villes desservies réelles
- [ ] Où envoyer les demandes de réservation (courriel ou outil de réservation) : le formulaire n'envoie rien pour l'instant
- [x] Aperçu en ligne sur Netlify : https://thermo-propre-apercu.netlify.app (projet « thermo-propre-apercu », non référencé par Google)
- [ ] Mise en ligne finale : nom de domaine, retirer le « noindex », renommer le projet selon la marque choisie
- [ ] Confirmer les engagements affichés : rappel dans la journée, pas de vendeur, rapport envoyé le jour même, seuil de 10 unités pour la soumission de volume
- [ ] Définir l'offre de lancement (durée, conditions) et l'outil qui produira le rapport d'entretien (ex. Jobber)

Pour mémoire, le plan d'affaires suggère une grille alignée sur le marché québécois après le lancement : 190 / 170 / 155 / 140 $.

## Autres versions essayées (non retenues)
- 1re série sans photos : `a-fiche-de-service.html`, `b-la-turbine.html`, `c-deux-saisons.html`
- 2e série avec photos : `d-premium.html`, `e-energique.html`

## Où se trouve le code
- Dépôt GitHub : poitevienwendy-beep/xauusd-alert-bot, branche `claude/ac-cleaning-website-examples-er8fet`, dossier `sites-nettoyage-clim/`
- Pull request : https://github.com/poitevienwendy-beep/xauusd-alert-bot/pull/7
- Photos et illustrations générées avec Higgsfield (dossier `img/`)
