# Le domaine de la livraison au Sénégal — étude de marché

**Version finale — 30 août 2026**
Monnaie : FCFA (XOF), parité fixe avec l'euro (1 EUR = 655,957 FCFA). Conversions au taux 1 USD ≈ 565 FCFA.
Sources et niveaux de fiabilité : voir [`sources.md`](sources.md). Modèle chiffré : [`unit_economics.py`](unit_economics.py).

---

## 1. Résumé exécutif

**Le marché de la livraison au Sénégal est réel et en croissance, mais il n'est pas là où la presse le situe.**

Trois conclusions structurent cette étude :

1. **La livraison de repas B2C à Dakar est un piège pour un nouvel entrant.** Le marché adressable solvable est étroit (13 à 79 M USD de GMV/an, estimation ascendante, cf. §4), Jumia Food y est déjà mort en 2023, et Yango y pratique depuis février 2025 une commission de 0 % pour les restaurateurs, adossée à un bilan de groupe international. Le modèle chiffré (§8) montre qu'en dessous de 15 % de commission et au-delà de 10 % de promotions, la marge de contribution est **négative** : le volume ne sauve rien, il aggrave.

2. **La valeur est dans le B2B et la logistique du dernier kilomètre pour le e-commerce et les PME.** Ce segment est rentable dès ~224 commandes/jour dans le modèle, sans subvention commerciale. Il est porté par une demande vérifiable : Jumia opère ~351 points de ramassage au Sénégal et **47 % de ses commandes viennent de zones secondaires et reculées**. Le segment premium/corporate (§9, scénario C) est cash-flow positif dès **27 commandes/jour** — c'est la tête de pont la plus réaliste.

3. **Le facteur décisif n'est pas la demande, c'est la réglementation.** Le décret n° 2024-847 impose aux plateformes de mise en relation un agrément réservé aux sociétés de droit sénégalais détenues à **≥ 51 % par des ressortissants sénégalais**, avec 15 M FCFA à verser au FDTT et un plafond de 5 000 véhicules par plateforme. Un décret spécifique à la **livraison à moto** est en préparation. Pour un porteur de projet sénégalais, ce n'est pas une contrainte : c'est une barrière à l'entrée qui joue en sa faveur contre les plateformes étrangères.

**Recommandation :** ne pas attaquer le marché des repas grand public. Entrer par le corporate/premium (marge élevée, zéro promo, cash-flow positif à petit volume), industrialiser ensuite le last-mile B2B e-commerce, et construire comme actif défendable la couche que personne ne possède : **adressage fiable + réconciliation du paiement à la livraison + conformité des livreurs**.

---

## 2. Méthode et fiabilité des sources

Ce marché est pollué par du contenu SEO qui invente des chiffres. Plusieurs pages en tête des résultats de recherche affirment par exemple qu'en 2026 le marché dakarois se partage entre « Jumia Express ~30 %, Yango ~22 %, Glovo ~10 % » pour « 25 000 à 40 000 livraisons/jour ». **Ces chiffres sont faux ou invérifiables** : Glovo n'a jamais opéré au Sénégal, et Jumia Food a fermé le pays début 2023 (§5.3).

Chaque affirmation de cette étude est donc classée :

| Niveau | Nature | Exemples |
|---|---|---|
| **A** | Source primaire ou institutionnelle | ANSD, ARTP, DGID, FMI, Journal officiel, communiqués d'entreprise |
| **B** | Presse établie ou spécialisée recoupée | Jeune Afrique, TechCrunch, Agence Ecofin, Le Soleil, Africa Check |
| **C** | Non vérifiable, écarté des conclusions | blogs SEO, agrégateurs sans méthode publiée |

Les estimations propres à cette étude sont signalées **[estimation]** et leur calcul est explicité, pour être contesté.

---

## 3. Cadrage : le pays, l'argent, les tuyaux

### 3.1 Démographie (niveau A — ANSD)

| Indicateur | Valeur | Source |
|---|---|---|
| Population 2025 | **19 075 959** hab. | ANSD, projections sur RGPH-5 (2023) |
| Région de Dakar | **4 157 751** hab. — 21,8 % du pays | ANSD |
| Population urbaine | **55,05 %** (~10,5 M) | ANSD |
| Thiès / Diourbel | 13,56 % / 11,58 % | ANSD |
| Croissance démographique | ~2,5 %/an | ANSD |
| Ménages (RGPH-5, 2023) | **2 059 855**, dont 2 045 436 ordinaires | ANSD |
| Taille moyenne des ménages | 8,6 national · 7,4 urbain · 10,7 rural · **6,2 à Dakar** | ANSD |

Dakar, Thiès et Diourbel concentrent près de la moitié de la population : toute opération de livraison rentable au Sénégal est d'abord une opération sur ce triangle, pas sur les 14 régions.

### 3.2 Macroéconomie : le vent est contraire (niveau A/B — FMI, presse économique)

C'est le point que la plupart des notes d'opportunité sur le Sénégal omettent, et il change les conclusions.

- **Croissance 2025 : 6,7 %**, tirée par une production d'hydrocarbures supérieure aux attentes à Sangomar.
- **Croissance 2026 révisée à 2,2 %** par le FMI (contre 3 % en octobre), **2,3 % en 2027**. L'effet hydrocarbures s'estompe.
- **Inflation 2026 relevée à 2,6 %** (contre 2,0 % prévu).
- **Dette publique : 132 % du PIB fin 2024**, après la découverte d'environ **13 Md USD de dette non déclarée**, qui a conduit le FMI à **suspendre un programme de 1,8 Md USD**.
- **Besoins de financement 2026 : 6 075 Md FCFA, soit 26,2 % du PIB**, dont **71 % au titre du service de la dette**.
- Déficit courant 2026 attendu à **6,2 % du PIB**.

**Conséquence opérationnelle directe :** un État qui doit financer 26 % de son PIB dont 71 % de service de dette cherche des recettes. La TVA numérique de 18 % (§7.3) en est la première manifestation ; d'autres suivront. Et un pouvoir d'achat sous contrainte plafonne le panier moyen d'un service par définition discrétionnaire.

### 3.3 Connectivité : attention au mirage des taux à 125 % (niveau A — ARTP, UIT)

| Indicateur | Valeur | Date |
|---|---|---|
| Abonnements internet mobile | **23,38 M** | déc. 2025 |
| Taux de pénétration internet affiché | **125,78 %** | déc. 2025 |
| Parc internet total (T1 2025) | 21 734 871 lignes — dont 20 950 396 mobile / 784 475 fixe | T1 2025 |
| **Utilisateurs réels d'internet (UIT)** | **60,1 % de la population** | 2024 |

Le régulateur compte des **cartes SIM**, pas des personnes ; le multi-SIM est massif. L'écart entre 125,78 % et 60,1 % n'est pas un détail : **il divise par deux toute estimation de marché fondée sur les chiffres de l'ARTP**. Africa Check a documenté ce biais. Cette étude retient l'ordre de grandeur de l'UIT.

### 3.4 Paiement : Wave a déjà gagné (niveau B)

- **Wave : ~70 % du mobile money au Sénégal** (2025) ; Orange Money ~25 % et en recul.
- **Plus de 70 % des Sénégalais** utilisent le mobile money, dont une majorité de non-bancarisés.
- Wave : transferts P2P gratuits, retraits à 1 % — la pression tarifaire est structurelle.
- Agrégateurs marchands (PayDunya, CinetPay) : **1,8 % à 2,5 %**, négociable au-delà de 50 M FCFA/mois ; coûts observés généralement entre **2 % et 3,5 %**.
- **JumiaPay** est annoncé au Sénégal.

Pour une plateforme de livraison, c'est une bonne nouvelle (encaissement digital possible, pas de dépendance à la bancarisation) et une mauvaise (2 à 3,5 % de commission PSP prélevés sur *tout* l'encaissement, panier compris — ce qui pèse lourd sur une marge par commande de quelques centaines de francs, cf. §8).

---

## 4. Le marché adressable, reconstruit par le bas

### 4.1 Pourquoi ne pas reprendre les chiffres publiés

Deux chiffres circulent :

- Statista : marché « Grocery Delivery – Sénégal » à **177,81 M USD en 2025**, +9,75 %/an, **283,07 M USD en 2030**, 3,5 M d'utilisateurs, ARPU 77,07 USD.
- Repris par la presse à l'occasion du lancement de Yango : **+10,07 % entre 2025 et 2029, pour 269,60 M USD en 2029**.

Ces montants sont des sorties de modèle propriétaire dont la méthode n'est pas publique, et leur périmètre (« grocery delivery ») recouvre vraisemblablement une large part de commerce alimentaire non intermédié par une plateforme. **177 M USD, ce serait environ 100 Md FCFA de GMV livrée par an — soit, au panier observé, plus de 30 000 commandes par jour, tous acteurs confondus.** Rien dans le paysage concurrentiel réel (§5) ne soutient un tel volume. Ces chiffres sont donc écartés.

### 4.2 Estimation ascendante **[estimation]**

| Étape | Hypothèse | Valeur |
|---|---|---|
| Population région de Dakar | ANSD 2025 | 4 157 751 |
| Taille moyenne des ménages à Dakar | RGPH-5 | 6,2 |
| **Ménages à Dakar** | calcul | **≈ 670 600** |
| Part solvable pour une livraison payante récurrente | fourchette retenue | 10 % – 20 % |
| **Ménages cibles** | calcul | **67 000 – 134 000** |
| Fréquence | fourchette retenue | 1 à 3 commandes/mois |
| Encaissement moyen (panier + frais) | §8 | 9 200 FCFA |

**GMV annuelle adressable à Dakar : 7,4 à 44,4 Md FCFA, soit ≈ 13 à 79 M USD.**
**Revenu net des plateformes (take rate ~30 % de l'encaissement) : ≈ 4 à 24 M USD/an, tous acteurs confondus.**

### 4.3 Le plafond de verre : ce que gagne un ménage sénégalais

L'EHCVM-II (ANSD, 2021-2022, 7 120 ménages) donne une **dépense annuelle moyenne de consommation par tête de 542 706 FCFA**, pour un **seuil de pauvreté monétaire à 369 666 FCFA/an**.

542 706 FCFA/an ≈ **1 487 FCFA par personne et par jour**.

Une commande livrée à 9 200 FCFA représente donc **plus de six jours de consommation moyenne par tête**. Ce n'est pas un argument contre le marché — c'est la démonstration que **le marché de la livraison au Sénégal n'est pas un marché de masse**, mais un marché de segments : hauts revenus dakarois, expatriés et diaspora, entreprises, et — sur un tout autre modèle économique — le colis e-commerce, où la livraison est un coût logistique et non un luxe.

C'est exactement la ligne de fracture entre les scénarios A et B/C du §9.

---

## 5. Paysage concurrentiel

### 5.1 Ce qui est établi (niveau A/B)

| Acteur | Depuis | Positionnement | Éléments vérifiés |
|---|---|---|---|
| **Yassir** (Algérie) | bureau à Dakar en **mars 2022** | VTC + livraison de repas + colis + services financiers | Annonçait 200 emplois directs et une expansion Côte d'Ivoire / Bénin / Togo |
| **Yango** (groupe international) | livraison de repas lancée le **25 février 2025** | SuperApp : VTC, livraison, marketplace restaurants | **Commission de 0 % pour les restaurateurs partenaires** (Mammamia, Wonderfood, Pizza Time, Eguettes…) |
| **Paps** (Sénégal) | fondée en **2016** par Bamba Lo | Logistique de bout en bout B2B, colis et documents | **4,5 M USD levés en janvier 2022** (Orange, 4DX Ventures, Proparco, GV, Enza Capital) ; **+10 M de livraisons** revendiquées ; Sénégal + Burkina Faso |
| **Yobante Express** (Sénégal) | — | Colis < 25 kg, réseau de transporteurs et points relais, transfrontalier | **1,2 M USD levés** ; Sénégal, Zimbabwe, Botswana ; filiales Afrique du Sud, Nigeria, Ghana, Zambie |
| **Jumia** | — | E-commerce + logistique propre | CA groupe 2025 **+13 % à 188,9 M USD** ; le Sénégal fait partie des 8 marchés clés ; **~351 points de ramassage** ; **47 % des commandes hors grandes villes** ; JumiaPay annoncé |

### 5.2 Le fait le plus important du marché

**Yango facture 0 % de commission aux restaurants depuis février 2025.**

Cela n'est pas un modèle économique, c'est un prix d'appel financé par un bilan de groupe. Deux conséquences :

- Un entrant indépendant ne peut pas s'aligner : la §8 montre qu'à 8 % de commission avec des promotions, la contribution par commande est de **−1 340 FCFA**, et qu'aucun volume ne la redresse.
- Le jour où Yango normalise sa commission (15-20 %, standard mondial), le marché redevient attaquable — mais Yango aura la base restaurateurs et la base clients. **C'est un signal à surveiller, pas une fenêtre à attendre passivement** (§11).

### 5.3 Trois erreurs répandues à corriger

1. **« Glovo est un concurrent au Sénégal. »** Faux. Glovo opère dans **six pays africains — Nigeria, Kenya, Maroc, Tunisie, Ouganda, Côte d'Ivoire** — a quitté le Ghana en mai 2024 pour raisons de rentabilité et l'Égypte en 2019. Le Sénégal n'a jamais figuré dans son périmètre. Le communiqué de lancement de Yango, largement repris, cite pourtant « Glovo et Jumia Food » comme acteurs établis : c'est inexact.

2. **« Jumia Food est un concurrent. »** Faux. Jumia a fermé la livraison de repas **au Sénégal, au Ghana et en Égypte dès le début 2023**, puis dans sept autres marchés en décembre 2023. Motif officiel : activité sous-critique, **dilution des unit economics, faible valeur vie client**, et concurrence d'acteurs mieux financés pratiquant des remises agressives. *Jumia reste très actif au Sénégal sur le e-commerce et sa logistique — ce sont deux métiers différents.*

3. **« Le marché fait 25 000 à 40 000 livraisons/jour à Dakar. »** Invérifiable, incohérent avec l'estimation ascendante du §4.2, et issu de sources de niveau C.

**L'enseignement de l'échec de Jumia Food est le plus précieux de cette étude :** un opérateur disposant déjà de la marque, du trafic, de la flotte et des points relais au Sénégal a jugé que la livraison de repas y détruisait de la valeur. Un entrant sans ces actifs part avec un handicap, pas un avantage.

---

## 6. L'exécution physique : là où les plans échouent

### 6.1 Les motos, outil de travail à statut incertain (niveau B)

La livraison à Dakar roule sur des motos-taxis appelés localement **« Jakarta »** ou **« tiak-tiak »**, dont la prolifération s'est faite en l'absence de cadre.

- Le ministère des Infrastructures et des Transports (MITTA) a lancé une **campagne d'immatriculation obligatoire** — plaque et carte grise, **coût 28 000 FCFA**, échéance fixée au **25 mai 2025**, avec annonce de sanctions immédiates.
- Dans les faits, **l'échéance est passée et des tiak-tiak non immatriculés continuent de circuler** sans être réellement inquiétés.

Pour un opérateur formel, cette non-application est un **désavantage compétitif** : celui qui met sa flotte en règle paie un coût que ses concurrents informels n'assument pas — jusqu'au jour où la règle est appliquée, et l'avantage s'inverse brutalement.

### 6.2 Le risque le plus sous-estimé : les interdictions de circulation

Les **arrêtés du gouverneur de Dakar interdisant ponctuellement la circulation des motos** lors de rassemblements politiques et d'appels à manifester ont un impact documenté sur le e-commerce de la capitale : les délais de livraison doivent être allongés, les coursiers ne pouvant plus être mobilisés.

C'est un risque d'exploitation d'un genre particulier : **non assurable, non planifiable, corrélé au calendrier politique**, et frappant simultanément 100 % de la flotte. Tout plan d'affaires sérieux doit prévoir un mode dégradé (véhicules 4 roues de secours, points relais, report de créneaux) et ne pas promettre de SLA que la voirie peut annuler.

### 6.3 L'adressage : le coût caché de chaque livraison (niveau A/B)

Au Sénégal, l'orientation repose largement sur des repères informels — une école, une station-service, un rond-point, un commerce du quartier. L'absence d'adresses normalisées rend « **les livraisons plus complexes, plus coûteuses et moins fiables** ».

Le **projet d'Adressage Numérique National (ANN)** a été relancé par le ministère des Télécommunications et du Numérique lors d'un atelier tenu à Dakar **début août 2026**, avec l'objectif d'un référentiel national unique et géoréférencé. Le gouvernement veut **achever une phase pilote sous un an** avant tout déploiement national.

Traduction : **le problème ne sera pas résolu avant 2028 au mieux.** D'ici là, chaque opérateur paie une taxe invisible — appels téléphoniques du coursier, kilomètres perdus, re-livraisons. Celui qui construit sa propre base d'adresses géocodées, commande après commande, se constitue **un actif que ses concurrents ne peuvent pas acheter** (§9, option D).

### 6.4 Le carburant, variable non maîtrisée (niveau A/B)

| Date | Super | Gasoil |
|---|---|---|
| 6 décembre 2025 | 920 FCFA/L (−70) | 680 FCFA/L (−75) |
| **15 août 2026** | **990 FCFA/L** | **755 FCFA/L** |

**+7,6 % sur l'essence en huit mois.** Sur une structure de coûts où le carburant représente ~300 FCFA par course pour une contribution de 550 FCFA (§8), une hausse de 10 % du carburant efface ~5 % de la marge par commande. Les tarifs coursiers doivent être indexés ou renégociables — sans quoi la hausse se traduit par des refus de course.

---

## 7. Réglementation : la vraie barrière à l'entrée

### 7.1 Décret n° 2024-847 — plateformes numériques et VTC (niveau B, texte à vérifier au JO)

| Disposition | Contenu |
|---|---|
| Objet | Réglementation des plateformes numériques de mise en relation et de l'exploitation des VTC |
| Durée de l'agrément | **5 ans**, personnel et non transmissible |
| Forme sociale | Personnes morales **de droit sénégalais** uniquement |
| **Capital** | **≥ 51 % détenu par des ressortissants sénégalais** |
| Droit d'entrée | **15 M FCFA** au Fonds de développement des transports terrestres (FDTT) |
| Plafond de flotte | **5 000 véhicules par plateforme** ; **500 VTC max** par entreprise de transport |
| Recours | Possibilité de compléter le dossier en cas de refus |

**État d'application :** le décret est **en cours de révision** selon le ministre des Transports terrestres et aériens, et **aucune entreprise n'a à ce jour obtenu d'agrément** de VTC — les ajustements réglementaires étant en cours.

**Lecture stratégique.** Trois implications, dans l'ordre d'importance :

1. La règle des 51 % transforme la nationalité du capital en **actif stratégique**. Un porteur de projet sénégalais peut se conformer nativement ; Yango et Yassir doivent restructurer ou négocier.
2. Le plafond de 5 000 véhicules par plateforme empêche mécaniquement la constitution d'un monopole par la taille de flotte — ce qui **préserve une place pour des opérateurs de niche**.
3. Le vide d'agrément actuel signifie que **tous les acteurs opèrent dans une zone grise**. Cela protège les entrants aujourd'hui, mais un rattrapage réglementaire peut arriver du jour au lendemain : le coût de mise en conformité (15 M FCFA + dossier) doit être provisionné dès le départ, pas découvert.

### 7.2 Le décret « livraison à moto » en préparation (niveau B)

Le ministère des Transports prépare **un décret spécifique aux livraisons effectuées à moto**, au motif que ces activités « ne peuvent pas se dérouler sans contrôle ni régulation ».

Parallèlement, la question du **statut des livreurs** est portée politiquement : le député **Guy Marius Sagna** a publiquement interpellé sur les conditions des livreurs et tiak-tiak « notamment dans leur relation avec des plateformes comme Yango ».

**C'est le principal risque à horizon 12-24 mois.** Les scénarios plausibles vont de l'obligation d'assurance et d'immatriculation (coût modéré, absorbable) à une **requalification du lien avec les livreurs** (coût structurel, qui ferait basculer la marge de contribution de tous les scénarios du §8). Toute modélisation financière doit inclure une variante « livreurs salariés ou assimilés ».

### 7.3 Fiscalité (niveau A — DGID)

- **TVA numérique de 18 %** sur les services numériques fournis au Sénégal par les fournisseurs et plateformes **étrangers**, en vigueur **depuis le 1er juillet 2024** (article 355 bis du CGI). Plus d'**1 Md FCFA** collectés la première année. Google s'y conforme depuis le **1er juin 2025** et exige le NINEA ou le n° de registre de commerce de ses clients professionnels.
- Là encore, **l'opérateur local est avantagé** : la mesure vise explicitement à « garantir une concurrence plus équitable entre entreprises locales et multinationales opérant en ligne ».

### 7.4 Incitations : Startup Act et création d'entreprise (niveau A/B)

- **Loi n° 2020-01 du 6 janvier 2020** (Startup Act) : label pour toute entreprise innovante de **moins de 8 ans**, à composante technologique forte, dont **au moins un tiers des investisseurs sont sénégalais** (ou 50 % du capital détenu par des Sénégalais de l'étranger). Avantages : **exonération d'impôts sur 3 ans**, accès facilité à des financements publics, démarches simplifiées pour la commande publique.
- **APIX** : création d'entreprise annoncée en **48 h** via le Bureau de Création d'Entreprise.

### 7.5 Contexte de politique publique : le New Deal Technologique (niveau A)

La stratégie numérique **New Deal Technologique — Horizon 2034** vise **15 % de contribution du numérique au PIB**, **500 startups technologiques reconnues**, **150 000 emplois directs** et 200 000 indirects, autour de 12 projets prioritaires et d'un portefeuille d'investissement d'environ **1 100 Md FCFA entre 2025 et 2034**. Un Conseil national du numérique a été installé.

Pour un projet de logistique numérique sénégalais, c'est un alignement politique exploitable : label startup, marchés publics, et — surtout — le chantier de l'adressage (§6.3) qui figure dans l'agenda de l'État.

---

## 8. Unit economics : le cœur du dossier

Le modèle complet est dans [`unit_economics.py`](unit_economics.py) — chaque hypothèse est un paramètre modifiable. Exécution : `python3 unit_economics.py --sensibilite`.

### 8.1 Hypothèses de coûts (socle commun)

| Poste | Valeur | Justification |
|---|---|---|
| Carburant par course | **300 FCFA** | Super à 990 FCFA/L (barème 15 août 2026), moto ~2,5 L/100 km, course A/R ~12 km ⇒ ~0,30 L |
| Rémunération coursier | **1 200 FCFA** | Cohérent avec un revenu net visé de 12 000 à 15 000 FCFA/jour pour 12-14 courses |
| Commission PSP | **2,2 %** de l'encaissement | Fourchette agrégateurs 1,8-2,5 % (PayDunya), coûts observés 2-3,5 % |
| Support / réconciliation | 90 FCFA/commande | Amorti sur l'équipe support |
| Taux d'échec | 6 % (repas) / 10 % (colis) | Course payée sans revenu |
| Charges fixes | 4,3 M FCFA/mois (repas), 3,2 M (B2B), 2,6 M (premium) | Équipe, bureau, cloud, juridique |

### 8.2 Résultats

| Scénario | Panier | Commission | Promo | **Contribution / commande** | **Seuil de rentabilité** |
|---|---|---|---|---|---|
| **A1** — marketplace repas, guerre des prix | 8 000 | 8 % | 15 % | **−1 340 FCFA** | **jamais atteint** |
| **A2** — marketplace repas, prix soutenables | 8 000 | 18 % | 5 % | **+553 FCFA** | 349 commandes/jour |
| **B** — last-mile B2B e-commerce / PME | 25 000 | 0 % (course facturée) | 0 % | **+565 FCFA** | **224 commandes/jour** |
| **C** — premium / corporate | 35 000 | 12 % | 0 % | **+3 659 FCFA** | **27 commandes/jour** |

### 8.3 Table de sensibilité — marketplace repas

Contribution par commande (FCFA), panier 8 000 FCFA, livraison facturée 1 200 FCFA :

| Promo ↓ / Commission → | 8 % | 12 % | 15 % | 18 % | 22 % | 25 % |
|---|---|---|---|---|---|---|
| **0 %** | 153 | 473 | 713 | 953 | 1 273 | 1 513 |
| **5 %** | −247 | 73 | 313 | 553 | 873 | 1 113 |
| **10 %** | −647 | −327 | −87 | 153 | 473 | 713 |
| **15 %** | −1 047 | −727 | −487 | −247 | 73 | 313 |
| **20 %** | −1 447 | −1 127 | −887 | −647 | −327 | −87 |

**Lecture.** La zone viable est le coin en haut à droite. En dessous de ~15 % de commission et au-delà de ~10 % de promotions, **la contribution devient négative quel que soit le volume**. Or c'est précisément la zone où se situe le marché tant que Yango pratique 0 % côté restaurateurs et finance l'acquisition côté client.

### 8.4 Les trois enseignements du modèle

1. **La marge est mince partout, et c'est normal.** Même le scénario B2B « sain » ne dégage que 565 FCFA (≈ 1 USD) par commande. Ce métier ne pardonne pas l'approximation opérationnelle : un point de taux d'échec en plus, c'est ~15 FCFA de marge en moins par commande, soit près de 3 % de la contribution.
2. **Le panier moyen fait plus que le volume.** Passer de 8 000 à 35 000 FCFA de panier avec zéro promotion multiplie la contribution par **6,6** et divise le seuil de rentabilité par **13**. Chercher des paniers élevés est plus rentable que chercher des commandes nombreuses.
3. **La promotion est le mécanisme qui tue.** À 18 % de commission, passer de 0 % à 20 % de promos fait chuter la contribution de +953 à −647 FCFA. Une plateforme sans capital patient ne peut pas jouer ce jeu, et ne doit donc jamais entrer sur un terrain où il se joue.

---

## 9. Options stratégiques

### Option A — Marketplace de livraison de repas B2C · **à éviter**

Marché adressable étroit (§4), concurrent pratiquant 0 % de commission adossé à un groupe international, précédent d'échec documenté (Jumia Food, sorti en 2023 pour dilution des unit economics), et zone de prix structurellement déficitaire (§8.3). Contribution négative dans les conditions réelles de marché.

### Option B — Last-mile B2B pour le e-commerce et les PME · **moteur de volume**

- **Rentable à 224 commandes/jour**, sans subvention commerciale.
- Demande vérifiable : Jumia opère ~351 points de ramassage au Sénégal et **47 % de ses commandes viennent de zones secondaires et reculées** — c'est-à-dire là où la logistique est la plus difficile et la plus valorisée.
- Concurrence existante et sérieuse : **Paps** (4,5 M USD levés, +10 M de livraisons) et **Yobante Express** (1,2 M USD, réseau de points relais). Entrer ici suppose un angle : géographie (corridor Dakar-Thiès-Touba plutôt que Dakar seul), verticale (pharmacie, pièces détachées, frais), ou qualité de service mesurée (taux de première présentation, délai de reversement du COD).
- Le vrai produit n'est pas la course : c'est **la réconciliation du paiement à la livraison**. Un marchand qui récupère son argent en 24 h avec un relevé propre paie plus cher qu'un marchand qui attend une semaine.

### Option C — Premium, corporate et restauration collective · **tête de pont recommandée**

- **Cash-flow positif dès 27 commandes/jour** — atteignable avec une poignée de comptes entreprises, sans levée de fonds.
- Paniers élevés (35 000 FCFA modélisés : plateaux-repas, commandes groupées de bureau, événements), **zéro promotion**, taux d'échec faible (2 %), facturation mensuelle en compte plutôt qu'encaissement à l'unité.
- Clients : sièges d'entreprises, banques, opérateurs télécoms, ONG et bailleurs, hôtels, ambassades — segment concentré géographiquement (Plateau, Almadies, Diamniadio) et joignable par une force de vente de deux personnes.
- **C'est le seul segment où un entrant peut être rentable avant d'être gros.**

### Option D — Couche d'infrastructure : adressage, COD, conformité · **actif défendable**

Ce que personne ne possède aujourd'hui au Sénégal :

1. **Une base d'adresses géocodées vérifiées par la livraison réelle.** L'ANN de l'État n'aura pas dépassé la phase pilote avant 2027-2028 (§6.3). Une base construite point de livraison par point de livraison devient rapidement le référentiel le plus fiable du pays sur les zones couvertes.
2. **Un moteur de réconciliation du paiement à la livraison**, branché sur Wave et Orange Money via un agrégateur, avec reversement marchand à J+1 et piste d'audit.
3. **Un module de conformité des livreurs** — immatriculation (28 000 FCFA), assurance, pièces — qui deviendra obligatoire dès la publication du décret « livraison à moto » (§7.2).

Ces trois briques se construisent *pendant* l'exploitation de C et B ; elles ne nécessitent pas de financement séparé, et elles sont ce qui rend l'entreprise difficile à copier.

### Séquence recommandée

| Horizon | Action | Jalon de sortie |
|---|---|---|
| **0-6 mois** | Option C. 5 à 10 comptes corporate à Dakar, flotte réduite mise en règle, facturation mensuelle. | 27+ commandes/jour ⇒ cash-flow positif |
| **6-18 mois** | Option B en s'appuyant sur la flotte financée par C. Angle : corridor Dakar-Thiès-Touba + réconciliation COD à J+1. | 224+ commandes/jour |
| **En continu** | Option D. Géocodage systématique, moteur COD, dossier de conformité prêt pour l'agrément. | Dossier d'agrément déposable dès publication du décret moto |
| **Jamais** | Option A, sauf changement de la politique tarifaire de Yango **et** disponibilité d'un capital de subvention. | — |

---

## 10. Risques

| # | Risque | Probabilité | Impact | Atténuation |
|---|---|---|---|---|
| 1 | **Décret « livraison à moto »** requalifiant le statut des livreurs | Élevée (texte en préparation, pression parlementaire) | Structurel — bascule la marge de tous les scénarios | Modéliser dès maintenant une variante « livreurs salariés » ; anticiper assurance et immatriculation |
| 2 | **Agrément décret 2024-847** : 51 % de capital sénégalais, 15 M FCFA | Certaine à terme (décret en révision, aucun agrément délivré) | Bloquant si le capital n'est pas conforme | Structurer le capital sénégalais dès la constitution ; provisionner 15 M FCFA |
| 3 | **Interdictions de circulation des motos** (arrêtés du gouverneur) | Récurrente, corrélée au calendrier politique | Arrêt total de la flotte, non assurable | Mode dégradé (4 roues, points relais), SLA rédigés avec clause de force majeure |
| 4 | **Guerre des prix prolongée par Yango** (0 % de commission) | Élevée tant que la stratégie de conquête dure | Rend l'option A non viable | Ne pas concourir sur ce terrain ; C et B ne sont pas exposés |
| 5 | **Macro** : programme FMI suspendu, dette à 132 % du PIB, besoins de financement à 26,2 % du PIB, croissance 2026 à 2,2 % | Avérée | Pression fiscale nouvelle, pouvoir d'achat comprimé | Segments corporate et B2B, moins sensibles que le B2C discrétionnaire |
| 6 | **Carburant** : +7,6 % en 8 mois | Élevée | ~5 % de la marge par commande pour +10 % de carburant | Indexation des tarifs coursiers ; clause de révision dans les contrats chargeurs |
| 7 | **Fiabilité des données de marché** | Avérée (§2, §5.3) | Décisions fondées sur des chiffres faux | N'engager du capital qu'après le test terrain du §12 |

---

## 11. Signaux à surveiller

1. **Publication du décret « livraison à moto »** — déclenche la mise en conformité et rebat les coûts de tous les acteurs.
2. **Révision du décret 2024-847 et premiers agréments VTC délivrés** — sortie de la zone grise ; qui obtient l'agrément en premier prend une avance réglementaire.
3. **Évolution de la commission de Yango** — le passage de 0 % à un taux standard rouvre le segment repas.
4. **Fin de la phase pilote de l'Adressage Numérique National** (annoncée sous un an à compter d'août 2026) — réduit le coût caché de chaque livraison, et dévalue partiellement l'actif « base d'adresses propriétaire ».
5. **Lancement effectif de JumiaPay au Sénégal** — change l'économie de l'encaissement e-commerce et donc la valeur du service de réconciliation COD.
6. **Reprise ou non du programme FMI** — conditionne la pression fiscale des 24 prochains mois.
7. **Application effective de l'obligation d'immatriculation des motos** — le jour où elle est appliquée, l'avantage bascule vers les flottes formelles.

---

## 12. Ce qui reste à vérifier — plan de terrain

Cette étude a été construite à partir de sources publiques. Cinq inconnues ne se lèvent que sur le terrain, et **aucune décision d'investissement ne devrait précéder ce test** :

| # | Question | Méthode | Effort |
|---|---|---|---|
| 1 | Volume et panier réels par segment | 20 entretiens restaurateurs partenaires Yango/Yassir + 10 marchands e-commerce | 2 semaines |
| 2 | Rémunération effective et rotation des livreurs | 15 entretiens coursiers sur points de stationnement (Plateau, Ouakam, Parcelles) | 1 semaine |
| 3 | Part du paiement à la livraison vs prépayé, et délai réel de reversement | Entretiens marchands + test client mystère sur 3 plateformes | 1 semaine |
| 4 | Appétence corporate réelle (option C) | 10 rendez-vous acheteurs services généraux ; viser 3 lettres d'intention | 3 semaines |
| 5 | Texte exact du décret 2024-847 et état du projet « livraison à moto » | Consultation au JO + rendez-vous MITTA / conseil juridique local | 2 semaines |

**Critère de décision proposé :** engager l'option C si et seulement si le point 4 produit **au moins 3 lettres d'intention totalisant ≥ 30 commandes/jour** — soit le seuil de rentabilité modélisé du scénario C, atteint avant le premier franc investi en flotte.

---

## 13. Réponse en une phrase

Le domaine de la livraison au Sénégal offre une opportunité réelle, mais **pas dans la livraison de repas grand public** : elle se situe dans la logistique B2B du dernier kilomètre et les comptes corporate, où un opérateur sénégalais — avantagé par la règle des 51 % de capital national et par la TVA numérique visant les plateformes étrangères — peut être rentable dès une trentaine de commandes par jour, à condition de ne jamais entrer dans la guerre des promotions.
