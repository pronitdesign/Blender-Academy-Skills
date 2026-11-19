"""Compara a silhueta do modelo (vista da câmera) com a referência, pixel a pixel.

Gera:
  - um JSON com IoU, % de falta/sobra, deslocamento de cada borda em pixels e veredito por fase;
  - uma imagem de overlay: VERMELHO = falta no modelo, CIANO = sobra no modelo, CINZA = acerto.

Não salva o .blend e restaura todas as configurações de render ao terminar.

Uso em background:
  blender -b projeto.blend --python silhouette_compare.py -- \
      --ref /abs/refs/hero.png --out /abs/provas/F2_silhueta_v003 [--fase F2]

Uso ao vivo via MCP (execute_blender_code):
  import runpy
  runpy.run_path("/abs/.../silhouette_compare.py", run_name="__main__",
                 init_globals={"ARGS": ["--ref", "/abs/refs/hero.png", "--out", "/abs/provas/F2_v003"]})

Máscara da referência (em ordem de prioridade):
  --ref-mask arquivo.png    branco = objeto (mais confiável; recorte feito por você)
  canal alfa da --ref       se a imagem tiver transparência real
  chave de fundo automática cor de fundo estimada pelas bordas da imagem (--tol ajusta)
"""
import argparse
import json
import os
import sys
import tempfile

import bpy
import numpy as np

# Limiares de IoU por fase (silhueta da vista-alvo). Ver references/04-comparacao-pixel.md
THRESHOLDS = {"F1": 0.90, "F2": 0.94, "F3": 0.975, "F6": 0.985}


def _argv():
    if "ARGS" in globals():
        return list(globals()["ARGS"])
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ref", required=True, help="Imagem de referência (caminho absoluto).")
    p.add_argument("--ref-mask", help="Máscara opcional da referência (branco = objeto).")
    p.add_argument("--out", required=True, help="Prefixo de saída absoluto, sem extensão.")
    p.add_argument("--fase", default="F2", choices=sorted(THRESHOLDS), help="Fase para o veredito.")
    p.add_argument("--camera", help="Nome da câmera (padrão: câmera ativa da cena).")
    p.add_argument("--tol", type=float, default=0.12, help="Tolerância da chave de fundo (0-1).")
    p.add_argument("--invert", action="store_true", help="Inverte a máscara da referência.")
    p.add_argument("--keep-holes", action="store_true",
                   help="Não preencher buracos internos da máscara (use para objetos vazados: alças, aros).")
    p.add_argument("--max-edge", type=int, default=1600, help="Maior lado usado na comparação.")
    p.add_argument("--hide", default="", help="Objetos a ignorar, separados por vírgula (ex.: chão).")
    return p.parse_args(_argv())


def load_rgba(path, size=None):
    img = bpy.data.images.load(path, check_existing=False)
    try:
        if size and tuple(img.size) != tuple(size):
            img.scale(size[0], size[1])
        w, h = img.size
        buf = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(buf)
        return buf.reshape(h, w, 4), (w, h)  # linhas de baixo para cima (padrão do Blender)
    finally:
        bpy.data.images.remove(img)


def ref_mask(args, size):
    if args.ref_mask:
        px, _ = load_rgba(args.ref_mask, size)
        m = px[..., :3].mean(axis=2) > 0.5
        method = "mascara_manual"
    else:
        px, _ = load_rgba(args.ref, size)
        alpha = px[..., 3]
        if alpha.min() < 0.5 < alpha.max():
            m = alpha > 0.5
            method = "alfa"
        else:
            rgb = px[..., :3]
            border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
            bg = np.median(border, axis=0)
            m = np.linalg.norm(rgb - bg, axis=2) > args.tol
            method = "chave_de_fundo(bg=%s, tol=%.2f)" % ([round(float(v), 3) for v in bg], args.tol)
    if args.invert:
        m = ~m
    if not args.keep_holes:
        m = fill_holes(m)
        method += "+buracos_preenchidos"
    return m, method


def fill_holes(mask):
    """Áreas de fundo que não tocam a borda da imagem (ex.: texto branco no rótulo) viram objeto.
    Flood fill por dilatação iterativa só com numpy (o Blender não traz scipy)."""
    bg = ~mask
    reach = np.zeros_like(bg)
    reach[0, :], reach[-1, :], reach[:, 0], reach[:, -1] = bg[0, :], bg[-1, :], bg[:, 0], bg[:, -1]
    for _ in range(20000):
        grown = reach.copy()
        grown[1:, :] |= reach[:-1, :]
        grown[:-1, :] |= reach[1:, :]
        grown[:, 1:] |= reach[:, :-1]
        grown[:, :-1] |= reach[:, 1:]
        grown &= bg
        if np.array_equal(grown, reach):
            break
        reach = grown
    return ~reach


def render_silhouette(scene, cam, size, hidden):
    r = scene.render
    saved = dict(engine=r.engine, x=r.resolution_x, y=r.resolution_y, pct=r.resolution_percentage,
                 transparent=r.film_transparent, path=r.filepath, fmt=r.image_settings.file_format,
                 mode=r.image_settings.color_mode, camera=scene.camera, border=r.use_border)
    saved_hide = {o.name: o.hide_render for o in hidden}
    tmp = os.path.join(tempfile.mkdtemp(prefix="pp_sil_"), "sil.png")
    try:
        for eng in ("BLENDER_WORKBENCH", "WORKBENCH"):
            try:
                r.engine = eng
                break
            except TypeError:
                continue
        r.resolution_x, r.resolution_y = size
        r.resolution_percentage = 100
        r.use_border = False
        r.film_transparent = True
        r.image_settings.file_format = "PNG"
        r.image_settings.color_mode = "RGBA"
        r.filepath = tmp
        scene.camera = cam
        for o in hidden:
            o.hide_render = True
        bpy.ops.render.render(write_still=True, scene=scene.name)
        px, _ = load_rgba(tmp)
        return px[..., 3] > 0.5
    finally:
        r.engine = saved["engine"]
        r.resolution_x, r.resolution_y = saved["x"], saved["y"]
        r.resolution_percentage = saved["pct"]
        r.film_transparent = saved["transparent"]
        r.filepath = saved["path"]
        r.image_settings.file_format = saved["fmt"]
        r.image_settings.color_mode = saved["mode"]
        r.use_border = saved["border"]
        scene.camera = saved["camera"]
        for o in hidden:
            o.hide_render = saved_hide[o.name]


def bbox(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    # converte para coordenadas de imagem (y = 0 no topo)
    h = mask.shape[0]
    return dict(left=int(xs.min()), right=int(xs.max()), top=int(h - 1 - ys.max()), bottom=int(h - 1 - ys.min()),
                cx=float(xs.mean()), cy=float(h - 1 - ys.mean()))


def side_hints(rb, mb):
    """Traduz diferenças de borda em instruções legíveis (positivo = modelo passou da referência)."""
    d = dict(esquerda=rb["left"] - mb["left"], direita=mb["right"] - rb["right"],
             topo=rb["top"] - mb["top"], base=mb["bottom"] - rb["bottom"])
    hints = []
    for lado, v in d.items():
        if abs(v) >= 2:
            hints.append("%s: modelo %s %d px" % (lado, "passa" if v > 0 else "fica aquém", abs(v)))
    return d, hints


def main():
    a = parse()
    scene = bpy.context.scene
    cam = bpy.data.objects.get(a.camera) if a.camera else scene.camera
    if cam is None or cam.type != "CAMERA":
        raise SystemExit("ERRO: nenhuma câmera válida. Rode ref_setup.py primeiro ou use --camera.")
    probe = bpy.data.images.load(a.ref, check_existing=False)
    w, h = probe.size
    bpy.data.images.remove(probe)
    s = min(1.0, a.max_edge / float(max(w, h)))
    size = (max(1, round(w * s)), max(1, round(h * s)))

    hidden = [bpy.data.objects[n.strip()] for n in a.hide.split(",") if n.strip() in bpy.data.objects]
    model = render_silhouette(scene, cam, size, hidden)
    ref, method = ref_mask(a, size)

    inter = np.logical_and(ref, model).sum()
    union = np.logical_or(ref, model).sum()
    falta = np.logical_and(ref, ~model).sum()
    sobra = np.logical_and(model, ~ref).sum()
    iou = float(inter / union) if union else 0.0
    rb, mb = bbox(ref), bbox(model)
    report = dict(
        fase=a.fase, limiar_iou=THRESHOLDS[a.fase], iou=round(iou, 4),
        aprovado_silhueta=bool(iou >= THRESHOLDS[a.fase]),
        falta_pct_da_ref=round(100.0 * falta / max(1, ref.sum()), 2),
        sobra_pct_da_ref=round(100.0 * sobra / max(1, ref.sum()), 2),
        tamanho_comparacao=list(size), metodo_mascara=method, camera=cam.name,
        lente_mm=round(cam.data.lens, 2), blender=bpy.app.version_string, arquivo=bpy.data.filepath,
        ignorados=[o.name for o in hidden],
        limites="Mede só a silhueta nesta câmera. Detalhes internos, materiais e outras vistas exigem comparação visual.",
    )
    if rb and mb:
        deltas, hints = side_hints(rb, mb)
        report.update(bordas_px=deltas, dicas=hints,
                      centro_delta_px=[round(mb["cx"] - rb["cx"], 1), round(mb["cy"] - rb["cy"], 1)],
                      largura_ref_vs_modelo=[rb["right"] - rb["left"], mb["right"] - mb["left"]],
                      altura_ref_vs_modelo=[rb["bottom"] - rb["top"], mb["bottom"] - mb["top"]])
    elif not mb:
        report["dicas"] = ["O modelo não aparece na câmera. Confira enquadramento e visibilidade de render."]
    else:
        report["dicas"] = ["A máscara da referência ficou vazia. Use --ref-mask ou ajuste --tol/--invert."]

    # overlay: referência escurecida ao fundo + cores de diferença
    px, _ = load_rgba(a.ref, size)
    base = px[..., :3].mean(axis=2, keepdims=True) * 0.35
    out = np.concatenate([np.repeat(base, 3, axis=2), np.ones(ref.shape + (1,), np.float32)], axis=2)
    out[np.logical_and(ref, model)] = (0.55, 0.55, 0.55, 1)
    out[np.logical_and(ref, ~model)] = (1.0, 0.1, 0.1, 1)
    out[np.logical_and(model, ~ref)] = (0.0, 0.9, 1.0, 1)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    img = bpy.data.images.new("pp_overlay", size[0], size[1], alpha=True)
    try:
        img.pixels.foreach_set(out.ravel())
        img.filepath_raw = a.out + "_overlay.png"
        img.file_format = "PNG"
        img.save()
    finally:
        bpy.data.images.remove(img)
    report["overlay"] = a.out + "_overlay.png"
    with open(a.out + "_silhueta.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("PP_SILHUETA_INICIO")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("PP_SILHUETA_FIM")
    return report


if __name__ == "__main__":
    main()
