# Plan d'affaires — Nettoyage de climatiseurs muraux et thermopompes

> **Nom de travail utilisé dans ce document : « Thermo-Propre »**
> Aucun nom réel n'a été fourni — remplace-le partout par le nom officiel de ton
> entreprise (idéalement le même que celui que tu inscriras dans
> `references/entreprise.md` du skill `devis-clim`, pour que devis et plan restent cohérents).
>
> Ce document part des tarifs déjà présents dans `references/tarifs.md` (encore marqués
> « EXEMPLE ») et des recherches de marché résumées dans `sources.md`. Chaque hypothèse
> qui n'est pas une donnée sourcée est signalée comme telle — à toi de la remplacer par
> tes chiffres réels au fil du démarrage.

---

## 1. Sommaire exécutif

**Thermo-Propre** est une entreprise individuelle de services offrant le nettoyage
professionnel de climatiseurs muraux, thermopompes et mini-splits résidentiels, avec
options de désinfection et d'entretien de l'unité extérieure.

Le marché est porté par un facteur structurel fort : l'adoption de thermopompes murales a
explosé au Québec ces dernières années — **148 687 thermopompes ont reçu une aide
financière provinciale en 2025, une hausse de 97 % par rapport à 2024** (donnée reprise de
la presse spécialisée, voir `sources.md`). Chaque appareil installé devient, un ou deux ans
plus tard, un client potentiel pour l'entretien : le marché ne dépend donc pas seulement des
nouvelles installations, mais d'un **parc installé qui grossit vite et qui a besoin d'un
entretien régulier** (nettoyage complet recommandé une fois par an en usage
chauffage + climatisation, ou tous les deux ans en climatisation estivale seule).

Le modèle d'affaires est volontairement simple et à faible capital de départ :
un technicien (le propriétaire), un véhicule, un kit d'équipement de nettoyage, et une
grille tarifaire dégressive selon le nombre d'unités nettoyées par visite.

**Chiffres clés du plan financier (détails section 9, calculs vérifiables dans
`modele_financier.py`) :**

| | Année 1 | Année 2 | Année 3 |
|---|---|---|---|
| Visites | 174 | 394 | 592 |
| Revenu total | 50 950 $ | 115 796 $ | 173 694 $ |
| Résultat avant revenu du propriétaire | 41 863 $ | 99 841 $ | 151 608 $ |

Coût de démarrage estimé : **~4 100 $**. Seuil de rentabilité : **~14 visites/an**
(structure à coûts fixes très bas — le vrai enjeu n'est pas de « survivre », c'est de
remplir l'agenda).

**Constat stratégique le plus important de ce plan** : les tarifs actuels
(`tarifs.md`, marqués EXEMPLE — 139 $ pour 1 unité, 109-129 $/unité en volume) se situent
**nettement sous le marché observé au Québec**, où des concurrents facturent couramment
150 $ à 300 $ par unité (180-240 $ en région de Québec). Voir section 5.2 : un
repositionnement progressif vers ces niveaux, à volume égal, ajouterait environ
**+53 000 $/an** de résultat dès l'année 3 sans travailler plus.

---

## 2. Présentation de l'entreprise

- **Nom** : Thermo-Propre *(à remplacer)*
- **Forme juridique proposée** : entreprise individuelle (immatriculée au Registraire des
  entreprises du Québec). C'est la structure la plus simple et la moins coûteuse pour
  démarrer seul avec un risque de responsabilité limité par une bonne assurance ; une
  incorporation (société par actions) peut être envisagée plus tard si le chiffre
  d'affaires ou le risque perçu augmentent, ou si un deuxième technicien est embauché.
  *(À valider avec un comptable/notaire selon ta situation personnelle.)*
- **Mission** : redonner à un climatiseur mural ou une thermopompe son efficacité et sa
  salubrité (poussière, bactéries, moisissures) par un nettoyage professionnel accessible,
  sans les délais et les tarifs des entreprises d'installation généralistes.
- **Zone desservie** : à définir dans `references/entreprise.md` — ce plan utilise
  l'exemple « Zone A : Montréal + 20 km (inclus) / Zone B : 20-40 km (+30 $) » déjà présent
  dans le skill.
- **Stade actuel** : pré-démarrage. Les fichiers de configuration du skill de devis
  (`tarifs.md`, `entreprise.md`) existent déjà mais contiennent encore des valeurs
  d'exemple — les remplir est la première étape concrète issue de ce plan (section 10).

---

## 3. Produits et services offerts

| Service | Description | Tarif de référence (EXEMPLE, `tarifs.md`) |
|---|---|---|
| Nettoyage unité murale — 1 unité | Nettoyage complet du filtre, du serpentin et du boîtier | 139 $ |
| Nettoyage — 2 unités | Tarif dégressif | 129 $/unité |
| Nettoyage — 3 à 4 unités | Tarif dégressif | 119 $/unité |
| Nettoyage — 5 unités et + | Tarif dégressif (conversions chauffage multi-zones) | 109 $/unité |
| Option — Désinfection / traitement antibactérien | Sur demande ou si l'état le justifie | +39 $/unité |
| Option — Traitement anti-moisissure renforcé | Si moisissure visible/odeur | +25 $/unité |
| Option — Nettoyage unité extérieure (condenseur) | Complément saisonnier | +59 $ |
| Option — Accès difficile | Hauteur, plafond > 3 m | +25 $/unité |

**Ce que l'entreprise ne fait pas (volontairement, au départ)** : toute intervention sur
le circuit de réfrigérant (vérification de pression, recharge) — ces actes sont réservés
aux détenteurs d'une licence RBQ (sous-catégories 15.9/15.10) et d'une accréditation
fédérale sur les halocarbures. Rester sur le nettoyage seul permet de démarrer sans cette
licence, tout en laissant la porte ouverte à l'obtenir plus tard si l'entreprise veut
élargir vers l'entretien complet avec recharge (voir section 11 — croissance). **À
confirmer directement auprès de la RBQ avant de démarrer** : la classification exacte de
ce qui constitue ou non un « travaux de construction » réglementé peut comporter des
nuances (voir `sources.md`).

**Piste de service récurrent** : proposer un forfait d'entretien annuel ou biannuel
(rappel automatique au client) plutôt que de dépendre uniquement de demandes ponctuelles —
cohérent avec la fréquence de nettoyage recommandée par les fabricants et installateurs
(1×/an en usage chauffage+climatisation, 1×/2 ans en climatisation estivale seule).

---

## 4. Analyse de marché

### 4.1 Tendance de fond : un parc installé en forte croissance

- La thermopompe murale (mini-split) est devenue au Québec une solution à la fois de
  climatisation ET de chauffage (remplacement du chauffage électrique classique), portée
  par les programmes **Chauffez Vert** (jusqu'à 1 275 $ par maison unifamiliale pour
  remplacer un chauffage au mazout/propane/gaz, se termine le 31 mars 2026) et
  **LogisVert** d'Hydro-Québec (50 $ à 120 $ par 1000 BTU/h selon le type d'appareil).
- Conséquence directe pour ce projet : chaque thermopompe installée est un **futur client
  d'entretien**, indépendamment de la poursuite ou non des subventions à l'achat — le
  parc déjà installé continuera d'avoir besoin de nettoyage même après la fin des
  programmes de subvention en mars 2026. C'est une base de revenu récurrent qui ne dépend
  pas d'un seul cycle de subvention.
- Cet usage double (chauffage + climatisation) réduit aussi la saisonnalité pure d'une
  activité qui, historiquement, ne dépendait que des étés chauds.

### 4.2 Clientèle cible

- **Propriétaires résidentiels** ayant 1 à 6 têtes murales (le cas le plus fréquent),
  particulièrement ceux ayant converti leur chauffage (donc plusieurs unités, un usage
  intensif toute l'année, et une sensibilité à l'efficacité énergétique — un climatiseur
  encrassé consomme plus).
- **Propriétaires ayant observé un signal d'alerte** : odeur de moisi au démarrage, baisse
  de puissance, allergies dans le foyer, achat d'une maison avec thermopompe existante
  sans historique d'entretien.
- **Gestionnaires de petits immeubles / copropriétés** avec plusieurs unités murales — plus
  gros volume par visite (tarif dégressif justement conçu pour ce cas), pertinent pour la
  section suivante.

### 4.3 Concurrence

Les recherches confirment l'existence d'une concurrence directe déjà active au Québec :
plusieurs entreprises spécialisées en nettoyage de thermopompes/climatiseurs muraux
opèrent dans la province (ex. offres identifiées dans la région de Québec), en plus des
entreprises généralistes de climatisation/chauffage qui proposent l'entretien comme
service secondaire. Aucune donnée fiable sur leurs volumes ou parts de marché n'a été
trouvée (et n'est donc pas inventée ici) — mais deux choses ressortent :

1. **Le concurrent le plus important n'est probablement pas une autre entreprise, c'est
   l'inaction** : beaucoup de propriétaires ignorent simplement qu'un nettoyage complet
   (au-delà du filtre qu'ils rincent eux-mêmes) est recommandé. Une partie du travail
   marketing est donc de l'**éducation**, pas seulement de la conquête de clients d'un
   concurrent.
2. **Les prix affichés par la concurrence sont significativement plus élevés** que la
   grille EXEMPLE actuelle — voir 5.2. C'est à la fois une opportunité (se positionner
   moins cher pour percer) et un risque (des tarifs trop bas peuvent signaler un service
   moins sérieux, ou simplement laisser de l'argent sur la table).

### 4.4 Réglementation et barrières à l'entrée

- **RBQ** : licence requise seulement pour les interventions sur le circuit de
  réfrigérant, pas (a priori) pour le nettoyage seul — à confirmer directement avec la
  RBQ avant de s'engager (voir 3 et `sources.md`).
- **Immatriculation d'entreprise** : obligatoire au Registraire des entreprises du Québec
  dès qu'on opère sous un nom autre que son propre nom légal.
- **Assurance responsabilité civile** : fortement recommandée (accès au domicile des
  clients, manipulation d'équipement électrique/électronique) — coût estimé 500-1 500 $/an
  pour une structure de cette taille, à confirmer avec un courtier.
- **TPS/TVQ** : inscription obligatoire seulement après 30 000 $ de revenu sur 12 mois
  glissants (statut de « petit fournisseur » en deçà) — donc probablement pas nécessaire
  dès le premier mois, mais à surveiller dès que l'activité décolle.

Ces barrières sont **basses** comparées à l'installation ou la vente d'équipement — ce qui
explique pourquoi de nouveaux entrants sont possibles, mais aussi pourquoi la différenciation
doit venir du service (fiabilité, rapidité de réponse, qualité perçue) plutôt que d'une
barrière réglementaire.

---

## 5. Stratégie marketing et prix

### 5.1 Positionnement

« Le nettoyage professionnel de ta thermopompe, réservé en 5 minutes, fait pendant que tu
es à la maison ou au travail — sans les délais des entreprises de climatisation. »
L'angle différenciant proposé : **spécialiste du nettoyage seul** (donc plus rapide à
réserver et souvent moins cher qu'une entreprise généraliste d'installation/entretien qui
traite le nettoyage comme un service secondaire).

### 5.2 Prix — l'écart avec le marché à corriger progressivement

| | 1 unité | 2 unités (ch.) | 3-4 unités (ch.) | 5+ unités (ch.) |
|---|---|---|---|---|
| **Grille actuelle** (`tarifs.md`, EXEMPLE) | 139 $ | 129 $ | 119 $ | 109 $ |
| **Marché observé au Québec** (voir `sources.md`) | 150-300 $ (≈180-240 $ région de Québec) | — | — | — |

Recommandation : **ne pas nécessairement copier le haut de la fourchette dès le jour 1**
(un prix d'appel aide à bâtir les premiers avis et la notoriété), mais éviter de rester
indéfiniment 30-40 % sous le marché une fois la réputation établie. Une trajectoire
raisonnable :
- **Lancement (0-6 mois)** : grille actuelle ou légèrement au-dessus, présentée comme
  « tarif de lancement », pour accumuler rapidement des avis Google/Facebook.
- **Après les premiers avis positifs (6-18 mois)** : ajustement vers le milieu de la
  fourchette marché (voir scénario B du modèle financier, section 9.3).
- **Une fois la notoriété locale établie** : aligner sur le marché, en réservant les
  tarifs les plus bas aux gros volumes (immeubles, conversions multi-zones) où le
  tarif dégressif reste un argument de vente légitime.

### 5.3 Canaux d'acquisition

- **Fiche Google Business Profile** optimisée (mots-clés : « nettoyage thermopompe
  [ville] », « nettoyage climatiseur mural [ville] ») — canal à fort ROI pour un service
  local, coût quasi nul hors temps investi.
- **Publicités locales ciblées** (Meta/Google Ads géolocalisées, budget mensuel modeste —
  voir frais fixes section 9).
- **Partenariats** avec de petites entreprises d'installation de thermopompes qui
  n'offrent pas ou peu d'entretien après-vente — elles ont déjà la liste de clients ayant
  une unité installée depuis 1-2 ans.
- **Rappels de fidélisation** : puisque le nettoyage recommandé est annuel ou biannuel,
  un simple rappel automatisé (SMS/courriel) 12 mois après chaque visite transforme un
  client ponctuel en revenu récurrent — c'est le levier de croissance le moins coûteux du
  plan.
- **Bouche-à-oreille / référencement client** : rabais de parrainage simple (ex. 10 % pour
  le client référent et le nouveau client) une fois la base de clients établie.

### 5.4 Saisonnalité et communication

La demande suit deux pics (avant-été et fin d'été/avant-saison de chauffe) avec un creux
en plein hiver et en plein été — voir modèle section 9. La communication marketing doit
donc pousser plus fort en mars-avril et en août-septembre, et peut se concentrer sur les
grands comptes (immeubles, entretiens groupés) pendant les mois plus creux de
janvier-février.

---

## 6. Plan des opérations

- **Prise de rendez-vous** : téléphone/SMS/formulaire web, idéalement avec un outil de
  calendrier en ligne simple pour réduire les allers-retours.
- **Déroulement d'une visite type** : confirmation la veille → déplacement → protection de
  la zone de travail → nettoyage filtre/serpentin/boîtier (± options) → test de
  fonctionnement → paiement sur place → photo avant/après pour le suivi qualité et le
  marketing (avec accord du client).
- **Équipement** (voir coûts détaillés section 9.1) : housses de protection étanches pour
  nettoyage in situ, pompe/pulvérisateur, produit nettoyant serpentins biodégradable,
  échelle ou perche télescopique pour les unités en hauteur, aspirateur d'atelier,
  équipement de protection individuelle.
- **Fournisseurs** : produits d'entretien spécialisés HVAC disponibles chez les
  distributeurs de pièces de climatisation/chauffage ou en ligne — pas de fournisseur
  exclusif requis, ce qui limite le risque d'approvisionnement.
- **Capacité** : un seul technicien (le propriétaire) au départ ; le modèle financier
  (section 9) prévoit explicitement le moment où la demande dépasse la capacité solo
  (autour de l'année 3), ce qui devient le déclencheur d'embauche plutôt qu'une décision
  arbitraire.

---

## 7. Organisation et ressources humaines

- **Année 1-2** : propriétaire unique, toutes les fonctions (technique, ventes,
  administration).
- **Année 3+ (si la demande le justifie, voir 9.2)** : embauche d'un deuxième technicien
  ou d'un apprenti à temps partiel pour absorber la demande en haute saison, avant
  d'envisager un statut d'employeur à temps plein.
- **Sous-traitance possible dès le départ** pour les tâches hors expertise : comptabilité
  (tenue de livres), création du site web/logo si non fait soi-même.

---

## 8. Exigences légales et administratives — liste de démarrage

1. Choisir et vérifier la disponibilité du nom d'entreprise.
2. Immatriculer l'entreprise individuelle au Registraire des entreprises du Québec.
3. **Confirmer directement auprès de la RBQ** si le nettoyage seul (sans ouverture du
   circuit de réfrigérant) nécessite une licence dans ta situation précise — ne pas se
   fier uniquement à ce document pour cette question.
4. Souscrire une assurance responsabilité civile professionnelle (obtenir au moins deux
   soumissions de courtiers).
5. Ouvrir un compte bancaire professionnel séparé.
6. Mettre en place un outil de facturation/comptabilité simple dès la première vente (pas
   après coup).
7. Remplir enfin pour de vrai `references/tarifs.md` et `references/entreprise.md` du
   skill `devis-clim` avec les vraies informations (actuellement marquées EXEMPLE/À
   REMPLIR) — le skill de devis ne produira des soumissions fiables qu'à partir de là.
8. Surveiller le seuil de 30 000 $ de revenu annuel pour l'inscription obligatoire aux
   fichiers de la TPS/TVQ (facultatif en deçà, statut de petit fournisseur).

---

## 9. Plan financier

Tous les calculs ci-dessous sont reproductibles avec :
```bash
python3 modele_financier.py --sensibilite
```
Chaque hypothèse (tarifs, mix de clientèle, capacité par jour, coûts) est une variable
nommée en haut du fichier — modifie-les dès que tu as des chiffres réels et relance le
script pour mettre à jour toute la suite des calculs.

### 9.1 Coût de démarrage estimé : ~4 100 $

| Poste | Montant |
|---|---|
| Kit d'équipement (housses de protection, pompe/pulvérisateur, produit serpentins, échelle, aspirateur, EPI) | 1 200 $ |
| Immatriculation entreprise (REQ) | 75 $ *(montant à confirmer — voir sources.md)* |
| Lettrage / signalisation véhicule | 350 $ |
| Site web + image de marque (logo, cartes d'affaires) | 900 $ |
| Outils de gestion (appli de rendez-vous/facturation) | 200 $ |
| Fonds de roulement de départ (≈2 mois de charges fixes) | 1 000 $ |
| **Sous-total** | **3 725 $** |
| Contingence (10 %) | 373 $ |
| **Total** | **4 098 $** |

Capital modeste, cohérent avec un métier où l'actif principal est le temps et le savoir-
faire du propriétaire, pas de l'équipement lourd. Financement envisageable par épargne
personnelle, marge de crédit personnelle, ou micro-prêt (BDC, Desjardins Entreprises,
organismes de microcrédit régionaux) — à explorer si l'apport personnel est insuffisant.

### 9.2 Projection 3 ans

**Hypothèses de capacité [Hypothèse — à ajuster]** : 1 technicien, capacité max 3,5
visites/jour en pleine saison, 5 jours/semaine ; taux de remplissage réel de l'agenda
(pas la capacité technique) de 22 % en année 1 (notoriété à bâtir), 50 % en année 2, 75 %
en année 3.

| | Année 1 | Année 2 | Année 3 |
|---|---:|---:|---:|
| Visites/an | 174 | 394 | 592 |
| Revenu moyen/visite | 293,65 $ | 293,65 $ | 293,65 $ |
| **Revenu total** | **50 950 $** | **115 796 $** | **173 694 $** |
| Coûts variables (fournitures, transport, usure) | 5 396 $ | 12 264 $ | 18 396 $ |
| Marge brute | 45 554 $ | 103 532 $ | 155 298 $ |
| Frais fixes annuels | 3 691 $ | 3 691 $ | 3 691 $ |
| **Résultat avant revenu du propriétaire** | **41 863 $** | **99 841 $** | **151 608 $** |

> Pour une entreprise individuelle solo, ce « résultat avant revenu du propriétaire » est,
> avant impôt, le revenu personnel réellement disponible pour le propriétaire — puisque son
> propre temps n'est pas comptabilisé comme une charge distincte. Il devient une vraie
> charge salariale seulement le jour où un deuxième technicien est embauché (section 7).

À 592 visites/an en année 3 (≈11,4/semaine en moyenne annuelle, jusqu'à ~3 visites/jour en
haute saison), l'agenda solo approche sa capacité réaliste — c'est le signal, pas une date
arbitraire, pour évaluer l'embauche d'un deuxième technicien.

### 9.3 Frais fixes annuels : ~3 691 $

| Poste | Montant/an |
|---|---:|
| Assurance responsabilité civile | 800 $ |
| Immatriculation / renouvellement REQ | 75 $ |
| Logiciel facturation / comptabilité | 480 $ |
| Téléphone / forfait affaires | 360 $ |
| Entretien véhicule / signalisation (allocation) | 300 $ |
| Marketing (annonces locales, site web) | 1 500 $ |
| Sous-total | 3 515 $ |
| Contingence (5 %) | 176 $ |
| **Total** | **3 691 $** |

### 9.4 Seuil de rentabilité et revenu cible

- **Seuil de rentabilité (couvrir les frais fixes uniquement)** : ≈ 14 visites/an —
  extrêmement bas, ce qui confirme que le risque principal de ce projet n'est pas la
  viabilité du modèle, mais la **capacité à remplir l'agenda** (marketing/notoriété).
- **Visites nécessaires pour un revenu personnel cible (avant impôt)** :

| Revenu personnel visé | Visites/an nécessaires | Moyenne/semaine |
|---:|---:|---:|
| 40 000 $ | 166 | 3,2 |
| 50 000 $ | 204 | 3,9 |
| 60 000 $ | 243 | 4,7 |

Un revenu personnel de 40 000-50 000 $ est donc déjà atteignable **dès l'année 1** avec les
hypothèses de ce plan — un signal encourageant, à condition de confirmer le mix de
clientèle et les tarifs réels au fil des premiers mois.

### 9.5 Sensibilité prix — l'effet d'un repositionnement vers le marché

En gardant exactement le même volume de visites (aucun travail supplémentaire), un
repositionnement des tarifs vers le marché observé (190 $ / 170 $ / 155 $ / 140 $ par
palier, contre 139 $ / 129 $ / 119 $ / 109 $ aujourd'hui — voir 5.2) change le résultat
ainsi :

| | Résultat — tarifs actuels | Résultat — tarifs marché | Écart |
|---|---:|---:|---:|
| Année 1 | 41 863 $ | 57 540 $ | +15 676 $ |
| Année 2 | 99 841 $ | 135 469 $ | +35 628 $ |
| Année 3 | 151 608 $ | 205 050 $ | +53 442 $ |

C'est, de loin, le levier financier le plus puissant de ce plan — plus déterminant que le
volume de visites lui-même. Voir la mise en garde de `sources.md` sur l'origine de la
fourchette de marché avant de fixer des tarifs définitifs.

---

## 10. Analyse des risques (FFOM)

| Forces | Faiblesses |
|---|---|
| Coût de démarrage très bas, seuil de rentabilité quasi nul | Dépendance à un seul technicien (le propriétaire) — pas de continuité en cas d'absence/maladie |
| Marché en croissance forte et structurelle (parc de thermopompes) | Pas encore de réputation/avis clients au démarrage |
| Barrières réglementaires basses = démarrage rapide | Activité en partie saisonnière |
| Tarif dégressif adapté aux gros volumes (immeubles) | Tarifs actuels sous le marché (manque à gagner tant qu'ils ne sont pas ajustés) |

| Opportunités | Menaces |
|---|---|
| Revenu récurrent via rappels d'entretien annuel/biannuel | Fin des subventions à l'achat (Chauffez Vert, mars 2026) pourrait ralentir le rythme de *nouvelles* installations — mais n'affecte pas le parc déjà installé qui a besoin d'entretien |
| Partenariats avec installateurs n'offrant pas l'entretien | Concurrents déjà établis avec plus de notoriété locale |
| Extension vers l'entretien complet avec licence RBQ (marché plus large) | Un hiver/été atypique peut décaler la demande saisonnière prévue |
| Segment immeubles/copropriétés pour lisser la saisonnalité | Risque réglementaire si la question RBQ n'est pas confirmée avant de démarrer |

---

## 11. Plan de croissance — prochaines étapes concrètes

1. Remplir `references/tarifs.md` et `references/entreprise.md` avec les vraies données
   (nom, zone, tarifs définitifs de lancement).
2. Confirmer le statut réglementaire exact (RBQ) et obtenir les soumissions d'assurance.
3. Immatriculer l'entreprise et ouvrir le compte bancaire dédié.
4. Créer la fiche Google Business Profile et un site web minimal (même une seule page)
   avant la première campagne publicitaire locale.
5. Lancer avec la grille tarifaire actuelle ou légèrement ajustée, en priorisant
   l'obtention des 10-15 premiers avis clients.
6. Après ~6 mois ou les premiers avis solides, réévaluer les tarifs vers le milieu de la
   fourchette marché (section 5.2/9.5).
7. Mettre en place les rappels automatiques d'entretien annuel dès le premier client.
8. Revoir ce plan et relancer `modele_financier.py` avec les chiffres réels après le
   premier trimestre d'activité — toutes les hypothèses marquées comme telles dans ce
   document sont faites pour être corrigées.
9. Vers l'année 3 (ou plus tôt si l'agenda sature avant), évaluer l'embauche d'un
   deuxième technicien et, en parallèle, la pertinence d'obtenir la licence RBQ pour
   élargir l'offre à l'entretien complet avec recharge de réfrigérant.
