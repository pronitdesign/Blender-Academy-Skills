# F7 — Entrega e validação no destino

## Estados de entrega (sempre declare um)

| Estado | Significa |
|---|---|
| 🟡 **Em andamento** | Ainda há portão reprovado ou fase incompleta |
| 🟠 **Preparado** | Arquivo e configurações prontos; render/exportação final **não** verificados (ex.: aluno pediu só setup) |
| 🟢 **Verificado nas vistas X, Y** | Renders das vistas listadas inspecionados a 100%; outras vistas não garantidas |
| ✅ **Validado no destino** | Aberto e testado onde vai ser usado (site, engine, vídeo encodado, mockup) |

Nunca chame de final só porque renderizou sem erro.

## Checklist por destino

**Imagem**
- Dimensões exatas, aspecto, formato e profundidade conferidos no arquivo gerado (não só nas configurações).
- Fundo/transparência conforme pedido (Film > Transparent + PNG RGBA; confirme no arquivo).
- Quadro inteiro + crops a 100%.

**Vídeo / animação**
- FPS, duração e número de quadros declarados (30 fps × 10 s = 300 quadros).
- Teste de tempo em 2–3 quadros representativos (um aberto, um close, um com vidro) antes do lote.
- Sequência de imagens numa pasta versionada; encode do vídeo depois.
- Assistir a um trecho contínuo para pegar tremulação, saltos de câmera e cintilação de textura; quadros soltos não provam movimento suave.

**3D para web, app ou jogo (glTF/GLB, FBX, USD)**
- Exportar de uma **cópia**, nunca do master de render.
- Aplicar escala/rotação; conferir eixo (+Y up no glTF; o exportador converte) e uma medida conhecida depois de importar.
- Procedurais e camadas: fazer bake (ver `06-texturas-uv.md`). glTF suporta Base Color, Metal/Rough, Normal, Emission, Occlusion, e via extensões Transmission, Clearcoat, Sheen, IOR, Specular.
- Medir triângulos, tamanho do arquivo **e** desempenho no dispositivo real; compressão Draco reduz bytes, não triângulos.
- Abrir no destino (ex.: gltf-viewer, three.js editor, a própria engine) e comparar com o render na mesma pose. O tempo real não é igual ao Cycles; registre as diferenças.

**Mockup**
- Tela/rótulo como ilha UV ou material separado, fácil de trocar.
- Testar a troca da arte em perspectiva e conferir cantos e brilho por cima.

**.blend editável**
- `File > External Data > Make Paths Relative` (ou Pack Resources, se combinado).
- Reabrir o arquivo do zero e conferir: texturas carregam, câmera ativa correta, coleções organizadas, nenhum script obrigatório ao abrir.
- Controles que outra pessoa vai usar com nomes claros.

## O que guardar

`refs/` originais, provas aprovadas por fase (`provas/`), `.blend` final e o último aprovado de cada fase, configurações de câmera/luz/render no `DIARIO.md`, renders finais versionados.

## Mensagem final ao aluno

```
Entrega: renders/relogio_hero_v012.png (3840×2160, PNG 16 bits) · blend/relogio_v012_F6.blend
Estado: 🟢 Verificado na vista hero e na lateral
Último portão: IoU 0.988 · crops de logo e coroa aprovados
Suposições: fundo da caixa (sem referência)
Não verificado: vista traseira, versão animada
Próximo passo sugerido: render da vista traseira quando houver foto
```
