# Controlando o Blender: MCP ao vivo e Python em background

A skill é o **método**. Quem executa no Blender é uma destas duas vias:

| Via | Quando usar | Vantagem | Cuidado |
|---|---|---|---|
| **MCP (ao vivo)** | Blender aberto, aluno acompanhando | Vê o resultado na hora, captura de tela | Mexe na sessão do aluno: checkpoint antes de mudanças grandes |
| **Python em background** | Renders, auditorias, builds repetíveis | Determinístico, não trava a interface | Trabalhar sempre numa cópia versionada |

## Primeiros comandos de uma sessão MCP

1. Status/versão do Blender e add-on (ex.: `get_addon_status`, se existir).
2. Info da cena (ex.: `get_scene_info`): objetos, câmera, arquivo aberto. **Sem alterar nada.**
3. Confirmar com o aluno qual arquivo é o certo e se já existe checkpoint.
4. Rodar `save_version.py` antes da primeira alteração.

Os nomes das ferramentas variam conforme o servidor MCP instalado (`execute_blender_code`, `look`, `get_viewport_screenshot`...). Use o que estiver disponível e diga ao aluno qual está usando.

## Regras para código enviado ao Blender ao vivo

- **Idempotente**: "pegue ou crie pelo nome" (`bpy.data.objects.get("Corpo") or ...`). Rodar duas vezes não pode duplicar objetos.
- Scripts curtos, um objetivo por vez; imprima o que mudou.
- Prefira a API de dados (`bpy.data`, `obj.modifiers.new`) a `bpy.ops`, que depende de contexto/seleção.
- Nós de shader: procure por **tipo** (`n.type == "BSDF_PRINCIPLED"`), não pelo nome (pode estar traduzido se a interface estiver em português).
- Entradas do Principled mudaram entre versões (ex.: `Specular` → `Specular IOR Level`, `Clearcoat` → `Coat Weight`). Liste `[i.name for i in bsdf.inputs]` antes de atribuir.
- Enums (motor, formato): leia os valores válidos ou use `try/except TypeError`.
- Cor de material vai nas entradas do nó; `material.diffuse_color` é só viewport.
- Nunca: limpar a cena inteira, deletar coleções que não criou, sobrescrever o arquivo aberto, instalar/habilitar add-ons sem pedir.
- Mudanças por código podem não entrar no Undo como o aluno espera: por isso o checkpoint.

## Ver o resultado

- Para comparação com a referência, capture **em vista de câmera** (`CAM_Ref`) com a foto de fundo ligada ou desligada conforme o objetivo.
- Captura de viewport é prova de forma/layout. Prova de material exige render Cycles (`render_stage.py --stage lookdev`).
- Capturas menores economizam contexto: 800–1200 px para forma, crop para detalhe.

## Rodar os scripts da skill pelo MCP

```python
import runpy
SKILL = "/Users/<aluno>/.claude/skills/blender-pixel-perfect"
runpy.run_path(SKILL + "/scripts/scene_report.py", run_name="__main__", init_globals={"ARGS": []})
```

Os scripts imprimem blocos marcados (`PP_SILHUETA_INICIO`, `PP_RAIOX_INICIO`, `PP_RENDER`, `PP_VERSAO`) fáceis de localizar na saída.

## Rodar em background (terminal)

```bash
sh "$SKILL/scripts/find_blender.sh"          # mostra BLENDER_BIN e versão
"$BLENDER_BIN" -b /abs/blend/nome_v004.blend --python "$SKILL/scripts/scene_report.py"
```

- Caminhos absolutos sempre.
- Em arquivos de terceiros, adicione `--disable-autoexec` para não rodar scripts embutidos.
- `--python-exit-code 1` faz o terminal acusar erro de script.

## Geração e bibliotecas de assets

Alguns servidores MCP importam modelos de bibliotecas ou geram 3D por IA (podem custar créditos: pergunte antes). Use apenas para **objetos de cena secundários** ou como referência de volume. Nunca entregue um modelo gerado como "fiel" à referência: ele não passa pelos portões de forma. Modelos importados chegam em escala arbitrária: ajuste pelas dimensões reais e apoie no chão.
