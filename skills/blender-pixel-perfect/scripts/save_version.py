"""Salva um checkpoint versionado SEM sobrescrever nada: <pasta>/<nome>_v001.blend, _v002 ...

A sessão continua no arquivo atual (save copy). Use ao final de cada fase aprovada.

Background:
  blender -b projeto.blend --python save_version.py -- --dir /abs/blend --name relogio --tag F2_blockout
MCP:
  import runpy; runpy.run_path("/abs/.../save_version.py", run_name="__main__",
      init_globals={"ARGS": ["--dir", "/abs/blend", "--name", "relogio", "--tag", "F2_blockout"]})
"""
import argparse
import hashlib
import json
import os
import re
import sys

import bpy


def _argv():
    if "ARGS" in globals():
        return list(globals()["ARGS"])
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", required=True)
    p.add_argument("--name", required=True, help="Nome base do projeto (sem versão).")
    p.add_argument("--tag", default="", help="Rótulo opcional, ex.: F3_forma_aprovada")
    a = p.parse_args(_argv())
    os.makedirs(a.dir, exist_ok=True)
    pat = re.compile(r"^%s_v(\d{3})" % re.escape(a.name))
    nums = [int(m.group(1)) for f in os.listdir(a.dir) if (m := pat.match(f))]
    n = max(nums, default=0) + 1
    tag = ("_" + re.sub(r"[^A-Za-z0-9_-]", "", a.tag)) if a.tag else ""
    path = os.path.join(a.dir, "%s_v%03d%s.blend" % (a.name, n, tag))
    if os.path.exists(path):
        raise SystemExit("ERRO: %s já existe." % path)
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()[:16]
    print("PP_VERSAO " + json.dumps(dict(arquivo=path, versao=n, sha256_16=digest,
                                         blender=bpy.app.version_string), ensure_ascii=False))


if __name__ == "__main__":
    main()
