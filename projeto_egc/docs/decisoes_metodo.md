# Registro de decisões de método e limitações

Serve de base para a seção de métodos e de limitações do relatório.
Decisões tomadas DEPOIS da entrega do protocolo (06/11/2026) estão marcadas.

## Dados e leitura
- Conversão do ECG verificada no S10 contra o arquivo bruto (offset de 61000
  amostras, erro 1,1e-16 mV). Os outros 14 participantes NÃO foram verificados.
- O `.pkl` já traz o ECG em mV; a fórmula não deve ser aplicada de novo.
- Trechos: janelas de 60 s consecutivas e sem sobreposição dentro de cada
  bloco contínuo de baseline (1) ou estresse (2); a sobra do bloco é descartada.
  S10: 19 e 12 janelas.
- Figuras: trecho de 10 s começando 60 s depois do início da condição (regra
  fixada antes de ver o sinal).

## Referência (ECG)
- Detector de picos R próprio, estilo Pan-Tompkins (passa-banda 5-15 Hz de fase
  zero, derivada, quadrado, integração de 150 ms, limiar adaptativo com busca
  retroativa, polaridade única por registro). Diferenças em relação ao artigo
  original estão no cabeçalho da função.
- 07/11/2026: o instante do pico passou a ser refinado no ECG original (e não
  no sinal filtrado), porque o marcador ficava abaixo do topo do R.
- Conferência: só visual, em trechos do S10 (baseline e a 1ª janela de estresse).
- Em ECG sintético com rajadas de ruído mais fortes que o QRS, Se caiu a 0,97
  e o erro de RMSSD naquela janela chegou a cerca de 90 ms: janelas de ECG ruim
  distorcem o RMSSD de referência.

## PPG
- Detector de picos do PPG: `find_peaks` com distância mínima de 0,4 s e
  proeminência de 0,3 do desvio padrão do trecho. Mesmos parâmetros nos três
  braços. Não foram ajustados nos dados do WESAD.
- Braços: sem filtro; passa-banda Butterworth 0,5-4 Hz (ordem 4, fase zero);
  wavelet.
- Wavelet (07/11/2026, escolhida SÓ em sinal sintético): db4, nível 6, limiar
  universal suave aplicado só aos detalhes acima de 4 Hz (D1 a D3); aproximação
  zerada; detalhes da banda cardíaca (D4 a D6) mantidos. A 1ª versão limiarizava
  todos os detalhes, falhou o critério fixado antes (Se e +P >= 0,97 em ruído
  0,2) e apagava o pulso com ruído maior. Foram comparadas 8 variantes. Com
  esta escolha a wavelet se comporta como um passa-banda 0,5-4 Hz em bandas
  diádicas.

## Alinhamento (decidido em 07/11/2026, depois do protocolo)
- Os dispositivos foram sincronizados à mão. No S10 o melhor atraso foi de
  0,8 a 1,9 s, bem acima do atraso fisiológico do pulso (algumas centenas de ms),
  e variou ao longo do registro (hipótese: deriva de relógio; NÃO confirmada).
- Como os batimentos são quase periódicos, o atraso só é identificado a menos
  de um intervalo entre batimentos. Por isso: atraso estimado por segmentos de
  300 s, busca de +-4 s, passo de 0,02 s, centro do platô de Se; a janela de
  60 s usa o atraso do segmento que contém o seu centro. O mesmo atraso vale para
  os três braços (estimado com o passa-banda).
- A 1ª tentativa (por janela de 60 s, busca de +-0,5 s) deu atrasos de 0,28 e
  0,48 s, que eram picos locais. Os números dessa tentativa (Se 0,57 a 0,69) são
  INVÁLIDOS e não devem ser usados.

## Métricas
- Casamento um a um com tolerância de 150 ms (protocolo). Picos do PPG fora da
  janela, depois do alinhamento, são descartados antes de contar falsos positivos.
- Nível de acaso: mediana da Se ao longo de atrasos entre -4 e +4 s. Com
  tolerância de 150 ms e frequência cardíaca alta (129 bpm, intervalo de 0,47 s)
  a tolerância cobre cerca de 65% do intervalo entre batimentos; Se de 0,4 a
  0,5 já ocorre ao acaso. Reportar Se junto do nível de acaso.

## Limitações conhecidas
- O atraso de cada segmento é escolhido para maximizar a Se nos mesmos dados:
  os valores de Se são otimistas.
- O S10 foi usado no desenvolvimento (detector, alinhamento, wavelet); os
  resultados dele são preliminares. Reportar os 15 participantes com e sem o S10.
- Janelas vizinhas não são independentes.
- A unidade do BVP e o ganho do ECG não constam no README da base.
- A qualidade do BVP no S10 é ruim em várias janelas; ondas lentas e irregulares
  dentro da banda de 0,5-4 Hz não são removidas por nenhum dos filtros.

## Rodada final e análise (decidido em 08/11/2026, antes de ver os resultados dos 15)
- Os 15 participantes (S2 a S17, sem S12) rodam com o MESMO código e os mesmos
  parâmetros; um CSV por participante em `resultados/final/`. S10 e S11 são
  participantes de desenvolvimento e entram na rodada; reportar também sem eles.
- Nenhuma janela é excluída pelo código. `ecg_suspeito` marca FC do ECG fora de
  40-180 bpm; essas janelas ficam fora só do erro de RMSSD.
- Unidade de análise: o participante (média das janelas). Janelas vizinhas não são
  independentes; p de Wilcoxon e intervalos por bootstrap são descritivos.
- Movimento: tercis de `acc_std` (desvio padrão do módulo da aceleração do pulso na
  janela), calculados com todas as janelas e SEM olhar a Se. Reportar também dentro
  de cada condição (movimento e estresse andam juntos). Unidade do acelerômetro não
  confirmada: só vale a comparação relativa.
- Sensibilidade: (a) tolerância de 50 e 100 ms, com o mesmo atraso; (b) atraso
  estimado SEM os batimentos da janela avaliada (`atraso_sem_janela`).
- RMSSD (secundária): erro absoluto entre o RMSSD do PPG (intervalos entre os picos
  alinhados dentro da janela) e o do ECG; todas as janelas com ECG plausível e,
  separadamente, só as com Se >= 0,8 (esta versão seleciona pelo desfecho: é
  descritiva).
- Nível de acaso: ver Métricas.

## Resultados da rodada final
Ver `docs/resultados_finais.md`. Conclusão do RMSSD: erro de 110 a 365 ms conforme a
Se; PPG de pulso com este detector não estima RMSSD. Sem ajuste de detector após ver
os 15 participantes.
