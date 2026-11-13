# Projeto Final EGC 21818: PPG de pulso vs ECG no WESAD

Camile de Santis Marques (RA 24006992) e Luana Varela Vacari (RA 24000499).
PUC-Campinas, Engenharia Biomédica, 2º semestre de 2026.

## Objetivo

Aplicar filtro passa-banda e filtro wavelet ao PPG de pulso (Empatica E4) da
base WESAD para detectar batimentos e estimar o RMSSD, avaliando por
sensibilidade e preditividade positiva dos batimentos (principal) e pelo erro
do RMSSD (secundária), em relação ao ECG do peito (RespiBAN). Há também um
braço sem filtro, como referência.

## Dados

- Base: WESAD (Wearable Stress and Affect Detection), Schmidt et al., ICMI 2018.
- Fonte: UCI Machine Learning Repository, https://doi.org/10.24432/C57K5T
  (também em https://www.eti.uni-siegen.de/ubicomp/home/datasets/icmi18/).
- Data de acesso: ___/11/2026  (preencher; baixado em 05/11/2026 segundo o Drive).
- Licença: uso científico e não comercial, com crédito aos autores. Por isso os
  dados brutos NÃO estão neste repositório.

Como obter: baixar o arquivo (cerca de 2,1 GB compactado) pela página da base
e extrair, de modo que exista `WESAD/S2/S2.pkl`. Nunca editar os dados brutos.

## Metadados confirmados (wesad_readme.pdf e participante S10)

- 15 participantes (S2 a S17, sem S1 e S12, descartados pelos autores por
  defeito de sensor).
- ECG do peito (RespiBAN): 700 Hz, conversor de 16 bits, em mV por
  ECG(mV) = (sinal / 2^16 - 0,5) * 3. No `.pkl` o ECG já está em mV (faixa
  de -1,46 a +1,48 no S10). Conversão VERIFICADA no S10: o ECG do `.pkl` é
  essa fórmula aplicada ao canal CH1 do arquivo bruto, erro máximo de
  1,1e-16 mV em 3.847.200 amostras; o `.pkl` começa na linha 61000 do bruto
  (87,14 s). Só o S10 foi verificado.
- BVP/PPG do pulso (Empatica E4, pulso não dominante): 64 Hz. O README não
  informa a unidade do BVP nem filtros. A unidade do acelerômetro do pulso
  (1/64 g) é uma inferência, não está confirmada.
- Rótulos a 700 Hz: 0 indefinido, 1 baseline, 2 estresse, 3 amusement,
  4 meditação, 5/6/7 ignorar.
- Os dois dispositivos foram sincronizados MANUALMENTE (toque duplo no peito).
  No S10, o atraso entre PPG e ECG ficou entre 0,8 e 1,9 s, muito acima do
  atraso fisiológico do pulso (ver `docs/decisoes_metodo.md`).

## Estrutura

```
src/
  leitura.py       ler ECG do peito, BVP do pulso, aceleração e rótulos
  janelas.py       janelas de 60 s a partir dos rótulos (S10: 19 baseline, 12 estresse)
  filtros.py       passa-banda 0,5-4 Hz e wavelet (db4, nível 6, limiar universal suave)
  deteccao.py      picos do PPG e picos R do ECG (estilo Pan-Tompkins)
  alinhamento.py   atraso PPG x ECG por segmentos de 300 s (busca de +-4 s)
  pipeline.py      processar_sujeito: todo o fluxo de um participante, por janela
  rodada_final.py  roda os 15 participantes, um de cada vez, com checkpoint por CSV
  analise.py       tabelas e figuras finais a partir dos CSV por participante
  metricas.py      casamento de batimentos, Se, +P, RMSSD
  sintetico.py     ECG e PPG sintéticos para testar o código
  conferir_conversao.py  compara o ECG do .pkl com o arquivo bruto do RespiBAN
  inspecionar_wesad.py   resumo da estrutura de um .pkl
notebooks/         projeto_egc_final.ipynb (reprodução) e as células dos passos 7 a 20
testes/            testes em sinal sintético ou arquivos fictícios
resultados/        tabelas por janela (CSV), geradas pelo código
docs/decisoes_metodo.md   registro das decisões de método e das limitações
docs/resultados_finais.md resultados e leitura da rodada final
docs/desvios_protocolo.md desvios e acréscimos em relação ao protocolo
docs/roteiro_estudo.md    roteiro de estudo por módulo e perguntas de defesa
docs/declaracao_ia.md     rascunho da Declaração de Uso de IA
```

## Como reexecutar

```
pip install -r requirements.txt     # inclui PyWavelets
python -I testes/teste_picos_r.py
python -I testes/teste_alinhamento.py
python -I testes/teste_pipeline.py
python -I testes/teste_rodada_analise.py
python -I testes/teste_janelas.py
python -I testes/teste_wavelet.py   # precisa do PyWavelets
```

Os testes usam sinal sintético ou arquivos fictícios: provam que o código
roda como esperado, NÃO que funciona nos dados reais.

## Status

- [x] Leitura, conversão e validação do ECG no S10 real
- [x] Janelas de 60 s no S10 real (19 baseline, 12 estresse)
- [x] Figura sinal bruto x filtrado do S10 (13/11)
- [x] Detector de picos R: testado em sintético e conferido visualmente em
      trechos do S10 (baseline e estresse); NÃO conferido nos outros participantes
- [x] Wavelet implementada; testada em sintético com PyWavelets no Colab
- [x] Alinhamento por segmentos de 300 s
- [x] Rodada do S10 com os 3 braços: `resultados/janelas_S10.csv`
      (S10 é participante de DESENVOLVIMENTO; resultado preliminar)
- [x] Código da rodada final e da análise (RMSSD, estratos de movimento, sensibilidade
      de tolerância e de atraso, tabelas e figuras), testado só em sinal sintético
- [x] Rodada dos 15 participantes (08/11/2026): 445 janelas, 0 falhas
- [x] Tabelas finais (`notebooks/celula_passo19_analise.py`); conferir as figuras
- [ ] Conferir visualmente o ECG e o PPG de alguns participantes além do S10 e do S11
- [ ] Consultar o datasheet do sensor de ECG (ganho e filtros analógicos)
- [ ] Anotar a data de acesso à base
- [ ] Declaração de Uso de IA; relatório (4 páginas); seminário

## Resultado preliminar do S10 (desenvolvimento, 1 participante)

Média das janelas de 60 s, tolerância de 150 ms; Se do acaso é a mediana da
Se em atrasos errados (nível de referência, não uma correção):

| Condição | Braço | Se | +P | Se do acaso |
|---|---|---|---|---|
| baseline | sem filtro | 0,80 | 0,88 | 0,45 |
| baseline | passa-banda | 0,80 | 0,89 | 0,44 |
| baseline | wavelet | 0,80 | 0,87 | 0,45 |
| estresse | sem filtro | 0,76 | 0,87 | 0,47 |
| estresse | passa-banda | 0,77 | 0,89 | 0,46 |
| estresse | wavelet | 0,76 | 0,87 | 0,46 |

Os três braços ficaram praticamente iguais. Um participante não permite
concluir nada geral.

## Transparência

O código deste repositório foi gerado com apoio de uma ferramenta de IA
generativa (Claude) e deve constar na Declaração de Uso de Inteligência
Artificial do relatório. O código só entra nos resultados depois de ser lido,
executado e compreendido pela dupla.
