# 00-diagnostic.ps1 — verifie les specs reelles de la machine. Ne modifie rien.
# Objectif : confirmer RTX 2060 12 Go / 32 Go RAM AVANT de telecharger 100+ Go de modeles.

$ErrorActionPreference = "Stop"

function Section($t) { Write-Host ""; Write-Host "=== $t ===" -ForegroundColor Cyan }

Section "GPU (nvidia-smi)"
$smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if (-not $smi) {
    Write-Host "nvidia-smi introuvable — pilote NVIDIA absent ou hors PATH." -ForegroundColor Red
} else {
    # compute_cap n'existe que sur les pilotes recents : repli sans ce champ.
    nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv 2>$null
    if ($LASTEXITCODE -ne 0) {
        nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
    }
}

Section "RAM et disque"
$os = Get-CimInstance Win32_OperatingSystem
$ramGo = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
Write-Host "RAM totale        : $ramGo Go"
$disk = Get-PSDrive -Name ($env:USERPROFILE.Substring(0,1))
Write-Host ("Libre sur {0}:     {1} Go" -f $env:USERPROFILE.Substring(0,1), [math]::Round($disk.Free / 1GB, 1))

Section "Verdict attendu"
Write-Host "GPU               : NVIDIA GeForce RTX 2060"
Write-Host "VRAM              : 12288 MiB"
Write-Host "Compute capability: 7.5"
Write-Host "RAM               : ~32 Go"
Write-Host ""
Write-Host "Si l'une de ces lignes ne correspond pas, ARRETER ici et re-specifier." -ForegroundColor Yellow

Section "Verification PyTorch (si le venv existe deja)"
$py = Join-Path $env:USERPROFILE "LocalGen\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "venv absent — normal avant 01-install.ps1. Cette section sera utile apres."
    return
}

& $py -c @'
import torch
print('torch            :', torch.__version__)
print('CUDA disponible  :', torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit('CUDA indisponible — arreter ici.')
major, minor = torch.cuda.get_device_capability(0)
props = torch.cuda.get_device_properties(0)
print('GPU              :', torch.cuda.get_device_name(0))
print('VRAM             :', round(props.total_memory / 2**30, 1), 'Gio')
print('Compute capability:', f'{major}.{minor}')
print('BF16 materiel    :', 'OUI' if major >= 8 else 'NON (Turing) -> utiliser float16')
print('FP8 materiel     :', 'OUI' if (major, minor) >= (8, 9) else 'NON -> pas de checkpoint FP8')
print('Calcul FP16 test :', (torch.ones(8, device='cuda', dtype=torch.float16) * 2).sum().item())
'@
if ($LASTEXITCODE -ne 0) { throw "Le diagnostic PyTorch a echoue — coller la sortie." }
