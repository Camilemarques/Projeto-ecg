"""Sinal sintético, só para verificar o funcionamento do algoritmo (R4)."""

import numpy as np


def gerar_ecg_sintetico(duracao=60.0, fs=700.0, rr_medio=0.8, rr_dp=0.05,
                        ruido=0.03, deriva=0.2, semente=0, polaridade=1):
    """
    Nome: gerar_ecg_sintetico
    Objetivo: gerar um ECG sintético com picos R conhecidos.
    Entradas: duracao (s); fs (Hz); rr_medio, rr_dp (s); ruido (desvio do
              ruído branco, mV); deriva (amplitude da linha de base lenta,
              mV); semente (int); polaridade (+1 ou -1: -1 inverte o ECG).
    Saídas: t_r (instantes dos picos R, s); ecg (vetor, mV); fs.
    Pré-condições: duracao > 0.
    Pós-condições: t_r é a verdade dos batimentos; reprodutível pela semente.
    Autoras: <nomes>
    """
    rng = np.random.default_rng(semente)
    t_r, t = [], 0.5
    while t < duracao - 1.0:
        t_r.append(t)
        t += max(0.4, rng.normal(rr_medio, rr_dp))
    t_r = np.array(t_r)
    tt = np.arange(0, duracao, 1.0 / fs)
    ecg = np.zeros_like(tt)

    def onda(c, amp, larg):
        return amp * np.exp(-0.5 * ((tt - c) / larg) ** 2)

    for r in t_r:
        ecg += onda(r, 0.8, 0.010)            # R
        ecg += onda(r - 0.025, -0.15, 0.010)  # Q
        ecg += onda(r + 0.025, -0.25, 0.012)  # S
        ecg += onda(r + 0.25, 0.2, 0.040)     # T
        ecg += onda(r - 0.16, 0.1, 0.025)     # P
    ecg += deriva * np.sin(2 * np.pi * 0.2 * tt)
    ecg += ruido * rng.standard_normal(len(tt))
    return t_r, polaridade * ecg, fs


def gerar_ppg_sintetico(duracao=60.0, fs=64.0, rr_medio=0.85, rr_dp=0.05,
                        atraso=0.25, ruido=0.1, deriva=0.5, semente=0):
    """
    Nome: gerar_ppg_sintetico
    Objetivo: gerar um PPG sintético com batimentos conhecidos.
    Entradas: duracao (s); fs (Hz); rr_medio, rr_dp (s): intervalo entre
              batimentos; atraso (s): do pulso em relação ao pico R;
              ruido (desvio do ruído branco); deriva (amplitude da linha
              de base lenta); semente (int): fixa o sorteio.
    Saídas: t_r (instantes dos picos R, s); ppg (vetor); fs.
    Pré-condições: duracao > 0.
    Pós-condições: t_r é a verdade dos batimentos; reprodutível pela semente.
    Autoras: <nomes>
    """
    rng = np.random.default_rng(semente)
    t_r, t = [], 0.5
    while t < duracao - 1.0:
        t_r.append(t)
        t += max(0.4, rng.normal(rr_medio, rr_dp))
    t_r = np.array(t_r)
    tt = np.arange(0, duracao, 1.0 / fs)
    ppg = np.zeros_like(tt)
    for r in t_r:
        c = r + atraso
        ppg += np.exp(-0.5 * ((tt - c) / 0.07) ** 2)                # sistólico
        ppg += 0.35 * np.exp(-0.5 * ((tt - (c + 0.30)) / 0.10) ** 2)  # diastólico
    ppg += deriva * np.sin(2 * np.pi * 0.15 * tt)
    ppg += ruido * rng.standard_normal(len(tt))
    return t_r, ppg, fs
