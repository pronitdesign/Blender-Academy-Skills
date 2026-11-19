"""Render por fase, com presets previsíveis. Nunca sobrescreve uma imagem existente.

Fases:
  clay     Cycles, material cinza neutro forçado (forma e luz, sem distração de material)
  preview  EEVEE (layout/composição; NÃO serve como prova de material)
  lookdev  Cycles com amostragem média (prova de material/textura)
  final    Cycles convergido para entrega

Background:
  blender -b projeto.blend --python render_stage.py -- --stage clay --out /abs/provas/F2_clay_v003.png
  ... --stage final --out /abs/renders/hero_v010.png --width 3840 --height 2160
  ... --stage lookdev --crop 0.40,0.60,0.35,0.55 --out /abs/provas/F4_crop_chip_v001.png   (recorte a 100%)
MCP:
  import runpy; runpy.run_path("/abs/.../render_stage.py", run_name="__main__",
      init_globals={"ARGS": ["--stage", "clay", "--out", "/abs/provas/F2_clay_v003.png"]})

Restaura as configurações de render ao final (a cena não fica alterada).
"""
import argparse
import json
import os
import sys
import time

import bpy

PRESETS = {
    "clay": dict(engine="CYCLES", samples=64, threshold=0.05, long_edge=1200),
    "preview": dict(engine="EEVEE", samples=32, threshold=None, long_edge=1500),
    "lookdev": dict(engine="CYCLES", samples=256, threshold=0.02, long_edge=1800),
    "final": dict(engine="CYCLES", samples=1024, threshold=0.008, long_edge=None),
}


def _argv():
    if "ARGS" in globals():
        return list(globals()["ARGS"])
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def set_engine(r, want):
    names = {"CYCLES": ["CYCLES"], "EEVEE": ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"]}[want]
    for n in names:
        try:
            r.engine = n
            return n
        except TypeError:
            continue
    raise SystemExit("ERRO: motor %s indisponível nesta versão." % want)


def pick_device(scene, want):
    """Tenta GPU (METAL/OPTIX/CUDA/HIP/ONEAPI); cai para CPU e informa o que foi usado."""
    if want == "CPU":
        scene.cycles.device = "CPU"
        return "CPU"
    addon = bpy.context.preferences.addons.get("cycles")
    prefs = addon.preferences if addon else None
    if prefs:
        for backend in ("METAL", "OPTIX", "CUDA", "HIP", "ONEAPI"):
            try:
                prefs.compute_device_type = backend
            except TypeError:
                continue
            prefs.refresh_devices()
            gpus = [d for d in prefs.devices if d.type != "CPU"]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type != "CPU"
                scene.cycles.device = "GPU"
                return "GPU:%s (%s)" % (backend, ", ".join(d.name for d in gpus))
    scene.cycles.device = "CPU"
    return "CPU (nenhuma GPU encontrada)"


def clay_material():
    m = bpy.data.materials.get("PP_Clay") or bpy.data.materials.new("PP_Clay")
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1)  # cinza 18% linear
    bsdf.inputs["Roughness"].default_value = 0.55
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stage", required=True, choices=PRESETS)
    p.add_argument("--out", required=True, help="Caminho absoluto .png/.exr (novo).")
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--long-edge", type=int, help="Sobrepõe o maior lado mantendo o aspecto atual.")
    p.add_argument("--samples", type=int)
    p.add_argument("--device", choices=("AUTO", "CPU"), default="AUTO")
    p.add_argument("--camera")
    p.add_argument("--crop", help="xmin,xmax,ymin,ymax em 0-1 (y a partir de baixo): recorte a 100%%.")
    p.add_argument("--transparent", action="store_true")
    a = p.parse_args(_argv())

    out = os.path.abspath(a.out)
    if os.path.exists(out):
        raise SystemExit("ERRO: %s já existe. Use um nome de versão novo." % out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pre = PRESETS[a.stage]
    scene = bpy.context.scene
    r, vl = scene.render, bpy.context.view_layer
    if a.camera:
        scene.camera = bpy.data.objects[a.camera]
    if not scene.camera:
        raise SystemExit("ERRO: cena sem câmera ativa.")

    keep = dict(engine=r.engine, x=r.resolution_x, y=r.resolution_y, pct=r.resolution_percentage,
                path=r.filepath, fmt=r.image_settings.file_format, depth=r.image_settings.color_depth,
                mode=r.image_settings.color_mode, border=r.use_border, crop=r.use_crop_to_border,
                bx=(r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y),
                transparent=r.film_transparent, override=vl.material_override)
    cyc_keep = None
    if hasattr(scene, "cycles"):
        c = scene.cycles
        cyc_keep = dict(samples=c.samples, ad=c.use_adaptive_sampling, th=c.adaptive_threshold,
                        dn=c.use_denoising, device=c.device)
    try:
        engine = set_engine(r, pre["engine"])
        aspect = keep["x"] / float(keep["y"])
        if a.width and a.height:
            r.resolution_x, r.resolution_y = a.width, a.height
        else:
            le = a.long_edge or pre["long_edge"]
            if le:
                r.resolution_x, r.resolution_y = (le, round(le / aspect)) if aspect >= 1 else (round(le * aspect), le)
        r.resolution_percentage = 100
        r.film_transparent = a.transparent
        device = "n/a"
        samples = a.samples or pre["samples"]
        if pre["engine"] == "CYCLES":
            c = scene.cycles
            c.samples = samples
            c.use_adaptive_sampling = True
            c.adaptive_threshold = pre["threshold"]
            c.use_denoising = True
            device = pick_device(scene, a.device)
        else:
            try:
                scene.eevee.taa_render_samples = samples
            except AttributeError:
                pass
        if a.stage == "clay":
            vl.material_override = clay_material()
        if a.crop:
            x0, x1, y0, y1 = (float(v) for v in a.crop.split(","))
            r.use_border, r.use_crop_to_border = True, True
            r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = x0, x1, y0, y1
        exr = out.lower().endswith(".exr")
        r.image_settings.file_format = "OPEN_EXR" if exr else "PNG"
        r.image_settings.color_depth = "16"
        r.image_settings.color_mode = "RGBA" if a.transparent else "RGB"
        r.filepath = out
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        secs = round(time.time() - t0, 1)
        vt = scene.view_settings.view_transform
        print("PP_RENDER " + json.dumps(dict(
            fase=a.stage, arquivo=out, motor=engine, dispositivo=device, amostras=samples,
            resolucao=[r.resolution_x, r.resolution_y], recorte=a.crop, segundos=secs,
            transformacao_de_cor=vt, look=scene.view_settings.look, blender=bpy.app.version_string,
            observacao="EEVEE = só layout" if a.stage == "preview" else ""), ensure_ascii=False))
    finally:
        try:
            r.engine = keep["engine"]
        except TypeError:
            pass
        r.resolution_x, r.resolution_y, r.resolution_percentage = keep["x"], keep["y"], keep["pct"]
        r.filepath = keep["path"]
        r.image_settings.file_format = keep["fmt"]
        r.image_settings.color_depth = keep["depth"]
        r.image_settings.color_mode = keep["mode"]
        r.use_border, r.use_crop_to_border = keep["border"], keep["crop"]
        r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = keep["bx"]
        r.film_transparent = keep["transparent"]
        vl.material_override = keep["override"]
        if cyc_keep:
            c = scene.cycles
            c.samples, c.use_adaptive_sampling, c.adaptive_threshold = cyc_keep["samples"], cyc_keep["ad"], cyc_keep["th"]
            c.use_denoising, c.device = cyc_keep["dn"], cyc_keep["device"]


if __name__ == "__main__":
    main()
