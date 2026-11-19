#!/bin/sh
# Encontra o executável do Blender e mostra a versão. Uso: sh find_blender.sh
set -u
for c in "${BLENDER_BIN:-}" \
         /Applications/Blender.app/Contents/MacOS/Blender \
         "$HOME/Applications/Blender.app/Contents/MacOS/Blender" \
         "$(command -v blender 2>/dev/null)" \
         /snap/bin/blender /usr/bin/blender; do
  if [ -n "$c" ] && [ -x "$c" ]; then
    echo "BLENDER_BIN=$c"
    "$c" --version 2>/dev/null | head -1
    exit 0
  fi
done
echo "Blender não encontrado. Instale em https://www.blender.org/download/ ou defina BLENDER_BIN." >&2
echo "Windows: normalmente C:\\Program Files\\Blender Foundation\\Blender <versão>\\blender.exe" >&2
exit 1
