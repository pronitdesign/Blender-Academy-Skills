"""Raio-X da cena, somente leitura: geometria, UVs, texturas, materiais e render.

Foco em erros que estragam fidelidade e textura sem fazer barulho:
escala não aplicada, mapa de normal em sRGB, imagem faltando, objeto sem UV usando textura,
material ausente, cor absoluta (preto 0 / branco 1), render fora de 100%, etc.

Não altera, não salva e não renderiza.

Background:
  blender -b projeto.blend --python scene_report.py -- [--json /abs/provas/raio-x_v003.json]
MCP:
  import runpy; runpy.run_path("/abs/.../scene_report.py", run_name="__main__", init_globals={"ARGS": []})
"""
import argparse
import json
import os
import sys

import bpy

DATA_HINTS = ("normal", "nrm", "_nor", "rough", "metal", "_ao", "ambient", "occlusion", "disp", "height",
              "bump", "mask", "opacity", "gloss", "spec", "orm", "arm", "cavity", "curv")
COLOR_HINTS = ("albedo", "basecolor", "base_color", "diffuse", "diff_", "_col", "color", "emissive", "emission")
DATA_SOCKETS = {"Roughness", "Metallic", "Normal", "Alpha", "IOR", "Specular IOR Level", "Coat Weight",
                "Coat Roughness", "Transmission Weight", "Anisotropic", "Height", "Strength", "Distance"}


def _argv():
    if "ARGS" in globals():
        return list(globals()["ARGS"])
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def linked_targets(tree, node, depth=0):
    """Sockets de destino alcançados a partir de um nó (atravessa nós intermediários simples)."""
    out = set()
    if depth > 6:
        return out
    for link in tree.links:
        if link.from_node == node:
            out.add(link.to_socket.name)
            if link.to_node.type in ("NORMAL_MAP", "BUMP", "MATH", "MAP_RANGE", "SEPARATE_COLOR",
                                     "SEPRGB", "INVERT", "GAMMA", "CURVE_RGB", "VALTORGB", "REROUTE",
                                     "DISPLACEMENT"):
                out.add("via:" + link.to_node.type)
                out |= linked_targets(tree, link.to_node, depth + 1)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", help="Salvar relatório neste caminho (novo).")
    a = p.parse_args(_argv())
    scene = bpy.context.scene
    issues = []

    def flag(nivel, codigo, onde, dica):
        issues.append(dict(nivel=nivel, codigo=codigo, onde=onde, dica=dica))

    us = scene.unit_settings
    rep = dict(blender=bpy.app.version_string, arquivo=bpy.data.filepath or "(não salvo)", cena=scene.name,
               unidades=dict(sistema=us.system, escala=us.scale_length, comprimento=us.length_unit))
    if us.scale_length != 1.0:
        flag("revisar", "escala_unidade", "cena", "Unit Scale diferente de 1 complica medidas reais e export.")

    # ---------- objetos / geometria ----------
    dg = bpy.context.evaluated_depsgraph_get()
    objs = []
    for o in scene.objects:
        row = dict(nome=o.name, tipo=o.type)
        if o.type in ("MESH", "CURVE", "FONT", "SURFACE"):
            sc = tuple(round(v, 4) for v in o.scale)
            row["escala"] = sc
            if any(v < 0 for v in sc):
                flag("erro", "escala_negativa", o.name, "Escala negativa inverte normais. Ctrl+A > Scale e recalcule normais.")
            elif any(abs(v - 1) > 1e-3 for v in sc):
                flag("revisar", "escala_nao_aplicada", o.name,
                     "Escala não aplicada distorce bevel, UV e texturas procedurais. Ctrl+A > Scale (se não for instância).")
            row["dimensoes_m"] = tuple(round(v, 4) for v in o.dimensions)
        if o.type == "MESH":
            me = o.data
            ev = o.evaluated_get(dg)
            tri = None
            try:
                em = ev.to_mesh()
                em.calc_loop_triangles()
                tri = len(em.loop_triangles)
            finally:
                ev.to_mesh_clear()
            ngons = sum(1 for poly in me.polygons if len(poly.vertices) > 4)
            row.update(vertices=len(me.vertices), triangulos_avaliados=tri, ngons=ngons,
                       uvs=[uv.name for uv in me.uv_layers], materiais=[m.name if m else None for m in me.materials],
                       modificadores=[m.type for m in o.modifiers], shade_smooth=any(poly.use_smooth for poly in me.polygons))
            if not me.materials or all(m is None for m in me.materials):
                if not o.hide_render:
                    flag("revisar", "sem_material", o.name, "Objeto visível sem material renderiza cinza padrão.")
            uses_img = any(m and m.use_nodes and any(n.type == "TEX_IMAGE" for n in m.node_tree.nodes)
                           for m in me.materials)
            if uses_img and not me.uv_layers:
                flag("erro", "textura_sem_uv", o.name, "Usa Image Texture mas não tem UV. Faça unwrap (U) ou use projeção Box.")
            if any(m.show_viewport != m.show_render for m in o.modifiers):
                flag("revisar", "modificador_viewport_render", o.name,
                     "Viewport e render avaliam modificadores diferentes: o preview não representa o render.")
        objs.append(row)
    meshes = [r for r in objs if r["tipo"] == "MESH"]
    rep["objetos"] = len(objs)
    rep["maiores_por_triangulos"] = sorted(meshes, key=lambda r: -(r.get("triangulos_avaliados") or 0))[:12]
    rep["triangulos_total"] = sum(r.get("triangulos_avaliados") or 0 for r in meshes)

    # ---------- imagens ----------
    imgs = []
    for im in bpy.data.images:
        if im.type != "IMAGE" or im.source not in ("FILE", "TILED"):
            continue
        path = bpy.path.abspath(im.filepath, library=im.library) if im.filepath else ""
        missing = not im.packed_file and (not path or not os.path.exists(path.replace("<UDIM>", "1001")))
        cs = im.colorspace_settings.name
        imgs.append(dict(nome=im.name, caminho=path, tamanho=list(im.size), espaco_de_cor=cs,
                         empacotada=bool(im.packed_file), faltando=missing, usuarios=im.users))
        if missing:
            flag("erro", "imagem_faltando", im.name, "Arquivo não encontrado: %s. Use File > External Data > Find Missing." % path)
    rep["imagens"] = imgs

    # ---------- materiais / espaço de cor ----------
    mats = []
    for m in bpy.data.materials:
        if not m.use_nodes or m.users == 0:
            continue
        nt = m.node_tree
        mrow = dict(nome=m.name, nos=len(nt.nodes), usuarios=m.users,
                    principled=sum(1 for n in nt.nodes if n.type == "BSDF_PRINCIPLED"))
        for n in nt.nodes:
            if n.type == "TEX_IMAGE" and n.image:
                cs = n.image.colorspace_settings.name
                is_data_cs = cs in ("Non-Color", "Linear", "Raw", "Generic Data", "Data") or "Non" in cs
                targets = linked_targets(nt, n)
                feeds_data = bool(targets & DATA_SOCKETS) or "via:NORMAL_MAP" in targets or "via:BUMP" in targets
                feeds_color = bool(targets & {"Base Color", "Emission Color", "Color"}) and not feeds_data
                low = n.image.name.lower()
                if feeds_data and not is_data_cs:
                    flag("erro", "espaco_de_cor_dados", "%s > %s" % (m.name, n.image.name),
                         "Mapa de dados (normal/rough/metal/altura) deve estar em Non-Color, não %s." % cs)
                elif feeds_color and is_data_cs:
                    flag("erro", "espaco_de_cor_cor", "%s > %s" % (m.name, n.image.name),
                         "Mapa de cor ligado em Base Color/Emissão deve estar em sRGB.")
                elif not targets and any(h in low for h in DATA_HINTS) and not is_data_cs:
                    flag("revisar", "espaco_de_cor_nome", n.image.name, "Nome sugere mapa de dados; confira Non-Color.")
            if n.type == "BSDF_PRINCIPLED":
                bc = n.inputs["Base Color"]
                if not bc.is_linked:
                    rgb = tuple(bc.default_value)[:3]
                    if max(rgb) <= 0.0:
                        flag("revisar", "preto_absoluto", m.name, "Base Color 0,0,0 mata reflexos e detalhe. Use ~0.01–0.03 linear.")
                    if min(rgb) >= 1.0:
                        flag("revisar", "branco_absoluto", m.name, "Base Color 1,1,1 é irreal. Use no máximo ~0.8–0.9 linear.")
        mats.append(mrow)
    rep["materiais"] = mats

    # ---------- render ----------
    r = scene.render
    vs = scene.view_settings
    rep["render"] = dict(motor=r.engine, camera=scene.camera.name if scene.camera else None,
                         resolucao=[r.resolution_x, r.resolution_y, r.resolution_percentage],
                         transformacao_de_cor=vs.view_transform, look=vs.look, exposicao=vs.exposure,
                         saida=r.filepath, formato=r.image_settings.file_format,
                         profundidade=r.image_settings.color_depth)
    if hasattr(scene, "cycles"):
        c = scene.cycles
        rep["render"]["cycles"] = dict(dispositivo=c.device, amostras=c.samples,
                                       limiar_adaptativo=c.adaptive_threshold, denoise=c.use_denoising,
                                       bounces=[c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces])
    if not scene.camera:
        flag("erro", "sem_camera", "cena", "Sem câmera ativa: não há vista-alvo para comparar.")
    if r.resolution_percentage != 100:
        flag("revisar", "resolucao_parcial", "render", "Resolution %% = %d. Entregas finais pedem 100%%." % r.resolution_percentage)
    if vs.view_transform not in ("AgX", "Filmic", "Khronos PBR Neutral"):
        flag("revisar", "transformacao_de_cor", "render",
             "View Transform '%s'. Para produto realista prefira AgX (ou Khronos PBR Neutral para cor fiel)." % vs.view_transform)

    rep["problemas"] = issues
    rep["resumo"] = dict(erros=sum(i["nivel"] == "erro" for i in issues),
                         revisar=sum(i["nivel"] == "revisar" for i in issues),
                         aviso="Relatório limpo não significa fidelidade visual aprovada.")
    payload = json.dumps(rep, indent=2, ensure_ascii=False, default=str)
    if a.json:
        if os.path.exists(a.json):
            raise SystemExit("ERRO: %s já existe." % a.json)
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        with open(a.json, "w") as f:
            f.write(payload)
    print("PP_RAIOX_INICIO")
    print(payload)
    print("PP_RAIOX_FIM")


if __name__ == "__main__":
    main()
