# Boa Mesa Cesta Básica — anúncio V4

[Assistir à versão atual no Google Drive](https://drive.google.com/file/d/18QwNgR2ej_bgo_xlJ_dfbfmgD5I9tv_x/view)

44 segundos • 1080×1920 • 30 fps • H.264 CRF 15 • AAC estéreo 320 kb/s, 48 kHz.

## Direção
Conceito: **Sua compra merece mais. Mais qualidade. Mais escolha. Mais cuidado.** Nova copy comercial, voz masculina expressiva ElevenLabs v3, tipografia condensada, fotografias originais em perspectiva e transições com aceleração e movimentos diferentes. Os materiais de proposta apoiam a variedade: quatro artes passam em 2,338 segundos; o kit de limpeza entra na sequência por 2,009 segundos. Não há relógios, barras ou etapas numeradas.

A narrativa apresenta casa e empresa, variedade, kit limpeza, fornecedor registrado no PAT FO002424, atendimento humanizado no WhatsApp e operação real: preparação, estoque e carregamento. O encerramento traz cotação e chamada para WhatsApp. Condições de entrega são combinadas no atendimento, sem promessas automáticas de benefícios fiscais.

## Reproduzir
Requer Python 3.10+, Pillow, NumPy e FFmpeg no PATH.

```sh
python -m pip install -r requirements.txt
python render_v4.py
python mix_v4.py
```

`assets_v4.zip` é extraído automaticamente. Contém imagens originais, logo, voz, fontes e efeitos usados na V4. `mix_v4.py` gera a montagem da trilha e o design sonoro de forma determinística. A música original `assets/music.mp3` está versionada desde a primeira edição.

Baixe os vídeos originais da [pasta Vídeo Boa Mesa](https://drive.google.com/drive/folders/1SFCXwYSUXl2inb1hvk1Rmu3VEO4aEeo2) para `assets/`:

| Original | Nome local |
| --- | --- |
| PRODUÇÃO.mp4 | producao.mp4 |
| estoque.mp4 | estoque.mp4 |
| Carregamento.mp4 | carregamento.mp4 |

Os originais 720×1280 recebem ampliação proporcional Lanczos para Full HD. Nenhuma cena operacional é gerada. Produtos e embalagens permanecem originais. Fotos dos kits são enquadradas por máscaras e apresentadas como planos em perspectiva; as artes completas também passam na galeria.

## Arquivos de revisão
- `DESIGN_V4.md` e `PLAN_V4.md`: direção e execução, incluindo a instrução de não destacar propostas.
- `NARRACAO_V4.txt`: texto final.
- `alignment_v4.json` e `timing_v4.json`: alinhamento e cenas.
- `voice_review_v4.json`: transcrição de conferência da voz.
- `REVISAO_V4.md`: crítica, correções e limites observados.
- `validation_v4.json`: especificações, hashes e verificações da entrega.
- `ASSET_CREDITS_V4.md`: créditos e fontes dos materiais.

O MP4 final está na mesma pasta do Drive como **vídeo pronto bm.mp4**. O repositório contém o projeto e os materiais reproduzíveis. Edições anteriores permanecem preservadas.
