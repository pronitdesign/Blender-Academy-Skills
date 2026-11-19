# F1 — Casar a câmera com a foto

Sem a câmera certa, nenhuma silhueta bate, e o instinto errado é deformar o modelo. Por isso a câmera vem **antes** da forma.

## Passo a passo

1. `ref_setup.py --ref refs/hero.jpg --lens <palpite>`: cria `CAM_Ref`, põe a foto ao fundo (só aparece em `Numpad 0`) e ajusta a resolução ao aspecto exato da foto.
2. Crie um **proxy**: caixa ou cilindro com as dimensões reais conhecidas do objeto, origem na base, apoiado em Z = 0.
3. Ajuste nesta ordem, sem pular:
   1. **Lente** (focal) — define o quanto a perspectiva "abre".
   2. **Altura e inclinação** da câmera — horizonte e linhas verticais.
   3. **Distância e giro** (azimute) — tamanho e lado visível.
   4. **Shift X/Y** — só se a foto foi recortada ou feita com lente de descentralização (verticais retas em foto de cima/baixo).
4. Rode `silhouette_compare.py --fase F1` com o proxy. Meta: IoU ≥ 0.90 e cantos/linhas principais alinhados no overlay.

## Estimando a lente

| Pista na foto | Lente provável (equiv. full frame, sensor 36 mm) |
|---|---|
| Foto de celular, bordas esticadas, fuga forte | 24–28 mm |
| Foto de loja/e-commerce comum | 50–85 mm |
| Produto "achatado", linhas quase paralelas, fundo infinito | 85–200 mm |
| Vista técnica sem perspectiva | câmera **Orthographic** |

Teste: se a parte da frente parece muito maior que a de trás no modelo mas não na foto, a lente está curta demais (aumente a focal e afaste a câmera).

Fotos com metadados EXIF trazem a focal real e o modelo do sensor: converta para equivalente 36 mm (`focal × fator de corte`).

## Ferramentas úteis

- **fSpy** (app gratuito + add-on de importação): resolve câmera a partir de pontos de fuga. Ótimo para fotos com arestas retas. Instalar só com autorização do aluno.
- Guias de composição da câmera (`Camera > Viewport Display > Composition Guides`) ajudam a checar centro e terços.
- Opacidade do fundo 0.4–0.6 e `Display Depth: Front` facilitam alinhar bordas.

## Erros clássicos

- Mexer na escala do modelo para "caber" na foto → a escala real se perde. Mexa na câmera.
- Usar a lente padrão 50 mm sem pensar → perspectiva errada em quase toda foto de produto.
- Comparar com resolução de aspecto diferente da foto → todas as bordas parecem erradas.

## Portão F1

Mostre: captura em vista de câmera com a foto ao fundo + overlay do proxy + valores (lente, distância, altura, rotação). Registre a câmera aprovada no `DIARIO.md`. Daqui em diante **a câmera está congelada**; se precisar mudar, volte à F1 explicitamente.
