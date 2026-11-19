# Blender Pixel Perfect — skill para Claude Code

Skill para alunos usarem o **Claude Code com o Blender** e chegarem a modelos, texturas e renders fiéis à referência **em fases**, com portões de aprovação e **medição de silhueta em pixels** (IoU + overlay colorido), em vez de "construir tudo de uma vez e torcer".

## O que vem no pacote

```
skills/blender-pixel-perfect/
  SKILL.md                 método, regras e tabela de fases (o Claude lê primeiro)
  references/              01 briefing · 02 câmera · 03 modelagem · 04 comparação pixel
                           05 materiais PBR · 06 texturas/UV/bake · 07 luz e render
                           08 entrega · 09 controle do Blender (MCP/background) · 10 erros comuns
  scripts/                 silhouette_compare · ref_setup · render_stage · scene_report
                           save_version · find_blender.sh · selftest
  templates/               BRIEFING.md · DIARIO.md
GUIA-DO-ALUNO.md           passo a passo e prompts prontos
```

## Instalação (Claude Code)

**Pelo próprio Claude Code** (mais fácil): peça

```
Instale a skill blender-pixel-perfect do repositório github.com/pronitdesign/Blender-Academy-Skills
(pasta skills/blender-pixel-perfect) em ~/.claude/skills/. Se já existir, faça backup antes.
```

**Pelo terminal, para todos os projetos do aluno** (macOS/Linux):

```bash
git clone https://github.com/pronitdesign/Blender-Academy-Skills.git
```

```bash
mkdir -p ~/.claude/skills && cp -R Blender-Academy-Skills/skills/blender-pixel-perfect ~/.claude/skills/
```

Para atualizar depois: `git -C Blender-Academy-Skills pull` e copie a pasta de novo (faça backup da anterior).

**Só para um projeto**: copie a pasta para `<projeto>/.claude/skills/blender-pixel-perfect`.

Windows: copie a pasta para `%USERPROFILE%\.claude\skills\`.

Se já existir uma instalação, faça backup antes de substituir. Copie a **pasta inteira**: só o `SKILL.md` não basta, os scripts e references são usados durante o trabalho.

Conferir: abra o Claude Code numa nova sessão e peça

```
/blender-pixel-perfect confirme que você consegue ler a skill, as references e os scripts. Resuma as fases. Não altere nada no Blender.
```

## Requisitos

- Blender instalado (recomendado: versão LTS estável; scripts testados no 5.3). Os scripts rodam com o Python **do Blender** (`bpy`), não com o Python do sistema.
- Para controle ao vivo: um servidor MCP do Blender configurado no Claude Code e o add-on correspondente ativo no Blender. A skill não instala MCP nem add-ons. Siga o README do MCP escolhido; o formato geral no Claude Code é `claude mcp add <nome> -- <comando do servidor>`.
- Sem MCP, tudo funciona em background pelo terminal.

Teste rápido dos scripts (cena descartável, não toca em projetos):

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python-exit-code 1 --python ~/.claude/skills/blender-pixel-perfect/scripts/selftest.py
```

Deve terminar com `PP_SELFTEST_OK`.

## Ideia central

1. **Câmera antes da forma** — casar a câmera com a foto usando um proxy de medida real.
2. **Forma antes de material, material antes de luz final.**
3. **Cada fase termina num portão**: captura real do Blender + overlay + números + pausa para o aluno aprovar.
4. **O risco maior é testado pequeno** (F4) antes de espalhar pelo objeto.
5. **Checkpoints versionados** e nenhuma sobrescrita.
6. **Modo aula**: em cada portão o Claude explica o porquê e sugere um atalho/conceito para o aluno treinar.

## Limites

O IoU mede a silhueta numa câmera; não certifica detalhes internos, materiais nem vistas sem referência. Uma foto só valida a vista daquela foto. Resultado técnico limpo (sem erros no raio-X) não é aprovação visual.
