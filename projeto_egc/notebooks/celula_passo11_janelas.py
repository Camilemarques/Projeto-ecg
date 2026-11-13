# Passo 11: Se e +P por janela de 60 s, com atraso por segmento de 300 s e controle de acaso
import os
import numpy as np
import pandas as pd
from deteccao import detectar_picos_r, detectar_picos_ppg
from filtros import passa_banda, wavelet_denoise
from janelas import janelas_da_condicao
from metricas import casar_batimentos, sensibilidade_pp
from alinhamento import atrasos_por_segmento, atraso_do_segmento, curva_se_atraso

USAR_WAVELET = globals().get('USAR_WAVELET', True)   # False só nos testes sem PyWavelets
TOL, MARG = 0.150, 6.0          # tolerância (s); folga em volta da janela para filtro e atraso (s)
ecg, bvp, rot = r['ecg'], r['bvp'], r['rotulo']
FS_E, FS_B = r['fs_ecg'], r['fs_bvp']
t_r = detectar_picos_r(ecg, FS_E)
t_p = detectar_picos_ppg(passa_banda(bvp, FS_B, 0.5, 4.0), FS_B)       # só para estimar o atraso
tab = atrasos_por_segmento(t_r, t_p, len(ecg) / FS_E)
lags_acaso = np.arange(-4.0, 4.0 + 1e-9, 0.02)

linhas = []
for nome in ('baseline', 'estresse'):
    for k, (a, b) in enumerate(janelas_da_condicao(rot, ROTULOS[nome], FS_ROTULO)):
        lag = atraso_do_segmento(tab, 0.5 * (a + b))
        ref = t_r[(t_r >= a) & (t_r < b)] - a
        i0 = int(round((a - MARG) * FS_B))
        seg = bvp[i0:int(round((b + MARG) * FS_B))]
        braco = {'sem filtro': seg, 'passa-banda': passa_banda(seg, FS_B, 0.5, 4.0)}
        if USAR_WAVELET:
            braco['wavelet'] = wavelet_denoise(seg, FS_B)
        for nome_b, x in braco.items():
            t_det = detectar_picos_ppg(x, FS_B) - MARG          # tempo relativo ao início da janela
            t_al = t_det - lag                                   # alinhado ao ECG
            t_al = t_al[(t_al >= 0) & (t_al < b - a)]            # só picos DENTRO da janela
            vp, fn, fp = casar_batimentos(ref, t_al, TOL)
            se, pp = sensibilidade_pp(vp, fn, fp)
            acaso = float(np.median(curva_se_atraso(ref, t_det, TOL, lags_acaso)))
            linhas.append(dict(sujeito=SUJEITO, condicao=nome, janela=k + 1, t_ini=a,
                               braco=nome_b, atraso=lag, n_ecg=len(ref), vp=vp, fn=fn,
                               fp=fp, se=se, pp=pp, se_acaso=acaso))
df = pd.DataFrame(linhas)

pasta = RAIZ_REPO + '/resultados'
os.makedirs(pasta, exist_ok=True)
df.to_csv(f'{pasta}/janelas_{SUJEITO}.csv', index=False)

print('Atraso por segmento de 300 s (s):', [round(s['atraso'], 2) for s in tab])
res = (df.groupby(['condicao', 'braco'])[['se', 'pp', 'se_acaso']].agg(['mean', 'min', 'max']).round(2))
print('\nResumo por condição e braço (média, mín, máx entre janelas):')
print(res.to_string())
print('\nSe - Se_acaso (média):')
print((df.assign(ganho=df.se - df.se_acaso).groupby(['condicao', 'braco']).ganho.mean().round(2)).to_string())
print('\nPor janela (passa-banda):')
print(df[df.braco == 'passa-banda'][['condicao', 'janela', 't_ini', 'atraso', 'n_ecg',
                                      'vp', 'fn', 'fp', 'se', 'pp', 'se_acaso']].round(2).to_string(index=False))
