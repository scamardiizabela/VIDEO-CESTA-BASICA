# Boa Mesa Cesta Básica — vídeo institucional

[Assistir ao vídeo pronto no Google Drive](https://drive.google.com/file/d/18QwNgR2ej_bgo_xlJ_dfbfmgD5I9tv_x/view?usp=drivesdk)

31 segundos, versão narrada V2, vertical 1080 × 1920, 30 fps, H.264 + AAC estéreo 48 kHz.

## Versão narrada V2

Narração gerada com a conta ElevenLabs autorizada, voz Bella e modelo Multilingual v2 em português. Tempos de cada palavra derivados do alinhamento retornado pela geração. Nova tipografia Inter, revelação por máscaras, composição do WhatsApp com profundidade, transições diagonais e circulares, legendas com palavra ativa, trilha com redução automática durante a fala e cinco passagens sonoras. Encerramento dirigido a compras para casa e para equipes.

`render_v2.py` é o ponto de entrada atual. `assets_v2.zip` contém voz, fontes e efeitos novos, extraídos automaticamente pelo código quando necessário. `alignment_v2.json`, `timing_v2.json` e `NARRACAO_V2.txt` tornam os tempos e o texto editáveis. `render.py` e `export.py` preservam a primeira edição no histórico do projeto.

## Sequência
Contato por WhatsApp → cotação e confirmação → produção → estoque → carregamento → chamada comercial.

Animação de conversa com efeito de digitação, destaques em cotação e pedido, entradas suaves de texto, transições por dissolução, trilha instrumental e notificação discreta. Logo original preservada. Endereço corrigido para boamesacestabasica.com.br.

## Reproduzir e editar
Requer Python 3.10+ e FFmpeg no PATH.

```
python -m pip install -r requirements.txt
python render_v2.py
```

Antes de renderizar, baixe os três originais da [pasta Vídeo Boa Mesa](https://drive.google.com/drive/folders/1SFCXwYSUXl2inb1hvk1Rmu3VEO4aEeo2) e coloque-os em `assets/` com estes nomes locais:

| Original | Nome local | SHA-256 |
| --- | --- | --- |
| PRODUÇÃO.mp4 | producao.mp4 | 44a572f05a76d665b74e0af6a7327f2248682af00716d2b1336d2005cbae9a92 |
| estoque.mp4 | estoque.mp4 | f44e32ba7164f3e6b04eb15cf7a2f38be43c3e19690535de6169d64246767b66 |
| Carregamento.mp4 | carregamento.mp4 | bbd7ef0768ca33931f5a620fc4c64f0e6ce934a885997b8d8cd205808ac035e4 |

Os originais continuam no Drive; o repositório guarda o código e os elementos usados na edição. O MP4 final está salvo na mesma pasta do Drive, com o nome **vídeo pronto bm.mp4**.

## Materiais e decisões
- `render.py`: toda a composição, paleta, tipografia, textos, animações e enquadramentos.
- `export.py`: mixagem e exportação reproduzível.
- `assets/logo.jpg`: logo fornecida pela cliente.
- `assets/music.mp3`: trilha criada para este filme com ElevenLabs Music v2, 35s, solicitação instrumental, sem narração.
- `assets/notification.mp3`: efeito discreto fornecido com o pacote HyperFrames instalado.
- `assets/regular.ttf` e `assets/bold.ttf`: DejaVu Sans.
- `validation.json`: metadados, verificações e hashes da entrega.

As fontes originais são 720 × 1280; a exportação faz ampliação proporcional para Full HD, sem prometer detalhe adicional. O carregamento recebe desaceleração leve (1,12× de duração) para acomodar o take. Nenhuma cena operacional foi criada por IA. Não foram alterados produtos, embalagens, quantidades ou procedimentos.

## Verificação
Cinco quadros de todas as etapas revisados visualmente; textos dentro das margens; 31s completos em vídeo e áudio; decodificação integral sem erros; nenhuma sequência preta detectada com limite de 0,2s. Transições da V2 posicionadas nos tempos reais da narração; ver `timing_v2.json`.
