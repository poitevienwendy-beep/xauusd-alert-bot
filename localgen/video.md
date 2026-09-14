# Vidéo sur RTX 2060 12 Go — ComfyUI + GGUF

## Pourquoi ça change d'approche

Le plan précédent visait **Wan 2.2 I2V-A14B en FP8**, estimé à 35,6 Go, avec
délestage automatique entre 24 Go de VRAM et 64 Go de RAM. Deux blocages
matériels sur cette machine :

1. **FP8 n'existe pas sur Turing.** Les checkpoints « FP8 scaled » ne
   s'exécutent pas nativement ; il faudrait les déquantiser à la volée, ce qui
   annule le gain mémoire.
2. **12 Go de VRAM + 32 Go de RAM** ne peuvent pas accueillir un modèle 14B,
   même délesté : la RAM utile sous Windows tourne autour de 24 Go.

La seule voie réaliste est la **quantisation GGUF**, dont les loaders vivent
dans ComfyUI (`ComfyUI-GGUF` de city96). C'est pourquoi ComfyUI revient dans le
plan, uniquement pour la vidéo.

## Modèle retenu

**Wan 2.2 TI2V-5B, quantisé GGUF Q4_K_M** (~3,4 Go de poids ; Q5_K_M ~4,3 Go si
la qualité manque et que la VRAM le permet).

Pour référence : le même modèle en FP16 demande ~24 Go avec délestage dans
l'implémentation officielle, et environ 8 Go via le délestage natif de ComfyUI.
Le Q4 laisse de la marge pour le VAE et l'encodeur de texte.

## Installation

```powershell
cd $env:USERPROFILE
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Loader GGUF
cd custom_nodes
git clone https://github.com/city96/ComfyUI-GGUF
cd ..
.\.venv\Scripts\python.exe -m pip install gguf
```

Fichiers à déposer :

| Fichier | Destination |
|---|---|
| `wan2.2-ti2v-5b-Q4_K_M.gguf` | `models\unet\` |
| Encodeur de texte UMT5-XXL (GGUF Q4 ou safetensors FP8) | `models\text_encoders\` |
| VAE Wan 2.2 | `models\vae\` |

Lancement en mode économe :

```powershell
.\.venv\Scripts\python.exe main.py --lowvram
```

## Graphe minimal (image → vidéo)

```
UnetLoaderGGUF (wan2.2-ti2v-5b-Q4_K_M.gguf)
        │
CLIPLoader (umt5-xxl, type: wan)  ──► CLIPTextEncode (positif)
        │                         └─► CLIPTextEncode (négatif)
LoadImage ──► VAEEncode (VAE Wan 2.2) ──► image de départ
        │
        └──► WanImageToVideo ──► KSampler ──► VAEDecode ──► SaveWebM / VideoCombine
```

## Réglages de départ

| Paramètre | Valeur |
|---|---|
| Résolution | 704 × 480 (ne pas viser 720p tout de suite) |
| Images | 49 (≈ 3 s à 16 fps) |
| Steps | 20 |
| CFG | 5.0 |
| Sampler | `uni_pc` ou `euler` |

**Durée attendue : 10 à 30 min par clip.** C'est une estimation dérivée de
l'écart de puissance FP16 avec la carte visée à l'origine, pas une mesure.
Chronométrer le premier clip avant d'en planifier une série.

## Si ça déborde quand même

1. Descendre à 33 images au lieu de 49.
2. Passer l'encodeur de texte en GGUF Q4 lui aussi.
3. Descendre en Q3_K_M (~2,6 Go) — perte de qualité visible.
4. `--novram` au lieu de `--lowvram` : tout est délesté, beaucoup plus lent mais
   ça passe.

## Ce qu'il faut accepter

Sur cette carte, la vidéo reste un usage « lancer et revenir plus tard ». Pour
de l'itération rapide, faire l'image dans `images.py`, valider le cadrage, et
n'animer que les images retenues.
