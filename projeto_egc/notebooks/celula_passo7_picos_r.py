import sys
RAIZ_REPO = '/content/projeto_egc'
PASTA_DADOS = '/content/dados/WESAD'
SUJEITO = 'S10'
sys.path.insert(0, RAIZ_REPO + '/src')

import numpy as np
import matplotlib.pyplot as plt
from leitura import ler_sujeito, ROTULOS
from janelas import janelas_da_condicao
from deteccao import detectar_picos_r

r = ler_sujeito(PASTA_DADOS, SUJEITO)
ecg, rot, FS_E = r['ecg'], r['rotulo'], r['fs_ecg']

# 1) Detector rodando no ECG inteiro (pode levar alguns segundos).
t_r = detectar_picos_r(ecg, FS_E)
rr = np.diff(t_r)
print(f'{SUJEITO}: {len(t_r)} picos R em {len(ecg) / FS_E:.0f} s')
print(f'RR: mínimo {rr.min():.3f} s | mediana {np.median(rr):.3f} s | '
      f'máximo {rr.max():.3f} s')
print(f'RR < 0,3 s: {np.sum(rr < 0.3)} | RR > 2,0 s: {np.sum(rr > 2.0)}')

# 2) Batimentos e frequência cardíaca por janela de 60 s.
print('\ncondição  | janela |  t_ini (s) | batimentos | FC (bpm) | RR máx (s)')
resumo = {}
for nome in ('baseline', 'estresse'):
    fcs = []
    for k, (a, b) in enumerate(janelas_da_condicao(rot, ROTULOS[nome],
                                                   700.0)):
        m = (t_r >= a) & (t_r < b)
        n = int(m.sum())
        rrj = np.diff(t_r[m])
        fc = 60.0 * n / (b - a)
        fcs.append(fc)
        print(f'{nome:9s} | {k + 1:6d} | {a:10.1f} | {n:10d} | {fc:8.1f} | '
              f'{(rrj.max() if len(rrj) else float("nan")):10.2f}')
    resumo[nome] = fcs
for nome, fcs in resumo.items():
    print(f'FC média {nome}: {np.mean(fcs):.1f} bpm '
          f'(mín {np.min(fcs):.1f}, máx {np.max(fcs):.1f})')

# 3) Mesmos trechos da figura anterior, agora com os picos marcados.
fig, ax = plt.subplots(2, 1, figsize=(12, 6))
for i, nome in enumerate(('baseline', 'estresse')):
    t0 = np.flatnonzero(rot == ROTULOS[nome])[0] / FS_E + 60
    e = ecg[int(t0 * FS_E):int((t0 + 10) * FS_E)]
    te = t0 + np.arange(len(e)) / FS_E
    ax[i].plot(te, e, lw=0.8)
    m = (t_r >= t0) & (t_r < t0 + 10)
    ax[i].plot(t_r[m], ecg[np.round(t_r[m] * FS_E).astype(int)], 'rv',
               label='pico R detectado')
    ax[i].set_title(f'{SUJEITO} - {nome}: 10 s a partir de 60 s após o início '
                    f'da condição')
    ax[i].set_ylabel('ECG (mV)')
    ax[i].legend(loc='upper right')
ax[1].set_xlabel('tempo (s)')
plt.tight_layout()
plt.savefig(f'figura_picos_r_{SUJEITO}.png', dpi=150)
plt.show()
