# Boa Mesa Cesta Básica — anúncio V5

[Assistir à versão atual no Google Drive](https://drive.google.com/file/d/18QwNgR2ej_bgo_xlJ_dfbfmgD5I9tv_x/view)

44 segundos • 1080×1920 • 30 fps • H.264 CRF 15 • AAC estéreo 320 kb/s, 48 kHz.

## Refinamento V5
Abertura tipográfica, sem fotografias recortadas de cestas. A cena para casa e empresa usa a filmagem real da preparação. As cinco artes aparecem apenas na passagem de propostas e kit, entre 11,583 e 15,930 segundos. A galeria rápida de quatro propostas mantém o movimento aprovado pela cliente. O kit usa a mesma linguagem de cartão original em perspectiva. Cena PAT sem fotografia de produto.

Encerramento sem itens, sem placa ou moldura: logo original transparente aplicada diretamente sobre fundo marfim de tela inteira. A logo muda de escala e posição de forma contínua até o CTA. Novas entradas por letras, com acomodação suave. Narração, trilha, cronologia e filmagens centrais da V4 preservadas.

O ponto de entrada V5 reaproveita `render_v4.py` e `mix_v4.py` com substituições de cenas. O ZIP de assets continua `assets_v4.zip`; não há novas gerações pagas.

## Direção da campanha
Conceito: **Sua compra merece mais. Mais qualidade. Mais escolha. Mais cuidado.** Nova copy comercial, voz masculina expressiva ElevenLabs v3, tipografia condensada, fotografias originais em perspectiva e transições com aceleração e movimentos diferentes. Os materiais de proposta apoiam a variedade: quatro artes passam em 2,338 segundos; o kit de limpeza entra na sequência por 2,009 segundos. Não há relógios, barras ou etapas numeradas.

A narrativa apresenta casa e empresa, variedade, kit limpeza, fornecedor registrado no PAT FO002424, atendimento humanizado no WhatsApp e operação real: preparação, estoque e carregamento. O encerramento traz cotação e chamada para WhatsApp. Condições de entrega são combinadas no atendimento, sem promessas automáticas de benefícios fiscais.

## Reproduzir
Requer Python 3.10+, Pillow, NumPy e FFmpeg no PATH.

```sh
python -m pip install -r requirements.txt
python render_v5.py
```

`assets_v4.zip` é extraído automaticamente. Contém imagens originais, logo, voz, fontes e efeitos usados na V4. `mix_v4.py` gera a montagem da trilha e o design sonoro de forma determinística. A música original `assets/music.mp3` está versionada desde a primeira edição.

Baixe os vídeos originais da [pasta Vídeo Boa Mesa](https://drive.google.com/drive/folders/1SFCXwYSUXl2inb1hvk1Rmu3VEO4aEeo2) para `assets/`:

| Original | Nome local |
| --- | --- |
| PRODUÇÃO.mp4 | producao.mp4 |
| estoque.mp4 | estoque.mp4 |
| Carregamento.mp4 | carregamento.mp4 |

Os originais 720×1280 recebem ampliação proporcional Lanczos para Full HD. Nenhuma cena operacional é gerada. Produtos e embalagens permanecem originais. Na V5, os kits aparecem nas artes completas da passagem rápida em perspectiva; não há fotografias recortadas na abertura, no PAT ou no final.

## Arquivos de revisão
- `DESIGN_V5.md` e `REVISAO_V5.md`: refinamentos e revisão da versão atual.
- `DESIGN_V4.md` e `PLAN_V4.md`: direção e execução, incluindo a instrução de não destacar propostas.
- `NARRACAO_V4.txt`: texto final.
- `alignment_v4.json` e `timing_v4.json`: alinhamento e cenas.
- `voice_review_v4.json`: transcrição de conferência da voz.
- `REVISAO_V4.md`: crítica, correções e limites observados.
- `validation_v5.json`: especificações, hashes e verificações da entrega atual.
- `ASSET_CREDITS_V4.md`: créditos e fontes dos materiais.

O MP4 final está na mesma pasta do Drive como **vídeo pronto bm.mp4**. O repositório contém o projeto e os materiais reproduzíveis. Edições anteriores permanecem preservadas.
