# Passo 18: rodar os 15 participantes (um de cada vez, com checkpoint no Drive)
from rodada_final import rodar_participantes, TODOS

PASTA_RES = RAIZ_REPO + '/resultados/final'
estado = rodar_participantes(TODOS, ZIP_WESAD, PASTA_DADOS, PASTA_RES)
