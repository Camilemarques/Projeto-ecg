# Conferência visual: 1ª janela de estresse (60 s), em 3 painéis de 20 s
import numpy as np
import matplotlib.pyplot as plt
from deteccao import detectar_picos_r
from janelas import janelas_da_condicao

ecg, FS = r['ecg'], r['fs_ecg']
t_r = detectar_picos_r(ecg, FS)
a, b = janelas_da_condicao(r['rotulo'], ROTULOS['estresse'], FS_ROTULO)[0]
rr = np.diff(t_r[(t_r >= a) & (t_r < b)])
print(f'1ª janela de estresse: {len(rr) + 1} batimentos | RR mín {rr.min():.3f} s | '
      f'mediana {np.median(rr):.3f} s | máx {rr.max():.3f} s | RR < 0,4 s: {(rr < 0.4).sum()}')

fig, ax = plt.subplots(3, 1, figsize=(13, 8))
for k in range(3):
    t0 = a + 20 * k
    i0, i1 = int(t0 * FS), int((t0 + 20) * FS)
    ax[k].plot(np.arange(i0, i1) / FS, ecg[i0:i1], lw=0.6)
    m = (t_r >= t0) & (t_r < t0 + 20)
    ax[k].plot(t_r[m], ecg[np.round(t_r[m] * FS).astype(int)], 'rv', ms=4)
    ax[k].set_ylabel('ECG (mV)')
ax[2].set_xlabel('tempo (s)')
plt.tight_layout()
plt.savefig('figura_estresse_janela1_S10.png', dpi=150)
plt.show()
