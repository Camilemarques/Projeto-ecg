"""Pipeline completo de um participante: ECG de referência, filtros, picos do PPG,
alinhamento e métricas por janela de 60 s."""

import numpy as np
import pandas as pd

from alinhamento import (atraso_sem_janela, atrasos_por_segmento, curva_se_atraso,
                         segmento_de)
from deteccao import detectar_picos_ppg, detectar_picos_r
from filtros import passa_banda, wavelet_denoise
from janelas import janelas_da_condicao
from leitura import FS_ROTULO, ROTULOS, ler_sujeito
from metricas import casar_batimentos, rmssd_ms, sensibilidade_pp

FC_MIN, FC_MAX = 40.0, 180.0   # bpm: fora disso o ECG da janela é marcado como suspeito


def processar_sujeito(pasta_dados, sujeito, usar_wavelet=True, tol=0.150,
                      marg=6.0, seg_s=300.0):
    """
    Nome: processar_sujeito
    Objetivo: calcular, por janela de 60 s e por braço (sem filtro,
              passa-banda, wavelet), Se, +P, nível de acaso, Se a 50 e 100 ms,
              Se com atraso estimado sem a janela, RMSSD do ECG e do PPG, e
              medidas de qualidade (desvio padrão do BVP e da aceleração).
    Entradas: pasta_dados (pasta que contém <sujeito>/<sujeito>.pkl); sujeito
              (str); usar_wavelet (bool); tol (s): tolerância principal;
              marg (s): folga em volta da janela para filtro e atraso;
              seg_s (s): segmento do atraso.
    Saídas: df (uma linha por condição, janela e braço) e tab (atrasos por
            segmento).
    Pré-condições: o .pkl existe e passa nas validações de ler_sujeito.
    Pós-condições: df tem ecg_suspeito (True se a FC do ECG na janela sai de
                   40-180 bpm); NENHUMA janela é excluída aqui.
    Autoras: <nomes>
    NOTA: os parâmetros do detector e dos filtros são os mesmos para todos os
          participantes e não são ajustados aqui. rmssd_* em ms; nan se
          houver menos de 3 batimentos.
    """
    r = ler_sujeito(pasta_dados, sujeito)
    ecg, bvp, rot = r["ecg"], r["bvp"], r["rotulo"]
    fs_e, fs_b = r["fs_ecg"], r["fs_bvp"]
    acc = None if r["acc_pulso"] is None else np.linalg.norm(r["acc_pulso"], axis=1)
    t_r = detectar_picos_r(ecg, fs_e)
    t_p = detectar_picos_ppg(passa_banda(bvp, fs_b, 0.5, 4.0), fs_b)
    tab = atrasos_por_segmento(t_r, t_p, len(ecg) / fs_e, seg_s=seg_s, tol=tol)
    lags_acaso = np.arange(-4.0, 4.0 + 1e-9, 0.02)
    dur_b = len(bvp) / fs_b

    linhas = []
    for nome in ("baseline", "estresse"):
        for k, (a, b) in enumerate(janelas_da_condicao(rot, ROTULOS[nome], FS_ROTULO)):
            if b > dur_b:
                continue
            seg_atraso = segmento_de(tab, 0.5 * (a + b))
            lag = seg_atraso["atraso"]
            lag_loo = atraso_sem_janela(t_r, t_p, seg_atraso, (a, b), tol=tol)
            ref = t_r[(t_r >= a) & (t_r < b)] - a
            i0 = max(0, int(round((a - marg) * fs_b)))
            seg = bvp[i0:int(round((b + marg) * fs_b))]
            desloc = a - i0 / fs_b                     # início da janela dentro de seg (s)
            bracos = {"sem filtro": seg, "passa-banda": passa_banda(seg, fs_b, 0.5, 4.0)}
            if usar_wavelet:
                bracos["wavelet"] = wavelet_denoise(seg, fs_b)
            fc = 60.0 * len(ref) / (b - a)
            bvp_std = float(np.std(bvp[int(round(a * fs_b)):int(round(b * fs_b))]))
            acc_std = (float("nan") if acc is None else float(np.std(
                acc[int(round(a * r["fs_acc"])):int(round(b * r["fs_acc"]))])))
            rmssd_ecg = rmssd_ms(ref)

            def alinhar(t_det, atraso):
                t_al = t_det - atraso
                return t_al[(t_al >= 0) & (t_al < b - a)]

            for nome_b, x in bracos.items():
                t_det = detectar_picos_ppg(x, fs_b) - desloc
                t_al = alinhar(t_det, lag)
                vp, fn, fp = casar_batimentos(ref, t_al, tol)
                se, pp = sensibilidade_pp(vp, fn, fp)
                se50, pp50 = sensibilidade_pp(*casar_batimentos(ref, t_al, 0.050))
                se100, pp100 = sensibilidade_pp(*casar_batimentos(ref, t_al, 0.100))
                if np.isfinite(lag_loo):
                    se_loo, pp_loo = sensibilidade_pp(
                        *casar_batimentos(ref, alinhar(t_det, lag_loo), tol))
                else:
                    se_loo = pp_loo = float("nan")
                acaso = float(np.median(curva_se_atraso(ref, t_det, tol, lags_acaso)))
                linhas.append(dict(
                    sujeito=sujeito, condicao=nome, janela=k + 1, t_ini=a, braco=nome_b,
                    atraso=lag, atraso_loo=lag_loo, n_ecg=len(ref), fc_ecg=fc,
                    ecg_suspeito=not (FC_MIN <= fc <= FC_MAX), n_ppg=len(t_al),
                    vp=vp, fn=fn, fp=fp, se=se, pp=pp, se_acaso=acaso,
                    se50=se50, pp50=pp50, se100=se100, pp100=pp100,
                    se_loo=se_loo, pp_loo=pp_loo,
                    rmssd_ecg=rmssd_ecg, rmssd_ppg=rmssd_ms(t_al),
                    bvp_std=bvp_std, acc_std=acc_std))
    return pd.DataFrame(linhas), tab
