# 01-install.ps1 — environnement de generation locale pour RTX 2060 12 Go / 32 Go RAM.
# Turing (SM 7.5) : pas de BF16, pas de FP8, pas de FlashAttention 2. Tout tourne en FP16.

$ErrorActionPreference = "Stop"

$root = Join-Path $env:USERPROFILE "LocalGen"
$py   = Join-Path $root ".venv\Scripts\python.exe"

# --- Python 3.11 (deja present sur la machine d'apres le diagnostic precedent) ---
$launcher = Get-Command py -ErrorAction SilentlyContinue
if (-not $launcher) { throw "Le lanceur 'py' est introuvable. Installer Python 3.11 depuis python.org." }

New-Item -ItemType Directory -Force -Path $root, "$root\models", "$root\outputs", "$root\references" | Out-Null
Set-Location $root

if (-not (Test-Path $py)) {
    Write-Host "Creation du venv Python 3.11..." -ForegroundColor Cyan
    & py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Creation du venv echouee." }
}

& $py -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) { throw "Mise a jour de pip echouee." }

# --- PyTorch CUDA ---
# Les roues cu126 incluent sm_75 (Turing). cu128 le conserve aussi, mais cu126
# est la combinaison la plus eprouvee sur serie 20.
Write-Host "Installation de PyTorch (CUDA 12.6)..." -ForegroundColor Cyan
& $py -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
if ($LASTEXITCODE -ne 0) { throw "Installation de PyTorch echouee." }

# --- Pile de generation ---
# bitsandbytes : la quantisation 4 bits exige compute capability >= 7.5, donc
# le 2060 est tout juste dans la cible. C'est ce qui fait tenir Klein 4B en 12 Go.
Write-Host "Installation de diffusers et dependances..." -ForegroundColor Cyan
& $py -m pip install `
    "diffusers>=0.36" `
    "transformers>=4.49" `
    accelerate `
    safetensors `
    sentencepiece `
    protobuf `
    ftfy `
    pillow `
    "huggingface_hub[hf_transfer]" `
    bitsandbytes
if ($LASTEXITCODE -ne 0) { throw "Installation de la pile de generation echouee." }

# --- Verification materielle : refuser d'aller plus loin si la carte n'est pas celle prevue ---
Write-Host "Verification du GPU..." -ForegroundColor Cyan
& $py -c @'
import sys, torch
if not torch.cuda.is_available():
    sys.exit("CUDA indisponible : verifier le pilote NVIDIA.")
major, minor = torch.cuda.get_device_capability(0)
vram = torch.cuda.get_device_properties(0).total_memory / 2**30
print("GPU  :", torch.cuda.get_device_name(0))
print("VRAM :", round(vram, 1), "Gio")
print("SM   :", f"{major}.{minor}")
if major >= 8:
    print("Note : cette carte supporte BF16 — les reglages FP16 restent valides mais")
    print("       ce plan a ete calibre pour Turing. Re-specifier si le materiel a change.")
else:
    print("Turing confirme : FP16 uniquement, delestage sequentiel par defaut.")
if vram < 10:
    sys.exit("Moins de 10 Gio de VRAM : ce plan vise 12 Go. Re-specifier.")
print("OK")
'@
if ($LASTEXITCODE -ne 0) { throw "Verification GPU echouee — coller la sortie." }

# --- Copie des scripts a cote du venv ---
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($f in @("images.py", "image-settings.json")) {
    $src = Join-Path $here $f
    $dst = Join-Path $root $f
    if (Test-Path $dst) {
        Write-Host "$f existe deja dans LocalGen — conserve (vos modifications sont preservees)." -ForegroundColor Yellow
    } elseif (Test-Path $src) {
        Copy-Item $src $dst
        Write-Host "$f copie dans $root"
    }
}

Write-Host ""
Write-Host "Installation terminee. Premier essai :" -ForegroundColor Green
Write-Host "  cd `"$root`""
Write-Host "  .\.venv\Scripts\python.exe .\images.py --prompt `"un observatoire de pierre dans la montagne`" --out .\outputs\test01.png"
