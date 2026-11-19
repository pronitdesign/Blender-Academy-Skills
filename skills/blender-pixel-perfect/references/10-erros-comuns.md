# Diagnóstico: sintoma → causa → correção

Ao corrigir erro de aluno, explique a **causa** em uma frase antes de aplicar a correção.

## Forma e geometria

| Sintoma | Causa provável | Correção |
|---|---|---|
| Bevel mais grosso em um eixo | Escala do objeto não aplicada | `Ctrl+A > Scale`, refazer bevel |
| Faces pretas ou sombreamento estranho | Normais invertidas / escala negativa | `Shift+N` (Recalculate Outside), aplicar escala |
| Riscos/manchas em superfície lisa | N-gon ou triângulo longo em área curva; Auto Smooth inadequado | Holding edges, `Shade Auto Smooth`, Weighted Normal |
| Faixas tremendo entre duas superfícies (z-fighting) | Duas faces no mesmo lugar | Remover duplicata ou afastar decalque 0.05–0.1 mm |
| Reflexo "facetado" em peça redonda | Poucos segmentos | Mais segmentos ou Subdivision; checar com luz rasante |
| Modelo bate na frente e erra na lateral | Câmera/lente errada na F1 | Voltar à F1; não deformar o modelo |
| Logo flutuando ou atravessando o corpo curvo | Texto plano sem conformar | Shrinkwrap/Simple Deform com o raio do corpo |

## Textura e UV

| Sintoma | Causa provável | Correção |
|---|---|---|
| Relevo do normal map exagerado/lavado | Normal map em sRGB | Color Space Non-Color |
| Relevo parece afundar ao contrário | Normal map DirectX | Inverter canal verde |
| Material todo brilhante/fosco errado com mapa de rugosidade | Mapa em sRGB ou glossiness ligado como roughness | Non-Color; inverter gloss |
| Textura esticada | UV sem unwrap, escala não aplicada ou projeção Generated | Unwrap/Box projection; aplicar escala |
| Costura visível com linha colorida | Margem/padding insuficiente | Pack Islands com margem; bake margin 16 px |
| Textura rosa/magenta | Imagem não encontrada | `File > External Data > Find Missing Files` |
| Bake "sumiu" ao reabrir | Imagem assada não foi salva | `Image > Save As` após cada bake |
| Texto do rótulo borrado | Resolução abaixo da densidade necessária ou JPEG | Calcular texel; PNG; fonte vetorial |

## Material e luz

| Sintoma | Causa provável | Correção |
|---|---|---|
| Preto parece cinza lavado | Reflexo grande de luz/HDRI no material | Mover/reduzir luz, ajustar rugosidade; não escurecer a cor |
| Preto sem forma nenhuma | Base Color 0 e luz frontal | Albedo ~0.02–0.04, contraluz e cartões de reflexo |
| Metal parece plástico | Metallic < 1 ou falta algo para refletir | Metallic 1, HDRI/cartões no ambiente |
| Vidro preto ou com manchas escuras | Poucos bounces de transmissão | Transmission/Transparent bounces ≥ 8 |
| Pontos brancos (fireflies) | Luz pequena e forte, caustics | Luz maior, Clamp Indirect, Filter Glossy |
| Cor da marca diferente | Transformação de cor dessaturando, HEX tratado como linear | Converter HEX→linear; testar Khronos PBR Neutral |
| Render diferente do viewport | Modificadores diferentes em viewport/render, EEVEE vs Cycles | `scene_report.py` aponta; comparar sempre no mesmo motor |

## Processo

| Sintoma | Causa provável | Correção |
|---|---|---|
| "Cada correção estraga outra coisa" | Várias mudanças ao mesmo tempo | Uma causa por vez + checkpoint antes |
| IoU não sobe | Corrigindo detalhe com proporção geral errada | Voltar à ordem: proporção → posição → perfil |
| Render demora horas | Resolução/amostras finais em fase de prova | `render_stage.py` com estágio certo |
| Arquivo pesado e lento | Peças repetidas como cópias reais | Instâncias / Geometry Nodes; Linked Duplicate (`Alt+D`) |
