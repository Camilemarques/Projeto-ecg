# Checagens usadas no relatório (lê os CSV de resultados/final)
import pandas as pd, glob
df = pd.concat([pd.read_csv(f) for f in glob.glob(RAIZ_REPO + '/resultados/final/janelas_*.csv')])

# 1) sem os participantes de desenvolvimento: média por participante, depois entre participantes
sem = df[~df.sujeito.isin(['S10', 'S11'])]
pp = sem.groupby(['sujeito', 'condicao', 'braco'])[['se', 'pp', 'se_acaso']].mean()
print(pp.groupby(['condicao', 'braco']).mean().round(3), '\n')

# 2) RMSSD: valores absolutos (passa-banda) e erro por faixa de Se
r = df[df.braco == 'passa-banda'].copy()
print(r.groupby('condicao')[['rmssd_ecg', 'rmssd_ppg', 'n_ecg', 'n_ppg']].describe().T.round(1))
r['erro'] = (r.rmssd_ppg - r.rmssd_ecg).abs()
r['faixa_se'] = pd.cut(r.se, [0, .6, .7, .8, .9, 1.0])
print(r.groupby('faixa_se', observed=False)[['erro', 'rmssd_ecg', 'rmssd_ppg']].agg(['median', 'count']).round(0))
