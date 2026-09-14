# LocalGen — specs révisées : RTX 2060 12 Go / 32 Go RAM

> **Note** : ce dossier n'a **rien à voir** avec le bot XAU/USD du dépôt. C'est le
> plan d'installation de génération d'images/vidéos en local, re-spécifié pour la
> machine réelle. Aucun fichier du bot n'est touché.

## 1. Les nouvelles specs

| | Ancien plan | **Machine réelle** |
|---|---|---|
| GPU | RTX 4090 (24 Go annoncés, 16 Go réels) | **RTX 2060 12 Go** |
| Architecture | Ada Lovelace (SM 8.9) | **Turing TU106 (SM 7.5)** |
| RAM système | 64 Go | **32 Go** |
| OS | Windows | Windows |
| Disque | 4 To | inchangé (prévoir ~120 Go libres) |

Caractéristiques utiles de la carte : 2 176 cœurs CUDA, 272 cœurs Tensor,
bus 192 bits, 336 Go/s, 185 W.

## 2. Ce que ce changement casse (à lire avant d'installer)

Ce n'est pas juste « moins de VRAM ». Turing est une génération antérieure à
Ampere, donc trois capacités matérielles disparaissent :

| Capacité | Turing (2060) | Conséquence |
|---|---|---|
| **BF16** | ❌ absent | Tout le plan précédent chargeait en `torch.bfloat16`. Il faut passer en `float16`. |
| **FP8** | ❌ absent | Les checkpoints « FP8 scaled » de Wan 2.2 sont hors-jeu. |
| **FlashAttention 2** | ❌ absent (Ampere+) | On reste sur SDPA/xformers. |
| FP16 tensor cores | ✅ présent | ~26 TFLOPS, soit environ 5 à 6× moins qu'un 4090 portable. |

### Conséquence n°1 : Z-Image est mort sur cette carte

Le modèle d'images du plan précédent (`Tongyi-MAI/Z-Image`) **ne fonctionne pas
sur RTX série 20** :

- en BF16 → non supporté par le matériel ;
- en FP16 → **images entièrement noires** (latents NaN). C'est un bug connu et
  toujours ouvert côté éditeur, signalé explicitement pour « RTX 20 series,
  RDNA2 and older ».

→ **Z-Image est retiré du plan.** Il existe une conversion FP16 communautaire
(`OmegaShred/Z-Image-0.36`) mais rien ne confirme qu'elle corrige le problème sur
Turing : à ne pas mettre sur le chemin principal.

### Conséquence n°2 : Wan 2.2 A14B est hors de portée

L'estimation précédente pour la vidéo était de 35,6 Go (A14B en FP8), avec
délestage entre 24 Go de VRAM et 64 Go de RAM. Avec 12 Go + 32 Go et sans FP8 :
impossible. On descend sur le **TI2V-5B quantisé GGUF**.

### Conséquence n°3 : le délestage devient la règle, pas l'option

Avec 24 Go on pouvait faire `enable_model_cpu_offload()`. Ici :

- `enable_sequential_cpu_offload()` devient le **défaut** ;
- la RAM disponible pour le délestage n'est plus 64 Go mais ~24 Go utiles
  (Windows en consomme 6 à 8). Un modèle de 20 Go en RAM n'est plus sûr.

## 3. Le nouveau stack

| Usage | Ancien choix | **Nouveau choix** | VRAM |
|---|---|---|---|
| Images (principal) | Z-Image Base BF16 | **SDXL 1.0 en FP16** — natif FP16, aucun risque Turing, énorme écosystème LoRA/ControlNet | ~7 Go |
| Images + références photo | FLUX.2 Klein 4B BF16 (~13 Go) | **FLUX.2 Klein 4B** — en 4 bits (NF4) via diffusers, ou GGUF Q4 via ComfyUI. Apache 2.0, références multiples natives | ~13 Go en FP16 (ne rentre pas) → ~5 Go en Q4 |
| Vidéo | Wan 2.2 I2V A14B FP8 | **Wan 2.2 TI2V-5B GGUF Q4_K_M** via ComfyUI + ComfyUI-GGUF | ~3,4 Go de poids |

Licences : FLUX.2 Klein et Wan 2.2 restent Apache 2.0, ce qui correspond à la
préférence exprimée. SDXL est sous CreativeML OpenRAIL++-M — plus permissif à
l'usage qu'un modèle propriétaire, mais **pas** Apache : c'est le compromis pour
avoir un chemin FP16 fiable sur Turing. Si la licence prime sur la fiabilité,
prendre FLUX.1 schnell (Apache 2.0) en GGUF Q4 à la place.

### Changement d'approche : ComfyUI n'est plus évitable

Le plan précédent évitait ComfyUI au profit de scripts Python éditables. Sur 12 Go
Turing, la **vidéo** passe obligatoirement par la quantisation GGUF, dont les
loaders vivent dans l'écosystème ComfyUI (`ComfyUI-GGUF` de city96).

Compromis retenu : **images en Python éditable** (`images.py`, ci-joint),
**vidéo dans ComfyUI**. Voir `video.md`.

## 4. Performances attendues

Estimations calculées depuis l'écart de puissance FP16, **non mesurées** — le
diagnostic et le premier run donneront les vrais chiffres :

| Tâche | Estimation sur 2060 12 Go |
|---|---|
| SDXL, 1024×1024, 30 pas | ~1,5 à 2,5 s/pas → **45 à 75 s** par image |
| FLUX.2 Klein 4B Q4, 768×768 | **2 à 5 min** par image |
| Wan 2.2 TI2V-5B Q4, 480p, 3-5 s de clip | **10 à 30 min** par clip |

## 5. Ordre d'installation

```powershell
# 1. Vérifier que la machine est bien celle qu'on croit (elle a déjà été
#    mal décrite deux fois). Ce script ne modifie rien.
.\00-diagnostic.ps1

# 2. Installer l'environnement (venv + PyTorch CUDA + diffusers)
.\01-install.ps1

# 3. Première image
cd $env:USERPROFILE\LocalGen
.\.venv\Scripts\python.exe .\images.py --prompt "un observatoire de pierre dans la montagne, lumiere du matin" --out .\outputs\test01.png
```

Le diagnostic doit afficher `Compute capability : 7.5`, `VRAM : ~12 Go`,
`BF16 materiel : NON`. S'il affiche autre chose, **arrêter** et re-spécifier
avant d'installer quoi que ce soit.

## 6. Fichiers

| Fichier | Rôle |
|---|---|
| `00-diagnostic.ps1` | Vérifie GPU, VRAM, compute capability, BF16, RAM, disque |
| `01-install.ps1` | Crée `%USERPROFILE%\LocalGen`, venv Python 3.11, PyTorch CUDA, diffusers |
| `images.py` | Génération d'images — FP16 forcé, délestage séquentiel par défaut |
| `image-settings.json` | Réglages par défaut recalibrés pour 12 Go |
| `video.md` | Chemin vidéo : ComfyUI + GGUF |

## 7. Sources

- [RTX 2060 12GB — specs (Tom's Hardware)](https://www.tomshardware.com/news/nvidia-geforce-rtx-2060-12gb-gpu-specifications)
- [Turing / compute capability 7.5 (Wikipedia)](https://en.wikipedia.org/wiki/Turing_(microarchitecture))
- [Z-Image incompatible RTX 20 series (discussion Hugging Face)](https://huggingface.co/Tongyi-MAI/Z-Image/discussions/22)
- [Z-Image FP16 → images noires (issue GitHub)](https://github.com/Tongyi-MAI/Z-Image/issues/14)
- [Wan2.2 TI2V-5B — besoins VRAM](https://willitrunai.com/video-models/wan-video-2-2-ti2v-5b)
- [FLUX.2 Klein 4B GGUF (unsloth)](https://huggingface.co/unsloth/FLUX.2-klein-4B-GGUF)
- [PyTorch — installation par version CUDA](https://pytorch.org/get-started/locally/)
