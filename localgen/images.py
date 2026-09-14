#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generation d'images locale — calibre pour RTX 2060 12 Go / 32 Go RAM.

Difference majeure avec la version 4090 :
  * dtype force a float16. Turing (SM 7.5) n'a PAS de BF16 materiel.
  * Z-Image retire : il rend des images noires (latents NaN) sur serie RTX 20.
  * delestage sequentiel par defaut (12 Go de VRAM, ~24 Go de RAM utile).
  * VAE fp16-fix pour SDXL, sans quoi le decodage FP16 produit des NaN.

Les imports lourds (PIL, torch, diffusers) sont charges tard, pour que
--selftest tourne avec la bibliotheque standard seule.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ENGINES = {
    "sdxl":  "stabilityai/stable-diffusion-xl-base-1.0",
    "klein": "black-forest-labs/FLUX.2-klein-base-4B",
}
SDXL_VAE_FP16_FIX = "madebyollin/sdxl-vae-fp16-fix"

REQUIRED_KEYS = {
    "width", "height", "steps", "guidance", "seed", "negative",
    "reference_max_edge", "offload", "quantize", "max_reference_images",
    "max_output_pixels", "blocked_prompt_terms",
}
INTEGER_KEYS = ("width", "height", "steps", "seed", "reference_max_edge",
                "max_reference_images", "max_output_pixels")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generation d'images locale (RTX 2060 12 Go)")
    p.add_argument("--engine", choices=["auto", "sdxl", "klein", "zimage"], default="auto")
    p.add_argument("--prompt", help="Requis sauf avec --selftest")
    p.add_argument("--ref", action="append", default=[], help="Repeter pour plusieurs photos")
    p.add_argument("--out", help="Fichier .png de sortie ; requis sauf avec --selftest")
    p.add_argument("--settings", default=str(ROOT / "image-settings.json"))
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--steps", type=int)
    p.add_argument("--guidance", type=float)
    p.add_argument("--seed", type=int)
    p.add_argument("--negative")
    p.add_argument("--strength", type=float, help="img2img SDXL uniquement ; defaut 0.55")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--low-vram", action="store_true", help="force le delestage sequentiel")
    p.add_argument("--fast", action="store_true",
                   help="delestage par modele : plus rapide, ~2 Go de VRAM en plus")
    p.add_argument("--nf4", action="store_true",
                   help="quantisation 4 bits (necessaire pour Klein 4B en 12 Go)")
    p.add_argument("--selftest", action="store_true",
                   help="valide les reglages et sort, sans charger torch")
    return p


def validate(p, a, c):
    """Valide le fichier de reglages fusionne avec les options de la ligne de commande."""
    if not isinstance(c, dict) or set(c) != REQUIRED_KEYS:
        missing = REQUIRED_KEYS - set(c) if isinstance(c, dict) else REQUIRED_KEYS
        extra = set(c) - REQUIRED_KEYS if isinstance(c, dict) else set()
        p.error(f"Reglages invalides. Manquants : {sorted(missing)} ; en trop : {sorted(extra)}")

    for key in ("width", "height", "steps", "guidance", "seed", "negative"):
        if getattr(a, key) is not None:
            c[key] = getattr(a, key)
    if a.low_vram:
        c["offload"] = "sequential"
    if a.fast:
        c["offload"] = "model"
    if a.nf4:
        c["quantize"] = "nf4"

    if any(type(c[k]) is not int for k in INTEGER_KEYS):
        p.error("Dimensions, pas, graine et limites doivent etre des entiers.")
    if min(c["width"], c["height"], c["steps"], c["max_output_pixels"]) < 1:
        p.error("Dimensions, pas et pixels max doivent etre positifs.")
    if c["width"] % 16 or c["height"] % 16:
        p.error("Largeur et hauteur doivent etre divisibles par 16.")
    if c["reference_max_edge"] < 16 or c["max_reference_images"] < 0:
        p.error("Bord de reference >= 16 ; nombre max de references >= 0.")
    if not 0 <= c["seed"] < 2**63:
        p.error("La graine doit aller de 0 a 2**63 - 1.")
    if type(c["guidance"]) not in (int, float) or not math.isfinite(c["guidance"]) or c["guidance"] < 0:
        p.error("Guidance : nombre fini positif ou nul.")
    if c["offload"] not in ("model", "sequential"):
        p.error("offload doit valoir model ou sequential.")
    if c["quantize"] not in ("none", "nf4"):
        p.error("quantize doit valoir none ou nf4.")
    if not isinstance(c["negative"], str):
        p.error("Le prompt negatif doit etre du texte.")

    terms = c["blocked_prompt_terms"]
    if not isinstance(terms, list) or any(not isinstance(t, str) for t in terms):
        p.error("blocked_prompt_terms doit etre une liste de chaines.")
    if a.prompt and any(t.strip() and t.strip().casefold() in a.prompt.casefold() for t in terms):
        p.error("Le prompt correspond a un terme de blocked_prompt_terms.")
    if c["width"] * c["height"] > c["max_output_pixels"]:
        p.error("La sortie depasse max_output_pixels.")
    if len(a.ref) > c["max_reference_images"]:
        p.error("Trop de photos pour max_reference_images.")
    return c


def choose_engine(p, a, c):
    if a.engine == "zimage":
        p.error("Z-Image ne fonctionne pas sur RTX serie 20 : le BF16 est absent du "
                "materiel et le FP16 produit des images noires (latents NaN). "
                "Utiliser --engine sdxl ou --engine klein.")
    engine = a.engine if a.engine != "auto" else ("klein" if a.ref else "sdxl")

    if engine == "sdxl" and len(a.ref) > 1:
        p.error("SDXL img2img prend une seule image de depart ; utiliser --engine klein "
                "pour plusieurs references.")
    if engine == "klein" and c["negative"]:
        p.error("FLUX.2 Klein n'utilise pas de prompt negatif : decrire ce qui est voulu "
                "dans --prompt, ou passer par --engine sdxl.")
    if engine == "sdxl" and c["negative"] and c["guidance"] <= 1:
        p.error("Un prompt negatif exige une guidance superieure a 1.")
    if engine == "klein" and c["quantize"] != "nf4":
        print("Attention : Klein 4B pese ~13 Go en FP16 et ne tient pas dans 12 Go. "
              "Ajouter --nf4, sinon le delestage sequentiel rendra la generation tres lente.")

    if a.strength is not None and not (engine == "sdxl" and a.ref):
        p.error("--strength ne s'applique qu'a SDXL img2img.")
    strength = 0.55 if a.strength is None else a.strength
    if engine == "sdxl" and a.ref and not (0 < strength <= 1 and int(c["steps"] * strength) >= 1):
        p.error("strength doit etre dans ]0, 1] avec steps * strength >= 1.")
    return engine, strength


def main() -> None:
    p = build_parser()
    a = p.parse_args()

    try:
        c = json.loads(Path(a.settings).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        p.error(f"Lecture des reglages impossible : {exc}")

    c = validate(p, a, c)
    engine, strength = choose_engine(p, a, c)

    if a.selftest:
        print(f"Moteur : {engine}")
        print(json.dumps(c, indent=2, ensure_ascii=False))
        print("Reglages valides.")
        return

    if not a.prompt or not a.out:
        p.error("--prompt et --out sont requis.")

    out = Path(a.out).resolve()
    record_path = out.with_suffix(".json")
    if out.suffix.lower() != ".png":
        p.error("Choisir un nom de sortie en .png.")
    if out.exists() or record_path.exists():
        p.error("La sortie ou sa fiche de reglages existe deja ; changer --out.")

    from PIL import Image, ImageOps
    photos = []
    for filename in a.ref:
        try:
            with Image.open(filename) as source:
                photo = ImageOps.exif_transpose(source).convert("RGB")
        except (OSError, ValueError) as exc:
            p.error(f"Reference illisible {filename} : {exc}")
        if engine == "sdxl":
            photo = ImageOps.fit(photo, (c["width"], c["height"]), method=Image.Resampling.LANCZOS)
        else:
            photo.thumbnail((c["reference_max_edge"], c["reference_max_edge"]),
                            Image.Resampling.LANCZOS)
        if min(photo.size) < 16:
            p.error("Une reference est devenue trop etroite ; eviter un ratio extreme.")
        photos.append(photo)

    import torch

    if not torch.cuda.is_available():
        raise SystemExit("CUDA indisponible.")
    major, _ = torch.cuda.get_device_capability(0)
    dtype = torch.float16          # Turing : jamais bfloat16.
    if major >= 8:
        print("Note : ce GPU supporte BF16. Le FP16 reste correct, mais ce script est "
              "calibre pour Turing — re-specifier si le materiel a change.")

    model_id = ENGINES[engine]
    print(f"Modele : {model_id}  |  dtype : float16  |  offload : {c['offload']}  "
          f"|  quantize : {c['quantize']}")

    loading = dict(dtype=dtype, cache_dir=str(ROOT / "models"),
                   local_files_only=a.offline, use_safetensors=True)

    if c["quantize"] == "nf4":
        # bitsandbytes 4 bits exige compute capability >= 7.5 : le 2060 est tout
        # juste dans la cible.
        try:
            from diffusers.quantizers import PipelineQuantizationConfig
        except ImportError:
            raise SystemExit(
                "PipelineQuantizationConfig indisponible dans cette version de diffusers. "
                "Mettre a jour diffusers, ou passer par ComfyUI + GGUF (voir video.md)."
            )
        loading["quantization_config"] = PipelineQuantizationConfig(
            quant_backend="bitsandbytes_4bit",
            quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4",
                          "bnb_4bit_compute_dtype": dtype},
            components_to_quantize=["transformer", "text_encoder"],
        )

    if engine == "sdxl":
        from diffusers import (AutoencoderKL, StableDiffusionXLImg2ImgPipeline,
                               StableDiffusionXLPipeline)
        pipeline_class = StableDiffusionXLImg2ImgPipeline if photos else StableDiffusionXLPipeline
        # Le VAE SDXL d'origine deborde en FP16 et sort des images noires.
        try:
            loading["vae"] = AutoencoderKL.from_pretrained(
                SDXL_VAE_FP16_FIX, dtype=dtype, cache_dir=str(ROOT / "models"),
                local_files_only=a.offline)
        except Exception as exc:                       # noqa: BLE001 - repli explicite
            print(f"Attention : VAE fp16-fix indisponible ({exc}). Le VAE d'origine peut "
                  "produire des images noires en FP16.")
        pipe = pipeline_class.from_pretrained(model_id, variant="fp16", **loading)
    else:
        from diffusers import Flux2KleinPipeline
        pipe = Flux2KleinPipeline.from_pretrained(model_id, **loading)

    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    if c["offload"] == "sequential":
        pipe.enable_sequential_cpu_offload()
    else:
        pipe.enable_model_cpu_offload()

    options = dict(
        prompt=a.prompt,
        num_inference_steps=c["steps"],
        guidance_scale=c["guidance"],
        generator=torch.Generator(device="cpu").manual_seed(c["seed"]),
    )
    with torch.inference_mode():
        if engine == "klein":
            options.update(width=c["width"], height=c["height"])
            if photos:
                options["image"] = photos
        else:
            options["negative_prompt"] = c["negative"]
            if photos:
                options.update(image=photos[0], strength=strength)
            else:
                options.update(width=c["width"], height=c["height"])
        result = pipe(**options).images[0]

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("xb") as destination:
        result.save(destination, format="PNG")
    record = dict(c, engine=engine, model=model_id, dtype="float16", prompt=a.prompt,
                  references=a.ref,
                  processed_reference_sizes=[list(photo.size) for photo in photos],
                  strength=strength if engine == "sdxl" and photos else None)
    with record_path.open("x", encoding="utf-8") as destination:
        json.dump(record, destination, indent=2, ensure_ascii=False)
    print(f"Image : {out}")
    print(f"Fiche de reglages : {record_path}")


if __name__ == "__main__":
    main()
