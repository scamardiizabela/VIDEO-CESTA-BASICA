# Boa Mesa Cesta Básica — filme institucional V3

[Assistir ao vídeo pronto no Google Drive](https://drive.google.com/file/d/18QwNgR2ej_bgo_xlJ_dfbfmgD5I9tv_x/view)

47 segundos, vertical 1080 × 1920, 30 fps, H.264 CRF 15, AAC estéreo 320 kb/s e 48 kHz.

## Conteúdo e direção
As cinco artes originais apresentam Propostas 01, 02, 03 e 04 e Kit Limpeza com seus valores, pesos e quantidades. A galeria usa movimentos contínuos e preserva integralmente as artes. Na sequência, imagens reais da operação apresentam soluções para empresas, registro PAT FO002424, atendimento humanizado e rápido, preparação com cuidado e entrega rápida com condições combinadas no atendimento.

Direção editorial com marfim, vinho e dourado; tipografia EB Garamond e Inter; revelações por palavra alinhadas à narração e transições de planos adjacentes. Sem relógios, numeração de etapas ou barras de progresso. Os números próprios das propostas e do registro PAT permanecem.

Narração ElevenLabs Multilingual v2 em português, voz Bella. Alinhamento real por palavra em `alignment_v3.json` e `timing_v3.json`. Trilha com extensão musical por crossfades e redução durante a fala; passagens, cliques suaves, notificação e ambiência dos originais em níveis discretos.

## Reproduzir
Requer Python 3.10+, Pillow, NumPy e FFmpeg no PATH.

```sh
python -m pip install -r requirements.txt
python render_v3.py
```

O código extrai automaticamente `assets_v3.zip` para `assets/` e gera a extensão da música quando necessário. O arquivo contém as cinco artes, a logo oficial do site, narração, fontes e efeitos usados na V3. A trilha `assets/music.mp3` está versionada desde a primeira edição.

Baixe os três vídeos originais da [pasta Vídeo Boa Mesa](https://drive.google.com/drive/folders/1SFCXwYSUXl2inb1hvk1Rmu3VEO4aEeo2) para `assets/`:

| Original | Nome local | SHA-256 |
| --- | --- | --- |
| PRODUÇÃO.mp4 | producao.mp4 | 44a572f05a76d665b74e0af6a7327f2248682af00716d2b1336d2005cbae9a92 |
| estoque.mp4 | estoque.mp4 | f44e32ba7164f3e6b04eb15cf7a2f38be43c3e19690535de6169d64246767b66 |
| Carregamento.mp4 | carregamento.mp4 | bbd7ef0768ca33931f5a620fc4c64f0e6ce934a885997b8d8cd205808ac035e4 |

Os originais são 720 × 1280; a exportação Full HD usa ampliação proporcional Lanczos. Nenhuma cena operacional foi gerada e nenhum produto, embalagem ou procedimento foi modificado. O projeto e os materiais de edição estão neste repositório; o MP4 final está no Drive como **vídeo pronto bm.mp4**.

## Validação
Decodificação completa sem erros, duração e formato conferidos, áudio sem saturação e revisão visual dos enquadramentos, textos e artes. Metadados e hashes em `validation_v3.json`. `NARRACAO_V3.txt` guarda a copy final. V1 e V2 permanecem no histórico e nos arquivos anteriores.

Referência de serviços e registro: https://boamesacestabasica.com.br/ . O registro PAT é apresentado como condição de fornecedor, sem promessas automáticas de benefícios fiscais. Prazos de entrega dependem das condições combinadas no atendimento.
