"""Prepara a câmera de referência: imagem ao fundo da câmera + resolução com o mesmo aspecto da foto.

Cria (ou reutiliza) a câmera, carrega a referência como background da câmera (visível só na vista
de câmera, não sai no render) e ajusta a resolução para o aspecto exato da foto.
Não salva o arquivo: salve um checkpoint com save_version.py depois de conferir.

Uso em background:
  blender -b projeto.blend --python ref_setup.py -- --ref /abs/refs/hero.png --long-edge 1500 \
      [--camera CAM_Hero] [--lens 85] [--sensor 36] [--opacity 0.5] [--save /abs/blend/x_v002.blend]

Uso ao vivo via MCP:
  import runpy; runpy.run_path("/abs/.../ref_setup.py", run_name="__main__",
      init_globals={"ARGS": ["--ref", "/abs/refs/hero.png", "--lens", "85"]})
"""
import argparse
import json
import os
import sys

import bpy


def _argv():
    if "ARGS" in globals():
        return list(globals()["ARGS"])
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ref", required=True)
    p.add_argument("--camera", default="CAM_Ref")
    p.add_argument("--long-edge", type=int, default=1500, help="Maior lado da resolução de trabalho.")
    p.add_argument("--lens", type=float, help="Distância focal em mm (equivalente full frame).")
    p.add_argument("--sensor", type=float, default=36.0, help="Largura do sensor em mm.")
    p.add_argument("--opacity", type=float, default=0.5)
    p.add_argument("--save", help="Opcional: salvar uma CÓPIA configurada neste caminho (não sobrescreve).")
    a = p.parse_args(_argv())

    if not os.path.isfile(a.ref):
        raise SystemExit("ERRO: referência não encontrada: %s" % a.ref)
    scene = bpy.context.scene
    cam = bpy.data.objects.get(a.camera)
    created = False
    if cam is None:
        data = bpy.data.cameras.new(a.camera)
        cam = bpy.data.objects.new(a.camera, data)
        scene.collection.objects.link(cam)
        cam.location = (0.0, -1.0, 0.15)
        cam.rotation_euler = (1.4835, 0.0, 0.0)  # ~85° olhando para +Y
        created = True
    elif cam.type != "CAMERA":
        raise SystemExit("ERRO: '%s' existe mas não é câmera." % a.camera)

    cd = cam.data
    cd.sensor_fit = "AUTO"
    cd.sensor_width = a.sensor
    if a.lens:
        cd.lens = a.lens
    img = bpy.data.images.load(a.ref, check_existing=True)
    w, h = img.size
    if not w or not h:
        raise SystemExit("ERRO: não consegui ler o tamanho da imagem.")

    cd.show_background_images = True
    bg = next((b for b in cd.background_images if b.image == img), None)
    if bg is None:
        bg = cd.background_images.new()
        bg.image = img
    bg.alpha = a.opacity
    bg.display_depth = "FRONT"  # referência por cima, semitransparente: facilita alinhar bordas
    bg.frame_method = "FIT"

    s = a.long_edge / float(max(w, h))
    r = scene.render
    r.resolution_x, r.resolution_y = max(1, round(w * s)), max(1, round(h * s))
    r.resolution_percentage = 100
    scene.camera = cam

    info = dict(camera=cam.name, criada=created, referencia=a.ref, ref_px=[w, h],
                resolucao=[r.resolution_x, r.resolution_y], lente_mm=cd.lens, sensor_mm=cd.sensor_width,
                aviso="Background de câmera só aparece na vista de câmera (Numpad 0) e não é renderizado.")
    if a.save:
        if os.path.exists(a.save):
            raise SystemExit("ERRO: %s já existe. Use um nome de versão novo." % a.save)
        bpy.ops.wm.save_as_mainfile(filepath=a.save, copy=True)
        info["salvo_copia"] = a.save
    print("PP_REF_SETUP " + json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
