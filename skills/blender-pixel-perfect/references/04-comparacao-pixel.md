# Comparação pixel a pixel

"Pixel perfect" aqui tem definição: **na câmera da referência, a silhueta do modelo cobre a mesma área que o objeto da foto**, medida por IoU (interseção ÷ união das duas máscaras).

## Rodar

```bash
"$BLENDER_BIN" -b blend/nome_v004.blend --python "$SKILL/scripts/silhouette_compare.py" -- \
  --ref "$PWD/refs/hero.jpg" --out "$PWD/provas/F2_v004" --fase F2 --hide Chao,Fundo
```

Ao vivo (MCP), com o arquivo aberto:

```python
import runpy
runpy.run_path(SKILL + "/scripts/silhouette_compare.py", run_name="__main__",
    init_globals={"ARGS": ["--ref", REF, "--out", PROJ + "/provas/F2_v004", "--fase", "F2", "--hide", "Chao"]})
```

Saídas: `*_silhueta.json` e `*_overlay.png` (vermelho = falta no modelo, ciano = sobra, cinza = acerto). **Sempre olhe o overlay**, não só o número.

## Máscara da referência

| Situação | Melhor opção |
|---|---|
| Foto em fundo branco/liso | Automático (chave de fundo). Ajuste `--tol` (0.08–0.2) se borda falhar |
| PNG recortado com transparência | Automático (canal alfa) |
| Fundo complexo, sombra no chão, reflexo | `--ref-mask` (recorte feito no Photoshop/GIMP/Remove BG: branco = objeto) |
| Objeto vazado (alça, aro, armação) | `--keep-holes` |
| Objeto escuro em fundo escuro | `--ref-mask` |

Esconda chão, fundo e luzes visíveis com `--hide`.

## Metas por fase

| Fase | IoU mínimo | Outras exigências |
|---|---|---|
| F1 (proxy) | 0.90 | Linhas e cantos do proxy coincidem |
| F2 (blockout) | 0.94 | Nenhuma borda com erro > 1% do lado maior |
| F3 (forma final) | 0.975 | Componentes verificados em crop |
| F6 (render final) | 0.985 | Mesma câmera congelada da F1 |

Os limiares assumem objeto ocupando boa parte do quadro. Objetos pequenos no quadro → recorte a referência em volta do objeto, ou aumente `--max-edge`.

## Ler os números

- **falta > sobra**: modelo menor que a foto. **sobra > falta**: maior.
- **bordas_px**: diz qual lado corrigir e quanto. Duas bordas opostas "passando" = largura grande demais; uma só = posição/rotação.
- **centro_delta_px** grande com IoU bom: deslocamento, não forma. Normalmente é câmera.
- IoU estagnado com bordas todas pequenas: o problema está no perfil (curvatura, chanfro), veja o overlay.

## Limites (diga isso ao aluno)

- Mede só **silhueta** e só **nesta câmera**. Detalhes internos (botões, logos) exigem crop lado a lado.
- Silhueta igual com câmera errada é possível em casos simétricos: confirme com uma 2ª vista.
- A foto pode ter distorção de lente; se as bordas da foto são curvas e o modelo reto, documente em vez de entortar o modelo.

## Comparação de detalhes (crops)

Para componentes, material e textura, renderize o mesmo recorte da referência com `render_stage.py --crop xmin,xmax,ymin,ymax` (0–1, y a partir de baixo) e mostre lado a lado na mesma escala. Avalie: posição, tamanho, borda, profundidade, brilho, rugosidade, cor sob a mesma luz.
