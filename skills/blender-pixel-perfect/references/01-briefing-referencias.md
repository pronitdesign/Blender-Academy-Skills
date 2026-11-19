# F0 — Briefing e referências

Objetivo: transformar "faz esse objeto" em um contrato verificável antes de tocar no Blender.

## 1. Montar o pacote de referência

Ideal: 4 a 8 imagens úteis do **mesmo modelo, versão e acabamento**.

| Tipo | Para que serve | Prioridade |
|---|---|---|
| Vista-alvo (hero) | É a imagem que vamos bater pixel a pixel | obrigatória |
| Frente / lado / topo (de preferência com tele, pouca distorção) | Proporções e perfis | alta |
| Detalhes (logo, botões, costura, conectores) | Componentes e textura | alta |
| Uma medida real (spec do fabricante, régua, ficha técnica) | Escala em metros | alta |
| Referência de clima/arte (luz, fundo, mood) | Só direção de arte, **nunca** forma | opcional |

Mais vale um ângulo novo do que cinco fotos quase iguais.

## 2. Classificar cada imagem

Para cada arquivo em `refs/`, anote no `BRIEFING.md`:

- **Forma** (serve para geometria), **Superfície** (serve para material/textura) ou **Arte** (só clima).
- Lente aparente: tele (linhas quase paralelas) ou grande-angular (bordas esticadas, fuga forte). Ver `02-camera-match.md`.
- Conflitos: duas fotos com versões diferentes do produto? Escolha uma e registre.

Imagens geradas por IA, renders de terceiros e mockups **não provam** forma oculta. Podem sugerir, nunca validar.

## 3. Decompor o objeto

Liste em tabela (vai virar o checklist da F3):

| # | Componente | Forma base | Material | Fonte (arquivo/crop) | Status |
|---|---|---|---|---|---|
| 1 | Corpo | cilindro com chanfro | alumínio anodizado | hero.jpg, lado.jpg | observado |
| 2 | Logo frontal | texto em relevo 0.3 mm | tinta fosca | detalhe_logo.jpg | observado |
| 3 | Fundo | — | — | sem foto | suposição |

Status possíveis: **observado** · **suposição** · **falta referência** · **verificado** (só depois do portão).

## 4. Identificar o maior risco

Pergunte: "qual parte, se sair errada, faz o objeto parecer falso?" Exemplos: vidro sobre metal, logo curvo, tecido com costura, pelo com acessório, gotas de condensação, preto sobre preto. Esse será o teste da **F4**.

## 5. Escopo honesto

Escolha e declare um:

- **Bater a vista-alvo**: fidelidade garantida só naquele ângulo; o resto é plausível.
- **Objeto completo**: exige refs de todos os lados e uma medida. Se faltar, peça antes de prometer.

## 6. Destino da entrega

Imagem (tamanho exato em px e aspecto), vídeo (fps, duração), arquivo 3D para web/app/jogo (formato, limite de triângulos/MB), mockup, ou `.blend` editável. Cada destino tem validação própria (`08-entrega.md`).

## Portão F0

Mostre ao aluno: resumo do briefing, tabela de componentes, maior risco, escopo e o que falta. Espere aprovação.
