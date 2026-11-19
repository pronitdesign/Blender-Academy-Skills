# F6 — Luz de estúdio e render

## Leia a luz da referência primeiro

Antes de criar luzes, descreva a foto: de onde vem a luz principal (sombra e brilho dizem), o tamanho da fonte (sombra dura = fonte pequena; reflexo grande e macio = softbox grande), se há contraluz no contorno, cor do fundo e se o objeto encosta no chão (sombra de contato).

## Montagem base de estúdio

| Luz | Tipo | Posição | Função |
|---|---|---|---|
| Key | Area grande (retângulo) | 30–60° de lado, um pouco acima | Define forma e reflexo principal |
| Fill | Area fraca ou cartão rebatedor | lado oposto | Abre sombra sem achatar |
| Rim / contraluz | Area estreita (strip) | atrás, de lado | Separa contorno do fundo |
| Top | Area grande e suave | acima | Gradiente em superfícies horizontais |
| Cartões de reflexo | Plano emissivo | fora do quadro | Desenham faixas em metal e vidro |

- Cartões de reflexo: em `Object > Visibility > Ray Visibility`, desligue **Camera** para não aparecerem no render.
- HDRI de estúdio neutro dá reflexos ricos; combine com áreas para controle. Gire o HDRI para posicionar os reflexos.
- **Light Linking** (Blender 4+) limita uma luz a certos objetos: útil para tirar um reflexo indesejado do vidro sem mexer no resto.
- Luz rasante revela relevo (logos, texturas); luz frontal achata.
- **Produto escuro em fundo escuro**: resolva com contraluz e cartões de reflexo, não clareando o material.

## Exposição e cor

- Acerte a exposição em `Color Management > Exposure` ou na potência das luzes, nunca no Base Color.
- Use temporariamente a transformação **False Color** para ver se há áreas estouradas (vermelho/branco) ou esmagadas (azul escuro), e volte para AgX.
- AgX é o padrão; para cor de marca exata considere *Khronos PBR Neutral*. Registre a escolha.
- Profundidade de campo: fotos de produto costumam ser f/8–f/16 (quase tudo nítido). Use DOF só se a referência mostrar desfoque.

## Render em estágios (`render_stage.py`)

| Estágio | Para quê | Padrão do script |
|---|---|---|
| `clay` | forma e luz sem material | Cycles 64 amostras, 1200 px, material cinza forçado |
| `preview` | layout/composição | EEVEE, 1500 px — **não** é prova de material |
| `lookdev` | prova de material/textura, crops | Cycles 256, limiar 0.02, 1800 px |
| `final` | entrega | Cycles 1024, limiar 0.008, resolução definida pelo aluno |

Ordem na F6: lookdev da vista-alvo → correções → validação ~2K com crops a 100% → segunda correção → master na resolução final. Não lance um master enquanto existir diferença conhecida de forma ou câmera.

Ajustes que costumam ser necessários:
- Vidro e líquido: `Light Paths > Transmission` e `Transparent` ≥ 8.
- Fireflies: `Clamp Indirect` 5–10; aumente o tamanho das luzes pequenas; Filter Glossy 0.5–1 se necessário.
- Denoise OpenImageDenoise no final; confira se não borrou texto fino ou textura (crop a 100%).
- Banding em gradientes: salve 16 bits (PNG 16 ou EXR).

## Defina a saída com números

"4K" não é resolução. Escreva largura × altura e aspecto: 16:9 4K = 3840×2160; 4:5 vertical = 2160×2700; quadrado = 2160×2160. Mantenha o aspecto aprovado na F1 ou recorte de propósito.

Master: PNG 16 bits ou EXR. JPEG é derivado para revisão/web.

## Quality gates do render

Olhe o quadro inteiro e crops a 100% de: silhueta e bevels, logos e texto fino, pretos (separados, não esmagados), vidro e metal, contato com o chão, ruído, fireflies, borrado do denoise, banding, altas luzes estouradas. Rode `silhouette_compare.py --fase F6` no master (IoU ≥ 0.985).

Antes de um render longo, meça o tempo de um quadro (o script imprime os segundos e o dispositivo usado) e informe a estimativa. Em animação: tempo de um quadro × número de quadros, e renderize sequência de PNG/EXR (retomável), nunca direto em vídeo.
