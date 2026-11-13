# Passo 19: tabelas e figuras finais (lê os CSV de resultados/final)
from rodada_final import TODOS
from analise import gerar_tudo

PASTA_RES = RAIZ_REPO + '/resultados/final'
t = gerar_tudo(PASTA_RES, esperados=TODOS)
