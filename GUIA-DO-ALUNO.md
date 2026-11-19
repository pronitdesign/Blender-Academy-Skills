# Guia do aluno — Blender Pixel Perfect

## Em uma frase

Você não pede "faz o objeto". Você conduz o Claude por **fases curtas**, e em cada uma ele te mostra uma prova real do Blender, com números, e espera seu ok.

```
F0 Briefing → F1 Câmera → F2 Blockout → F3 Forma → F4 Prova de material → F5 Lookdev → F6 Luz e render → F7 Entrega
```

## 1. Antes de começar

- Blender aberto (se for usar MCP ao vivo) ou só instalado (modo background).
- Uma pasta de projeto com suas referências em `refs/`.
- Referências que você tem direito de usar. Ideal: 4–8 fotos do **mesmo modelo**, uma vista principal, vistas de lado/topo, detalhes e **uma medida real**.

## 2. Primeiro pedido (copie e preencha)

```
/blender-pixel-perfect Quero criar [objeto] a partir das referências em refs/.

Vista principal: refs/[arquivo].
Medida real: [ex.: altura 14,2 cm].
Entrega: [imagem 3840×2160 PNG / glTF para site / vídeo 10 s 30 fps / .blend editável].
Precisa bater: [silhueta, logo, cor da marca...].
Pode aproximar: [parte de trás, parafusos...].

Comece pela F0: confira o ambiente sem alterar nada, crie a estrutura de pastas,
preencha o BRIEFING.md e me mostre o portão F0.
```

## 3. Durante as fases

Em cada portão você recebe: referência | captura do Blender | overlay (vermelho = falta, ciano = sobra), IoU, diferenças e incertezas. Responda com:

- **"Aprovado, siga para F[n]"**
- **"Ajuste: [problema visível]"** — seja específico ("a tampa está 3 mm mais alta", "o logo está mais à esquerda")
- **"Modo direto"** — sem explicações didáticas

### Ajuste localizado

```
Preserve [o que já foi aprovado] da versão [arquivo _v00X].
Ajuste somente [problema observável].
Mostre antes/depois com a mesma câmera e luz e confira a região ao lado.
```

### Só material/textura num modelo pronto

```
/blender-pixel-perfect O modelo em blend/[arquivo] está com a forma aprovada.
Comece na F4: faça a prova do material [alumínio escovado da tampa] num recorte
comparado com refs/[detalhe].jpg. Não mexa na geometria.
```

### Revisar um arquivo seu

```
/blender-pixel-perfect Rode o raio-X (scene_report) em blend/[arquivo].blend.
Não altere nem renderize. Explique cada problema e como eu corrijo no Blender.
```

## 4. O que significam os números

| Número | Leitura |
|---|---|
| IoU 1.000 | Silhueta idêntica na câmera da foto |
| IoU ≥ 0.985 | Pixel perfect para entrega (meta da F6) |
| IoU ≥ 0.975 | Forma final aprovável (F3) |
| IoU ≥ 0.94 | Blockout aprovável (F2) |
| "direita: modelo passa 9 px" | O lado direito está 9 px além da foto |

O IoU só olha o contorno. Botões, logos e materiais são conferidos em recortes lado a lado.

## 5. Checklist final

- [ ] Briefing com referência, medida, escopo e entrega definidos
- [ ] Câmera aprovada e congelada (F1)
- [ ] Blockout e forma com overlay aprovados (F2, F3)
- [ ] Material mais difícil testado em amostra antes de espalhar (F4)
- [ ] Raio-X sem erros de espaço de cor, UV ou imagem faltando (F5)
- [ ] Render conferido em quadro inteiro e recortes a 100% (F6)
- [ ] Entrega aberta e testada no destino, estado declarado (F7)
- [ ] DIARIO.md com versões, decisões e pendências

## 6. Atalhos do Blender que vão aparecer

| Atalho / local | Para quê |
|---|---|
| `Numpad 0` | Vista da câmera ativa |
| `Ctrl+A > Scale` | Aplicar escala (antes de bevel/UV) |
| `Shift+N` | Recalcular normais |
| `Alt+D` | Duplicata ligada (instância) |
| `Object Data > Background Images` | Referência atrás/na frente da câmera |
| UV Editor → Overlays → Display Stretch | Ver esticamento de UV |
| Color Management → View Transform → False Color | Checar exposição |
