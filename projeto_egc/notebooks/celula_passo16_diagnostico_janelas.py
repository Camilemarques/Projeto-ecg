# Passo 16: olhar o BVP e os picos em janelas escolhidas (diagnóstico, não ajuste)
import numpy as np
import matplotlib.pyplot as plt
from leitura import ler_sujeito
from deteccao import detectar_picos_r, detectar_picos_ppg
from filtros import passa_banda

s = globals().get('s', 'S11')
alvos = globals().get('alvos', [('estresse', 6), ('estresse', 1), ('estresse', 11)])   # (condição, nº da janela)
rr = ler_sujeito(PASTA_DADOS, s)
FS_B = rr['fs_bvp']
t_r = detectar_picos_r(rr['ecg'], rr['fs_ecg'])
tabela = df11[df11.braco == 'passa-banda'].set_index(['condicao', 'janela'])
MARG = 6.0

fig, ax = plt.subplots(len(alvos), 1, figsize=(13, 3.2 * len(alvos)))
ax = np.atleast_1d(ax)
for k, (cond, jan) in enumerate(alvos):
    lin = tabela.loc[(cond, jan)]
    a, lag = float(lin.t_ini), float(lin.atraso)
    i0 = max(0, int(round((a - MARG) * FS_B)))
    seg = rr['bvp'][i0:int(round((a + 60 + MARG) * FS_B))]
    desloc = a - i0 / FS_B
    x = passa_banda(seg, FS_B, 0.5, 4.0)
    t_al = detectar_picos_ppg(x, FS_B) - desloc - lag            # picos alinhados ao ECG
    tt = np.arange(len(x)) / FS_B - desloc - lag                 # eixo do BVP alinhado ao ECG
    ax[k].plot(tt, x, color='tab:red', lw=0.9)
    m = (t_al >= 0) & (t_al < 20)
    ax[k].plot(t_al[m], x[np.round((t_al[m] + lag + desloc) * FS_B).astype(int)], 'k^', ms=5)
    ref = t_r[(t_r >= a) & (t_r < a + 20)] - a
    for t in ref:
        ax[k].axvline(t, color='tab:blue', alpha=0.35, lw=0.8)
    ax[k].set_xlim(0, 20)
    ax[k].set_title(f'{s} {cond}, janela {jan} (1ª parte, 20 s) | ECG: {len(ref)} batimentos, '
                    f'PPG: {int(m.sum())} picos | Se da janela = {lin.se:.2f}, atraso = {lag:.2f} s',
                    fontsize=9)
    ax[k].set_ylabel('BVP (u.a.)')
ax[-1].set_xlabel('tempo na janela (s)  [linhas azuis = batimentos do ECG; triângulos = picos do PPG]')
plt.tight_layout()
plt.savefig(f'figura_diagnostico_{s}.png', dpi=150)
plt.show()
