# Roteiro de estudo (as duas devem saber explicar cada item)

Ordem sugerida: leitura -> janelas -> R -> PPG/filtros -> métricas -> alinhamento
-> pipeline -> análise. Abra o arquivo, rode o teste correspondente, responda.

| Módulo | O que faz | Perguntas para responder sem consultar |
|---|---|---|
| leitura.py | lê ECG, BVP, ACC, rótulos do .pkl | Qual a fs de cada sinal? Em que unidade está o ECG? Por que o .pkl começa depois do arquivo bruto? Que rótulos usamos? |
| janelas.py | janelas de 60 s por condição | Como são formadas? O que acontece com o resto que não completa 60 s? Por que 19/12 no S10? |
| deteccao.py (R) | Pan-Tompkins próprio | Para que servem passa-banda, derivada, quadrado e integração? Como funciona o limiar adaptativo e a busca retroativa? Por que refinar no ECG bruto? |
| deteccao.py (PPG) | find_peaks com distância e proeminência | Por que os mesmos parâmetros nos 3 braços? O que a proeminência controla? |
| filtros.py | passa-banda e wavelet | Por que 0,5-4 Hz? O que é sosfiltfilt e fase zero? O que a wavelet db4 nível 6 decompõe (faixas de cada nível)? Por que a wavelet ficou parecida com o passa-banda? |
| metricas.py | casamento, Se, +P, RMSSD | Como um batimento vira VP, FN ou FP? Por que 150 ms? O que é RMSSD? |
| alinhamento.py | atraso por segmento | Por que há atraso? Por que não usar o mesmo atraso na gravação toda? O que é o nível de acaso e por que ele é alto? |
| pipeline.py | fluxo por participante | Quais colunas saem e o que cada uma significa? O que é `se_loo`? |
| rodada_final.py / analise.py | 15 participantes, tabelas | Por que a unidade de análise é o participante? Por que o p é descritivo? O que é bootstrap? |

Perguntas de defesa (seminário):
1. Se a Se é 0,79, 79% dos batimentos foram achados? (Resposta: com tolerância de 150 ms; a 50 ms é 0,30.)
2. O filtro melhora? (1 a 2 pontos; passa-banda um pouco acima; wavelet ~ sem filtro.)
3. Por que o estresse piora? (FC maior, movimento; movimento não explica tudo.)
4. Por que o RMSSD do PPG falha? (Batimentos errados e jitter do pico.)
5. O que limita a conclusão? (S10/S11 no desenvolvimento, atraso estimado com o ECG, acelerômetro sem unidade confirmada, só 15 participantes, conversão checada só no S10.)
