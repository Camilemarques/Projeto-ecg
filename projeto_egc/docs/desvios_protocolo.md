# Desvios e acréscimos em relação ao protocolo entregue (06/11/2026)

Conferir cada item com o PDF entregue (que não deve ser alterado) e escrever no
relatório o que difere.

1. Alinhamento PPG x ECG: atraso estimado por segmento de 300 s (busca de +-4 s,
   centro do platô da curva de Se). Definido DEPOIS da entrega, porque os
   dispositivos foram sincronizados manualmente e o atraso medido (0,8 a 1,9 s)
   não é fisiológico. Usa o ECG de referência; por isso há a análise com o atraso
   estimado sem a janela avaliada.
2. Wavelet: db4, nível 6, aproximação A6 zerada, limiar universal suave só em
   D1-D3 (> 4 Hz). Escolhida entre 8 variantes em sinal SINTÉTICO. Fica próxima
   do passa-banda por construção.
3. Nível de acaso (mediana da Se em atrasos errados) e ganho sobre o acaso:
   acrescentados para interpretar a Se com tolerância de 150 ms.
4. Sensibilidade à tolerância (50 e 100 ms) e ao atraso: acrescentada.
5. Estratificação por movimento (acc_std) e correlação de Spearman: acrescentadas,
   exploratórias. Unidade do acelerômetro não confirmada.
6. S10 e S11 usados no desenvolvimento e mantidos na análise final; resultados
   também sem eles.
7. Conversão do ECG verificada contra o arquivo bruto só no S10.
8. Detector de picos R próprio (estilo Pan-Tompkins, fase zero), conferido
   visualmente só no S10 (e trechos do S11).
9. Nenhuma janela excluída. `ecg_suspeito` (FC fora de 40-180 bpm) só filtra o
   erro de RMSSD; foi 0 em todas as janelas.
10. Janelas: 445 no total (29 a 31 por participante).
