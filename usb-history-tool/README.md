# Historique Nomade — outil portable pour clé USB

Un outil **autonome** à copier sur une clé USB. Branchez la clé sur un
ordinateur, lancez l'outil, et vous obtenez une page web locale qui :

- **détecte tous les navigateurs** installés pour la session ouverte
  (Chrome, Edge, Brave, Opera, Vivaldi, Chromium, Yandex, Firefox…) ;
- **récupère l'historique de navigation de tous les profils / sessions** de
  chaque navigateur, réuni au même endroit ;
- vous laisse **naviguer** dedans (recherche, filtres, tri, ouverture des
  liens) et **effacer** ce que vous voulez : une entrée, une sélection, ou
  tout l'historique d'un profil / de tous les profils ;
- permet d'**exporter** le tout en CSV ou JSON.

> ✅ **Aucune installation, aucune dépendance.** Uniquement Python 3, présent
> d'origine sur macOS et Linux, et installable en un clic sur Windows.
> **Tout reste en local** : rien n'est envoyé sur Internet.

---

## ⚠️ Usage responsable

Cet outil lit **seulement** les fichiers auxquels la session Windows / macOS /
Linux déjà ouverte a accès. Il n'y a **ni** contournement de mot de passe,
**ni** élévation de privilèges, **ni** vol d'identifiants, **ni** envoi de
données. C'est l'équivalent d'ouvrir chaque navigateur pour regarder son
historique — en version regroupée et portable.

**Utilisez-le uniquement sur des ordinateurs et des comptes qui vous
appartiennent, ou que vous êtes explicitement autorisé à gérer.**

---

## 1. Préparer la clé USB

Copiez le dossier `usb-history-tool/` sur votre clé. Il contient :

```
usb-history-tool/
├── history_tool.py        ← le programme (tout est ici)
├── selftest.py            ← auto-test facultatif (données factices)
├── START-Windows.bat      ← double-clic sous Windows
├── start-macos.command    ← double-clic sous macOS
├── start-linux.sh         ← lancement sous Linux
└── README.md              ← ce fichier
```

## 2. Lancer l'outil

### Windows
1. Ouvrez la clé USB dans l'explorateur.
2. Double-cliquez sur **`START-Windows.bat`**.
3. Votre navigateur s'ouvre sur l'interface. C'est prêt.

> Si Windows dit que Python est introuvable : installez-le depuis le Microsoft
> Store (cherchez « Python 3 », gratuit) ou sur <https://python.org>, en
> cochant **« Add Python to PATH »**. Relancez ensuite le `.bat`.

### macOS
1. Ouvrez la clé USB dans le Finder.
2. Double-cliquez sur **`start-macos.command`**.
   - Au premier lancement, macOS peut bloquer le fichier : faites un
     **clic droit → Ouvrir**, puis confirmez.
3. Le navigateur s'ouvre sur l'interface.

### Linux
```bash
cd /media/…/usb-history-tool     # là où est montée la clé
./start-linux.sh                 # ou : python3 history_tool.py
```

### Sans les lanceurs (toutes plateformes)
```bash
python3 history_tool.py
```

## 3. Utiliser l'interface

- **Rechercher** : tapez un mot ; plusieurs mots = « ET » (toutes les entrées
  qui contiennent tous les mots).
- **Filtrer** : choisissez un navigateur / profil précis dans la liste.
- **Trier** : par date, nombre de visites, titre ou URL (les en-têtes de
  colonnes sont cliquables).
- **Naviguer** : cliquez sur un titre pour ouvrir la page dans votre
  navigateur par défaut.
- **Supprimer une entrée** : le bouton `✕` à droite de la ligne.
- **Supprimer une sélection** : cochez les cases, puis
  **« Supprimer la sélection »**.
- **Tout effacer** : bouton **« Tout effacer… »** (avec double confirmation).
  Si un profil précis est filtré, seul cet historique est effacé ; sinon,
  c'est celui de **tous** les navigateurs.
- **Exporter** : boutons **Export CSV** / **Export JSON** en haut à droite.

## 4. Mode terminal (facultatif)

```bash
python3 history_tool.py --cli                     # liste dans le terminal
python3 history_tool.py --cli --search "youtube"  # avec un filtre
python3 history_tool.py --cli --limit 200         # plus de lignes
python3 history_tool.py --cli --export histo.csv  # export CSV
python3 history_tool.py --cli --export histo.json --format json
python3 history_tool.py --help                    # toutes les options
```

---

## Point important sur la suppression

Un navigateur **ouvert verrouille** son fichier d'historique.

- **La lecture** fonctionne toujours (l'outil travaille sur une copie).
- **La suppression** exige que le navigateur concerné soit **fermé**. Si vous
  tentez d'effacer alors que Chrome/Firefox/… est ouvert, l'outil vous
  l'indique clairement (« ⚠ Fermez d'abord : … ») et ne casse rien. Fermez le
  navigateur, puis recommencez.

La suppression est **définitive** et se fait de façon sûre :
- les **favoris (marque-pages) sont préservés** ;
- pour Firefox, l'opération est encadrée par une transaction atomique — en cas
  d'incident, la base est laissée intacte.

---

## Navigateurs pris en charge

| Famille | Navigateurs | Emplacements lus |
|--------|-------------|------------------|
| Chromium | Chrome, Edge, Brave, Opera / Opera GX, Vivaldi, Chromium, Yandex | fichier `History` de chaque profil |
| Firefox | Firefox (classique, Snap, Flatpak) | `places.sqlite` de chaque profil |

Tous les profils de chaque navigateur sont détectés automatiquement
(`Default`, `Profile 1`, `Profile 2`, profils Firefox, etc.).

---

## Vérifier que tout marche (auto-test)

Le script `selftest.py` crée de fausses bases de données (aucun historique
réel n'est touché) et vérifie lecture, suppression et export :

```bash
python3 selftest.py
```

Vous devez voir « Tous les tests sont passés ».

---

## Confidentialité & sécurité

- **100 % local** : aucune connexion réseau sortante, aucune télémétrie.
- Le mini-serveur web n'écoute que sur `127.0.0.1` (votre machine) et protège
  ses actions par un **jeton aléatoire** généré à chaque lancement, afin
  qu'aucun autre programme ou site web ne puisse le piloter.
- Les fichiers d'historique d'origine ne sont copiés que temporairement, en
  lecture, puis supprimés.

## Dépannage

| Problème | Solution |
|----------|----------|
| « Python introuvable » (Windows) | Installer Python 3 (Microsoft Store ou python.org, cocher « Add to PATH »). |
| « Aucun historique détecté » | Aucun navigateur pris en charge pour ce compte, ou navigateurs jamais utilisés. |
| La suppression échoue | Fermez complètement le navigateur concerné, puis réessayez. |
| macOS bloque le `.command` | Clic droit → Ouvrir → Ouvrir. |
| Le navigateur ne s'ouvre pas seul | Ouvrez manuellement l'adresse affichée dans le terminal (`http://127.0.0.1:…`). |

## Prérequis

- **Python 3.7 ou plus récent**. Aucune bibliothèque externe (uniquement la
  bibliothèque standard).
