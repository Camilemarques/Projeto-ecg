# Resultados da rodada final (08/11/2026)

15 participantes (S2 a S17, sem S12), 445 janelas de 60 s, nenhuma excluída,
nenhuma com ECG suspeito. Média das janelas por participante, depois entre
participantes. Tolerância de 150 ms. S10 e S11 foram participantes de
desenvolvimento (a tabela "sem S10 e S11" mostra que não puxaram o resultado).

| Condição | Braço | Se | +P | Se do acaso | Ganho s/ acaso |
|---|---|---|---|---|---|
| baseline | sem filtro | 0,769 | 0,775 | 0,333 | 0,435 |
| baseline | passa-banda | 0,792 | 0,800 | 0,329 | 0,463 |
| baseline | wavelet | 0,772 | 0,774 | 0,335 | 0,437 |
| estresse | sem filtro | 0,601 | 0,714 | 0,408 | 0,193 |
| estresse | passa-banda | 0,611 | 0,733 | 0,404 | 0,208 |
| estresse | wavelet | 0,609 | 0,712 | 0,415 | 0,193 |

Sem S10 e S11 (Se, baseline / estresse): sem filtro 0,761 / 0,604;
passa-banda 0,784 / 0,613; wavelet 0,764 / 0,610.

## Leitura
1. Estresse reduz a Se (0,79 para 0,61 no passa-banda) e o ganho sobre o acaso
   (0,46 para 0,21). O acaso sobe no estresse porque a FC é maior.
2. Filtros: diferenças de 1 a 2 pontos percentuais. Passa-banda > sem filtro
   (Se +0,023 baseline, +0,010 estresse; IC95% acima de 0). Wavelet ~ sem filtro
   (+P e ganho sobre o acaso sem diferença). Wavelet < passa-banda no baseline.
   Wavelet foi desenhada para se parecer com o passa-banda (ver decisões).
   p de Wilcoxon é descritivo.
3. Movimento (tercis de acc_std, limites 1,25 e 2,76): Se cai com o movimento
   (0,80 / 0,76 / 0,62 no passa-banda). Dentro do estresse, baixo movimento ainda
   dá 0,685 contra 0,861 no baseline de baixo movimento: o movimento explica
   parte da queda, não toda. Janelas agrupadas e vizinhas: descritivo.
   Spearman Se x acc_std negativo em todos os participantes (de -0,05 a -0,90).
   bvp_std também negativo na maioria (provável artefato de movimento inflando o
   desvio padrão; não é "sinal mais forte").
4. Sensibilidade: tolerância 50 / 100 / 150 ms dá Se 0,30 / 0,61 / 0,79 no
   baseline (passa-banda). O resultado principal vale para 150 ms. Atraso
   estimado sem a janela: Se cai só 0,02 a 0,03.
5. RMSSD (secundária): ECG plausível (mediana 45 ms baseline, 36 estresse).
   PPG com mediana 262 / 350 ms. Erro mediano 150 a 300 ms; cai com a Se
   (365, 283, 237, 182, 110 ms nas faixas de Se), mas fica em 110 ms mesmo com
   Se > 0,9. Com este detector e esta tolerância o RMSSD do PPG não é
   utilizável. Resultado negativo, a ser reportado como tal.
6. Não há ajuste de detector após ver os 15. Ideias (ex.: refinar o instante do
   pico pela subida sistólica) ficam como trabalho futuro ou, se testadas, como
   análise exploratória rotulada.
