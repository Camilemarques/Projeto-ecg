# Passo 10: o atraso PPG x ECG muda ao longo do registro? (segmentos de 300 s)
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from deteccao import detectar_picos_r, detectar_picos_ppg
from filtros import passa_banda
from metricas import casar_batimentos, sensibilidade_pp

TOL, SEG, LIM = 0.150, 300.0, 4.0     # tolerância (s), duração do segmento (s), busca de atraso ±LIM (s)
ecg, bvp, rot = r['ecg'], r['bvp'], r['rotulo']
FS_E, FS_B = r['fs_ecg'], r['fs_bvp']
t_r = detectar_picos_r(ecg, FS_E)
t_p = detectar_picos_ppg(passa_banda(bvp, FS_B, 0.5, 4.0), FS_B)
dur = len(ecg) / FS_E
lags = np.arange(-LIM, LIM + 1e-9, 0.02)

def condicao_em(t):
    c = int(rot[min(int(t * FS_ROTULO), len(rot) - 1)])
    return {1: 'baseline', 2: 'estresse'}.get(c, 'outra')

print('segmento (s)      | condição no centro | melhor atraso (s) | Se melhor | Se mediana | margem p/ 2º pico')
res = []
for ini in np.arange(0.0, dur - SEG + 1e-9, SEG):
    fim = ini + SEG
    ref = t_r[(t_r >= ini) & (t_r < fim)]
    det = t_p[(t_p >= ini - LIM - 1) & (t_p < fim + LIM + 1)]
    ses = np.array([sensibilidade_pp(*casar_batimentos(ref, det - L, TOL))[0] for L in lags])
    j = int(np.argmax(ses))
    bom = ses >= ses[j] - 0.01          # faixa CONTÍNUA em volta do máximo (platô)
    i0 = i1 = j
    while i0 > 0 and bom[i0 - 1]:
        i0 -= 1
    while i1 < len(bom) - 1 and bom[i1 + 1]:
        i1 += 1
    centro = 0.5 * (lags[i0] + lags[i1])
    pk, _ = find_peaks(ses)
    alt = np.sort(ses[pk])[::-1]
    margem = alt[0] - alt[1] if len(alt) > 1 else np.nan
    cond = condicao_em(ini + SEG / 2)
    res.append((ini + SEG / 2, centro, ses[j], cond))
    print(f'{ini:6.0f} a {fim:6.0f} | {cond:18s} | {centro:17.2f} | {ses[j]:9.2f} | '
          f'{np.median(ses):10.2f} | {margem:8.2f}')

res = np.array([(a, b, c) for a, b, c, _ in res])
fig, ax = plt.subplots(figsize=(12, 4))
for cod, cor in ((1, 'tab:green'), (2, 'tab:orange')):
    idx = np.flatnonzero(rot == cod)
    if idx.size:
        quebras = np.flatnonzero(np.diff(idx) > 1)
        ini_b = idx[np.r_[0, quebras + 1]] / FS_ROTULO
        fim_b = (idx[np.r_[quebras, idx.size - 1]] + 1) / FS_ROTULO
        for a, b in zip(ini_b, fim_b):
            ax.axvspan(a, b, color=cor, alpha=0.15)
sc = ax.scatter(res[:, 0], res[:, 1], c=res[:, 2], cmap='viridis', vmin=0.3, vmax=1.0, s=50)
plt.colorbar(sc, label='Se no melhor atraso')
ax.set_xlabel('tempo no registro (s)  [verde = baseline, laranja = estresse]')
ax.set_ylabel('melhor atraso (s)')
ax.set_ylim(-LIM, LIM)
plt.tight_layout()
plt.savefig(f'figura_deriva_atraso_{SUJEITO}.png', dpi=150)
plt.show()
