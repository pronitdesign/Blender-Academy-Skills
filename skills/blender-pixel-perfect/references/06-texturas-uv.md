# Texturas, UVs e bake

## Tipos de mapa e espaço de cor

| Mapa | Liga em | Color Space |
|---|---|---|
| Base Color / Albedo / Diffuse | Base Color | **sRGB** |
| Emission | Emission Color | **sRGB** |
| Roughness | Roughness | Non-Color |
| Metallic | Metallic | Non-Color |
| Normal | Normal Map node → Normal | Non-Color |
| Height / Displacement | Displacement node ou Bump | Non-Color |
| AO | (ver abaixo) | Non-Color |
| Alpha / Opacity / Máscaras | Alpha, Fac | Non-Color |
| ORM / ARM empacotado | Separate Color → R=AO, G=Rough, B=Metal | Non-Color |

`scene_report.py` acusa mapa de dados em sRGB e mapa de cor em Non-Color.

- **Normal DirectX vs OpenGL**: o Blender usa OpenGL. Mapas DirectX (comuns em Unreal/Substance com preset DX) têm o verde invertido: inverta o canal G (Separate Color → Math 1−G → Combine) antes do Normal Map. Sintoma: relevo parece "afundar" com a luz vindo de cima.
- **AO no Cycles**: não multiplique AO na cor; o Cycles já calcula a oclusão. Use AO só como máscara de sujeira. Em asset para tempo real, AO vai no canal próprio do glTF.
- **Gloss → Roughness**: mapa de glossiness precisa ser invertido.
- **Specular (fluxo antigo)** não se liga direto no Principled metálico; prefira conjuntos Metal/Rough.

## Resolução necessária (densidade de texel)

Regra: **pelo menos 1 texel por pixel de tela**, idealmente 1.5–2.

```
pixels_de_textura_necessários = largura_na_tela_em_px / fração_da_UV_que_a_ilha_ocupa
```

Exemplo: o rótulo aparece com 1200 px de largura no render 4K e a ilha do rótulo ocupa 50% da largura da UV → 2400 px → textura 4096. Se o mesmo rótulo só aparece em 600 px, 2048 sobra.

- Mantenha densidade parecida entre peças vizinhas (textura nítida ao lado de borrada denuncia CG). Confira com uma imagem **UV Grid/Color Grid** (`New Image > Generated Type`): os quadrados devem ter tamanho parecido em todas as peças.
- Para hero com muito detalhe, considere **UDIM** em vez de uma textura 8K única.

## UV unwrap: o que usar

| Forma | Método |
|---|---|
| Hard surface rápido | Smart UV Project (ângulo 30–66°) e depois revisar |
| Cilindros, alças, tiras | Seam numa linha escondida + Unwrap, ou Follow Active Quads |
| Rótulos e telas | Project From View na câmera frontal ou unwrap da face isolada, ilha retangular |
| Objetos orgânicos | Seams em áreas escondidas + Unwrap (Angle Based / Conformal) |

- Escala aplicada **antes** de desembrulhar.
- Ver esticamento: no UV Editor, Overlays → **Display Stretch**.
- **Margem** entre ilhas: 8–16 px numa 2K (Pack Islands, margin ~0.005–0.01). Sem margem, mipmaps e bake vazam cor nas costuras.
- Costuras onde a câmera não vê e onde o material já muda.

## Rótulos, logos e decalques

- Fonte vetorial (SVG/AI/PDF) sempre que possível; rasterize na resolução calculada acima em PNG. **Nunca JPEG para texto** (artefatos nas bordas).
- Rótulo como ilha própria (ou objeto próprio) para poder trocar a arte sem refazer o resto.
- Decalque em objeto separado: offset 0.05–0.1 mm da superfície ou use Shrinkwrap com offset; sem isso há z-fighting.
- Logo impresso com transparência: mix pelo alpha na Base Color e, se houver verniz, também na Roughness.

## Repetição e escala real

- Texture Coordinate **Object** + Mapping com escala em metros para procedurais; projeção **Box** com Blend 0.1–0.3 evita costuras em objetos sem UV.
- Quebre repetição de tile: misture duas escalas da mesma textura por um ruído grande, ou varie rotação/offset por célula de Voronoi.
- Confira a escala física: uma textura de madeira de 1 m não pode cobrir um porta-lápis de 10 cm com a veia do tamanho de uma prancha.

## Bake (quando o destino não é Cycles)

Necessário para glTF/web/jogos quando há procedurais, camadas ou alta → baixa poligonagem.

1. Crie a imagem de destino (Non-Color para dados, sRGB para cor), selecione o nó de imagem como ativo **em cada material**.
2. Cycles → Bake:
   - Cor: tipo **Diffuse**, só *Color* (desmarque Direct/Indirect).
   - Rugosidade: tipo **Roughness**.
   - Normal (alta → baixa): **Selected to Active**, Cage ou Extrusion pequena, Space Tangent.
   - Qualquer canal: ligue-o num Emission e asse **Emit**.
3. Margin 16 px.
4. **Salve a imagem** (Image → Save As). Bake fica só na memória até salvar — erro número 1 de aluno.

## Fontes de textura

Prefira fontes com licença clara (ex.: Poly Haven e ambientCG são CC0). Registre origem, licença e escala física no `DIARIO.md`. Logos e arte de marcas só com direito de uso para o fim do trabalho.
