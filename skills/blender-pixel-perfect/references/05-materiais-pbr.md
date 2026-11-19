# Materiais PBR: valores de partida e construção em camadas

Use os valores como **ponto de partida medido**, depois ajuste olhando a referência sob luz parecida. Nomes de entrada do Principled BSDF mudam entre versões: procure o nó pelo tipo (`BSDF_PRINCIPLED`) e confira os nomes das entradas na versão do aluno antes de escrever o script.

> Cores abaixo estão em **RGB linear** (os campos R, G, B do seletor de cor do Blender). O campo Hex do Blender é sRGB, não confunda.

## Regras físicas que resolvem 80% dos casos

1. **Metal ou não metal**, sem meio-termo: `Metallic` 1 ou 0. Valores intermediários só em máscaras de transição (ferrugem, tinta descascada).
2. Em metal, a cor vai em `Base Color` e é a cor do **reflexo**. Em não metal, `Base Color` é a cor difusa.
3. **Rugosidade conta a história**: a mesma cor vira plástico brilhante, fosco ou borracha só mudando `Roughness`.
4. Albedo de não metal entre ~0.02 (carvão, borracha) e ~0.9 (neve). Preto 0 e branco 1 não existem.
5. Detalhe pequeno de superfície vem de **variação de rugosidade** antes de vir de cor.

## Metais (Metallic = 1)

| Metal | Base Color (linear) | Roughness típico |
|---|---|---|
| Alumínio | 0.91, 0.92, 0.92 | polido 0.05–0.15 · escovado 0.25–0.4 · jateado 0.4–0.55 |
| Prata | 0.96, 0.95, 0.92 | 0.05–0.25 |
| Ouro | 1.00, 0.77, 0.34 | 0.1–0.3 |
| Cobre | 0.96, 0.64, 0.54 | 0.15–0.35 |
| Latão | 0.91, 0.78, 0.42 | 0.15–0.35 |
| Ferro/aço | 0.53, 0.51, 0.50 | 0.2–0.5 |
| Cromo | 0.55, 0.56, 0.55 | 0.02–0.1 |
| Titânio | 0.54, 0.50, 0.45 | 0.2–0.4 |

- **Escovado**: `Anisotropic` 0.5–0.8 com `Tangent` alinhado ao sentido da escovação (radial em tampas: Tangent Radial; linear: UV). Reforce com ruído esticado na rugosidade.
- **Anodizado colorido**: metal com Base Color saturada, roughness 0.25–0.45. Não use emissão para "brilhar".

## Não metais (Metallic = 0)

| Material | Base Color (linear) | Roughness | Extra |
|---|---|---|---|
| Plástico brilhante | cor da peça | 0.05–0.2 | IOR 1.46–1.5 |
| Plástico fosco / injetado | cor da peça | 0.4–0.7 | textura de injeção leve no bump |
| Plástico preto | 0.02–0.04 | 0.3–0.6 | nunca 0; o brilho mostra a forma |
| Borracha | 0.02–0.05 | 0.6–0.9 | Specular IOR Level ~0.3 |
| Vidro | branco | 0–0.05 | Transmission 1, IOR 1.5, espessura modelada |
| Acrílico | branco/cor | 0–0.05 | Transmission 1, IOR 1.49 |
| Água / gotas | branco | 0–0.03 | Transmission 1, IOR 1.333 |
| Cerâmica esmaltada | cor | 0.3–0.5 | Coat 1, Coat Roughness 0.02–0.05 |
| Pintura automotiva | cor | 0.3–0.4 (base) | Coat 1, Coat Roughness 0.01–0.05, flocos via Voronoi no normal da base |
| Madeira envernizada | textura | 0.4–0.6 | Coat 0.5–1 |
| Couro | textura | 0.4–0.65 | bump de grão fino |
| Tecido | textura | 0.8–1.0 | Sheen Weight 0.3–1, trama em normal |
| Papel / papelão | textura | 0.7–0.9 | Sheen leve; papel fino: um pouco de Subsurface |
| Pele | tom de pele | 0.35–0.5 | Subsurface Weight 0.1–0.3, Scale em metros (~0.005–0.01) |
| Tela ligada | preto 0.01 | 0.05 | imagem em Emission Color, força calibrada pela exposição |

## Construção em camadas (pense como fábrica)

Monte na ordem em que o objeto foi fabricado:

1. **Substrato** (metal, plástico, papel).
2. **Pintura/tinta** (cor, rugosidade própria).
3. **Verniz/coat** (`Coat Weight`, com rugosidade e normal próprios).
4. **Gráficos** (tinta, verniz localizado, hot stamping) por máscara.
5. **Uso real**: digitais e manchas na rugosidade, poeira em superfícies voltadas para cima, desgaste em quinas.

Máscaras úteis: `Geometry > Pointiness` (só Cycles) e `Ambient Occlusion` para quinas e cavidades; `Normal Z` para poeira; texturas de imperfeição (smudge/fingerprint) em rugosidade com contraste baixo.

## Dicas de especialista

- **Nó Bevel** (Cycles) no normal arredonda visualmente arestas de 0.1–0.5 mm sem geometria: ótimo para peças pequenas e logos.
- **Líquido em vidro**: o volume de líquido deve invadir levemente a parede interna do vidro (0.1 mm); o Cycles resolve a interface corretamente. Deixar um vão de ar gera uma borda falsa.
- **Vidro escuro sobre tela**: separe vidro, bezel preto e tela em materiais distintos; a tela emite, o vidro só reflete.
- **Preto sobre preto**: diferencie por rugosidade e relevo (verniz localizado: mesma cor, roughness 0.15 contra 0.5 ao redor).
- **Cor de marca**: converta o HEX da marca para linear e confira com transformação *Khronos PBR Neutral* ou *Standard*; AgX dessatura cores muito saturadas de propósito.
- Material aprovado pode mudar de cara em outra forma ou luz: ao reutilizar, teste na nova geometria antes de declarar aprovado. Se alterar, crie variação nomeada (`Aluminio_escovado_v2`).

## Portão F4 (prova de material)

Renderize **só o trecho mais arriscado** (`render_stage.py --stage lookdev --crop ...`) com a câmera e luz definidas, ao lado do mesmo crop da referência. Avalie em voz alta: cor, nível de brilho, tamanho do reflexo, rugosidade, relevo, contato. Só replique o material para o resto do objeto depois de aprovado.
