# F2 e F3 — Modelagem do blockout à forma final

## F2 Blockout: só volumes

- Construa os volumes primários com medidas reais, a partir do proxy da F1.
- Sem bevel, sem subdivisão, sem material (o `render_stage.py --stage clay` força cinza neutro).
- Origem de cada peça em um ponto lógico (base, eixo de rotação, dobradiça). Nomeie tudo: `Corpo`, `Tampa`, `Botao_Power`.
- Organize em coleções: `GEO`, `LUZ`, `CAM`, `REF`, `ARTE_FONTE` (textos/curvas editáveis).
- Escala do objeto sempre aplicada (`Ctrl+A > Scale`) antes de bevel, UV ou textura procedural.

Ordem de correção quando o overlay mostra erro: **proporção geral → posição das peças → perfil/curvatura**. Não refine um detalhe numa peça que ainda está no lugar errado.

Portão F2: clay da vista-alvo + overlay + IoU ≥ 0.94 + uma segunda vista (lado ou topo) para pegar erros de profundidade que a foto principal esconde.

## F3 Forma final: o que torna o objeto "real"

### Arestas e bevels
- Toda aresta visível precisa de bevel. Ordem de grandeza: eletrônicos 0.2–1 mm; móveis 1–3 mm; embalagem 0.1–0.5 mm.
- Prefira modificador **Bevel** (limit: Angle ~30°, segments 2–4, `Harden Normals`) antes de modelar à mão.
- Peças com curvatura suave: modelagem com holding edges + **Subdivision Surface**, ou bevel + `Shade Auto Smooth`.
- Teste com luz rasante: reflexos devem correr contínuos, sem facetas ou ondulação.

### Peças de revolução (garrafas, latas, potes, lentes)
- Desenhe o **perfil** como curva/meia seção e use **Screw** ou **Spin**. Segmentos suficientes para o brilho não facetar (64–128 em hero).
- Modele espessura real de parede onde houver transparência ou borda visível.

### Componentes (checklist do briefing)
Para cada componente: posição, tamanho, forma, profundidade (rebaixo ou saliência), como encosta no corpo. Regras:
- Um furo tem borda e fundo; um botão tem folga e assento; uma lente tem aro e vidro.
- Nunca troque um componente visível por um disco preto genérico.
- Não espelhe peças assimétricas sem evidência.

### Logos e texto em relevo
1. Guarde o original editável (Text ou curva SVG) em `ARTE_FONTE`, oculto.
2. Duplique para a versão visível e converta só a cópia.
3. Em superfície curva: **Shrinkwrap** (Target Normal Project) ou **Simple Deform/Curve** com o mesmo raio do corpo.
4. Relevo típico 0.2–0.6 mm com bevel 0.03–0.1 mm, para gerar sombra de contato.
5. Logo só impresso (sem relevo) fica na textura, não na geometria.

### Booleans
Use modificadores não destrutivos com o cortador numa coleção oculta. Aplique só em cópia, se o export exigir. Verifique n-gons e sombreamento no lugar do corte.

## Portão F3

- IoU ≥ 0.975 na vista-alvo.
- Checklist de componentes atualizado (observado → verificado) com crop de cada um.
- Uma vista extra sem regressão.
- `scene_report.py` sem `escala_negativa`/`escala_nao_aplicada` nas peças finais.

Forma aprovada **não** aprova material nem luz. Salve checkpoint `_F3`.
