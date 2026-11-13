# Passo 8: PPG x ECG em UMA janela de cada condição (a 1ª de cada, regra fixa)
import numpy as np
import matplotlib.pyplot as plt
from deteccao import detectar_picos_r, detectar_picos_ppg
from filtros import passa_banda
from janelas import janelas_da_condicao
from metricas import casar_batimentos, sensibilidade_pp, rmssd_ms, estimar_atraso

TOL = 0.150   # s (tolerância do protocolo)
MARGEM = 5.0  # s extras de cada lado, só para o efeito de borda do filtro
ecg, bvp, rot = r['ecg'], r['bvp'], r['rotulo']
FS_E, FS_B = r['fs_ecg'], r['fs_bvp']
t_r = detectar_picos_r(ecg, FS_E)

fig, ax = plt.subplots(2, 1, figsize=(13, 7))
for i, nome in enumerate(('baseline', 'estresse')):
    a, b = janelas_da_condicao(rot, ROTULOS[nome], FS_ROTULO)[0]
    ref = t_r[(t_r >= a) & (t_r < b)] - a          # batimentos do ECG, t = 0 no início da janela
    i_ini = max(0, int(round((a - MARGEM) * FS_B)))
    seg = bvp[i_ini:int(round((b + MARGEM) * FS_B))]
    n0 = int(round(a * FS_B)) - i_ini
    n1 = n0 + int(round((b - a) * FS_B))
    braco = {'sem filtro': seg[n0:n1],
             'passa-banda': passa_banda(seg, FS_B, 0.5, 4.0)[n0:n1]}
    print(f'\n{nome}: janela {a:.1f}-{b:.1f} s | ECG: {len(ref)} batimentos, '
          f'RMSSD {rmssd_ms(ref):.1f} ms')
    print('  braço        | PPG picos | atraso (s) | VP | FN | FP |  Se  |  +P  | RMSSD PPG (ms)')
    for nome_b, x in braco.items():
        t_det = detectar_picos_ppg(x, FS_B)
        atraso = estimar_atraso(ref, t_det, TOL)
        t_al = t_det - atraso
        vp, fn, fp = casar_batimentos(ref, t_al, TOL)
        se, pp = sensibilidade_pp(vp, fn, fp)
        print(f'  {nome_b:12s} | {len(t_det):9d} | {atraso:10.2f} | {vp:2d} | {fn:2d} | '
              f'{fp:2d} | {se:.2f} | {pp:.2f} | {rmssd_ms(t_al):13.1f}')
        if nome_b == 'passa-banda':
            tt = np.arange(len(x)) / FS_B
            ax[i].plot(tt, x, color='tab:red', lw=0.9, label='BVP passa-banda')
            ax[i].plot(t_al, x[np.round(t_det * FS_B).astype(int)], 'k^', ms=5,
                       label='picos do PPG (alinhados)')
            for k, t in enumerate(ref):
                ax[i].axvline(t, color='tab:blue', alpha=0.3, lw=0.8,
                              label='batimento do ECG' if k == 0 else None)
            ax[i].set_xlim(0, 20)
            ax[i].set_title(f'{SUJEITO} - {nome}: primeiros 20 s da 1ª janela')
            ax[i].set_ylabel('BVP (u.a.)')
            ax[i].legend(loc='upper right', fontsize=8)
ax[1].set_xlabel('tempo na janela (s)')
plt.tight_layout()
plt.savefig(f'figura_ppg_ecg_{SUJEITO}.png', dpi=150)
plt.show()
