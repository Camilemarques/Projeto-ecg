import sys
RAIZ_REPO = '/content/projeto_egc'
PASTA_DADOS = '/content/dados/WESAD'
SUJEITO = 'S10'
sys.path.insert(0, RAIZ_REPO + '/src')

import numpy as np
import matplotlib.pyplot as plt
from leitura import ler_sujeito, ROTULOS
from filtros import passa_banda

r = ler_sujeito(PASTA_DADOS, SUJEITO)
ecg, bvp, rot, acc = r['ecg'], r['bvp'], r['rotulo'], r['acc_pulso']
FS_E, FS_B, FS_A = r['fs_ecg'], r['fs_bvp'], r['fs_acc']

# Regra fixa, definida ANTES de ver o sinal (evita escolher um trecho bonito):
# trecho de 10 s, começando 60 s depois do início de cada condição.
REGRA = 'trecho de 10 s, 60 s após o início da condição'
COND = [('baseline', ROTULOS['baseline']), ('estresse', ROTULOS['estresse'])]

fig, ax = plt.subplots(3, 2, figsize=(12, 8), sharex='col')
for col, (nome, cod) in enumerate(COND):
    t0 = np.flatnonzero(rot == cod)[0] / FS_E + 60
    # O filtro roda num trecho maior (10 s antes e 10 s depois) para que o
    # efeito de borda do filtro fique fora da parte desenhada.
    seg = bvp[int((t0 - 10) * FS_B):int((t0 + 20) * FS_B)]
    filt = passa_banda(seg, FS_B, 0.5, 4.0)
    i0, i1 = int(10 * FS_B), int(20 * FS_B)
    tb = t0 + np.arange(i1 - i0) / FS_B
    e = ecg[int(t0 * FS_E):int(t0 * FS_E) + int(10 * FS_E)]
    te = t0 + np.arange(len(e)) / FS_E
    ax[0, col].plot(te, e, lw=0.8)
    ax[1, col].plot(tb, seg[i0:i1], color='tab:red', alpha=0.35, lw=0.8,
                    label='bruto')
    ax[1, col].plot(tb, filt[i0:i1], color='tab:red', lw=1.1,
                    label='passa-banda 0,5-4 Hz')
    if acc is not None:
        a = acc[int(t0 * FS_A):int((t0 + 10) * FS_A)]
        ta = t0 + np.arange(len(a)) / FS_A
        ax[2, col].plot(ta, np.linalg.norm(a, axis=1), color='tab:gray', lw=0.9)
    ax[0, col].set_title(nome)
    ax[2, col].set_xlabel('tempo desde o início do registro (s)')
ax[0, 0].set_ylabel('ECG do peito (mV)')
ax[1, 0].set_ylabel('BVP do pulso (u.a.)')
ax[2, 0].set_ylabel('|aceleração| do pulso (u.a.)')
ax[1, 0].legend(loc='upper right', fontsize=8)
fig.suptitle(f'{SUJEITO}: {REGRA}')
plt.tight_layout()
plt.savefig(f'figura_bruto_filtrado_{SUJEITO}.png', dpi=150)
plt.show()

# Verificação de saturação do ECG no registro inteiro
print(f'ECG: {100 * np.mean(np.abs(ecg) >= 1.4):.4f}% das amostras com |valor| >= 1,4 mV')
