"""Autoteste dos scripts da skill. Roda numa cena descartável (factory startup), sem tocar em projetos.

  blender -b --factory-startup --python-exit-code 1 --python selftest.py
"""
import json
import os
import runpy
import tempfile

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="pp_selftest_")


def run(script, args):
    runpy.run_path(os.path.join(HERE, script), run_name="__main__", init_globals={"ARGS": args})


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 0.1))
    cube = bpy.context.active_object
    cube.name = "Produto"
    cam = bpy.data.objects.new("CAM_Ref", bpy.data.cameras.new("CAM_Ref"))
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (0.45, -0.6, 0.35)
    con = cam.constraints.new("TRACK_TO")
    con.target = cube
    bpy.context.scene.camera = cam
    r = bpy.context.scene.render
    r.resolution_x, r.resolution_y = 800, 600
    return cube


def make_reference(path):
    sc = bpy.context.scene
    r = sc.render
    r.engine = "BLENDER_WORKBENCH"
    r.film_transparent = True
    r.image_settings.color_mode = "RGBA"
    r.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    cube = build()
    ref = os.path.join(TMP, "ref.png")
    make_reference(ref)
    run("ref_setup.py", ["--ref", ref, "--camera", "CAM_Ref", "--long-edge", "800"])

    run("silhouette_compare.py", ["--ref", ref, "--out", os.path.join(TMP, "igual"), "--fase", "F3"])
    same = json.load(open(os.path.join(TMP, "igual_silhueta.json")))
    assert same["iou"] >= 0.99, same

    cube.scale.x = 1.15
    run("silhouette_compare.py", ["--ref", ref, "--out", os.path.join(TMP, "maior"), "--fase", "F3"])
    big = json.load(open(os.path.join(TMP, "maior_silhueta.json")))
    assert big["iou"] < same["iou"] and not big["aprovado_silhueta"], big
    assert big["sobra_pct_da_ref"] > 1, big
    assert os.path.isfile(big["overlay"])

    run("scene_report.py", ["--json", os.path.join(TMP, "raiox.json")])
    rx = json.load(open(os.path.join(TMP, "raiox.json")))
    assert any(i["codigo"] == "escala_nao_aplicada" for i in rx["problemas"]), rx["problemas"]

    before = bpy.context.scene.render.engine
    run("render_stage.py", ["--stage", "clay", "--out", os.path.join(TMP, "clay.png"),
                            "--long-edge", "160", "--samples", "4", "--device", "CPU"])
    assert os.path.isfile(os.path.join(TMP, "clay.png"))
    assert bpy.context.scene.render.engine == before, "render_stage não restaurou o motor"
    assert bpy.context.view_layer.material_override is None

    run("save_version.py", ["--dir", TMP, "--name", "teste", "--tag", "F2"])
    run("save_version.py", ["--dir", TMP, "--name", "teste"])
    vers = sorted(f for f in os.listdir(TMP) if f.startswith("teste_v"))
    assert vers == ["teste_v001_F2.blend", "teste_v002.blend"], vers

    print("PP_SELFTEST_OK iou_igual=%.4f iou_maior=%.4f dicas=%s pasta=%s"
          % (same["iou"], big["iou"], big.get("dicas"), TMP))


main()
