# Passo 9: o atraso entre PPG e ECG é identificável? Curva Se x atraso
import numpy as np
import matplotlib.pyplot as plt
from deteccao import detectar_picos_r, detectar_picos_ppg
from filtros import passa_banda
from janelas import janelas_da_condicao
from metricas import casar_batimentos, sensibilidade_pp

TOL = 0.150
ecg, bvp, rot = r['ecg'], r['bvp'], r['rotulo']
FS_E, FS_B = r['fs_ecg'], r['fs_bvp']
t_r = detectar_picos_r(ecg, FS_E)
t_p = detectar_picos_ppg(passa_banda(bvp, FS_B, 0.5, 4.0), FS_B)   # registro inteiro
print(f'{len(t_r)} picos R | {len(t_p)} picos de PPG (passa-banda, registro inteiro)')

def blocos(cod):
    idx = np.flatnonzero(rot == cod)
    return idx[0] / FS_ROTULO, (idx[-1] + 1) / FS_ROTULO

trechos = {}
for nome in ('baseline', 'estresse'):
    a, b = janelas_da_condicao(rot, ROTULOS[nome], FS_ROTULO)[0]
    trechos[f'1ª janela de {nome} (60 s)'] = (a, b)
    trechos[f'{nome} inteiro'] = blocos(ROTULOS[nome])

lags = np.arange(-3.0, 3.0001, 0.02)
fig, ax = plt.subplots(len(trechos), 1, figsize=(12, 10), sharex=True)
print('\ntrecho                          | platô de atraso (s) | centro | Se no platô | Se mediana (acaso) | nº de ECG')
for k, (nome, (a, b)) in enumerate(trechos.items()):
    ref = t_r[(t_r >= a) & (t_r < b)]
    det = t_p[(t_p >= a - 4) & (t_p < b + 4)]
    ses = []
    for lag in lags:
        vp, fn, fp = casar_batimentos(ref, det - lag, TOL)
        ses.append(sensibilidade_pp(vp, fn, fp)[0])
    ses = np.array(ses)
    j = int(np.argmax(ses))
    bom = ses >= ses[j] - 0.01                  # atrasos praticamente tão bons quanto o melhor
    i0 = i1 = j                                 # só a faixa CONTÍNUA em volta do máximo
    while i0 > 0 and bom[i0 - 1]:
        i0 -= 1
    while i1 < len(bom) - 1 and bom[i1 + 1]:
        i1 += 1
    plato = lags[i0:i1 + 1]
    centro = 0.5 * (plato.min() + plato.max())
    print(f'{nome:31s} | {plato.min():6.2f} a {plato.max():5.2f}     | {centro:6.2f} | '
          f'{ses[j]:11.2f} | {np.median(ses):18.2f} | {len(ref):9d}')
    ax[k].plot(lags, ses, lw=1)
    ax[k].axvline(centro, color='r', ls=':')
    ax[k].set_ylabel('Se'); ax[k].set_title(nome, fontsize=9)
    ax[k].set_ylim(0, 1)
ax[-1].set_xlabel('atraso aplicado ao PPG (s)')
plt.tight_layout()
plt.savefig(f'figura_curva_atraso_{SUJEITO}.png', dpi=150)
plt.show()
