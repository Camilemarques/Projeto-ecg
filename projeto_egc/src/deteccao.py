"""Detecção de batimentos."""

import numpy as np
from scipy import signal


def detectar_picos_ppg(x, fs, dist_min=0.4, prominencia_rel=0.3):
    """
    Nome: detectar_picos_ppg
    Objetivo: achar os picos sistólicos do PPG já filtrado.
    Entradas: x (vetor); fs (Hz); dist_min (s): intervalo mínimo entre
              picos; prominencia_rel (float): fração do desvio padrão de x.
    Saídas: t_pico (vetor, s): instantes dos picos, a partir de t = 0.
    Pré-condições: x filtrado (sem tendência lenta).
    Pós-condições: t_pico crescente.
    Autoras: <nomes>
    NOTA: o MESMO detector, com os MESMOS parâmetros, deve ser usado nos
          três braços (sem filtro, passa-banda, wavelet).
    """
    x = np.asarray(x, dtype=float)
    picos, _ = signal.find_peaks(x, distance=int(dist_min * fs),
                                 prominence=prominencia_rel * np.std(x))
    return picos / fs


def detectar_picos_r(ecg, fs, refrataria=0.2, janela_integ=0.15):
    """
    Nome: detectar_picos_r
    Objetivo: achar os picos R do ECG (referência da avaliação), com um
              detector no estilo de Pan-Tompkins (ref. [7] do roteiro).
    Entradas: ecg (vetor, mV); fs (Hz); refrataria (s): intervalo mínimo
              entre batimentos; janela_integ (s): janela da integração.
    Saídas: t_r (vetor, s): instantes dos picos R, a partir de t = 0.
    Pré-condições: ECG convertido para mV; fs pelo menos 200 Hz.
    Pós-condições: t_r estritamente crescente, com separação >= refrataria;
                   a polaridade (R para cima ou para baixo) é escolhida uma
                   vez para o registro inteiro, para o instante do pico ser
                   sempre o mesmo ponto do QRS (importante para o RMSSD).
    Autoras: <nomes>
    Etapas: 1) passa-banda 5-15 Hz com fase zero; 2) derivada; 3) quadrado;
            4) integração em janela móvel; 5) picos candidatos, aceitos por
            limiar adaptativo (sinal x ruído) com busca retroativa quando
            passa muito tempo sem batimento; 6) refino do instante no sinal
            filtrado.
    DIFERENÇAS em relação ao artigo original: usa filtro de fase zero (o
            original é causal), derivada por gradiente e janela centrada.
            Conferir com o que for visto nas aulas do item 6.
    """
    x = np.asarray(ecg, dtype=float).ravel()
    if len(x) < int(5 * fs):
        return np.array([])
    sos = signal.butter(2, [5.0, 15.0], btype="bandpass", fs=fs, output="sos")
    xf = signal.sosfiltfilt(sos, x)                       # 1) passa-banda
    d = np.gradient(xf) * fs                              # 2) derivada
    n_int = max(1, int(round(janela_integ * fs)))
    mwi = np.convolve(d ** 2, np.ones(n_int) / n_int, mode="same")  # 3 e 4)

    cand, _ = signal.find_peaks(mwi, distance=int(refrataria * fs))
    if len(cand) == 0:
        return np.array([])
    alt = mwi[cand]

    ref = int(refrataria * fs)
    spki = 0.5 * float(np.max(alt[:10]))                  # nível do sinal
    npki = 0.0                                            # nível do ruído
    limiar = npki + 0.25 * (spki - npki)
    aceitos, rejeitados = [], []                          # 5) limiar adaptativo
    for p, h in zip(cand, alt):
        if len(aceitos) >= 3:                             # busca retroativa
            rr_med = float(np.mean(np.diff(aceitos[-8:])))
            if p - aceitos[-1] > 1.66 * rr_med and rejeitados:
                lista = [(hh, pp) for pp, hh in rejeitados
                         if pp > aceitos[-1] + ref and hh > 0.5 * limiar]
                if lista:
                    hh, pp = max(lista)
                    aceitos.append(pp)
                    spki = 0.25 * hh + 0.75 * spki
                    rejeitados = []
        if h > limiar:
            aceitos.append(p)
            spki = 0.125 * h + 0.875 * spki
            rejeitados = []
        else:
            npki = 0.125 * h + 0.875 * npki
            rejeitados.append((p, h))
        limiar = npki + 0.25 * (spki - npki)

    aceitos = np.array(sorted(aceitos))
    if len(aceitos) == 0:
        return np.array([])
    # poda: dois picos a menos de metade do RR mediano => fica o mais forte
    if len(aceitos) >= 5:
        rr_mediano = float(np.median(np.diff(aceitos)))
        lista = list(aceitos)
        mudou = True
        while mudou and len(lista) > 1:
            mudou = False
            for i in range(len(lista) - 1):
                if lista[i + 1] - lista[i] < 0.5 * rr_mediano:
                    if mwi[lista[i]] >= mwi[lista[i + 1]]:
                        del lista[i + 1]
                    else:
                        del lista[i]
                    mudou = True
                    break
        aceitos = np.array(lista)
    w = int(0.1 * fs)                                   # 6) refino
    segs = [(max(0, p - w), min(len(xf), p + w + 1)) for p in aceitos]
    maximos = np.array([xf[a:b].max() for a, b in segs])
    minimos = np.array([xf[a:b].min() for a, b in segs])
    pol = 1.0 if np.median(maximos) >= np.median(-minimos) else -1.0
    picos = np.array([a + int(np.argmax(pol * xf[a:b])) for a, b in segs])
    # 7) refino final no ECG ORIGINAL (o filtro 5-15 Hz desloca o topo do R)
    w2 = int(0.04 * fs)
    picos = np.array([max(0, p - w2) + int(np.argmax(pol * x[max(0, p - w2):p + w2 + 1]))
                      for p in picos])
    picos = np.unique(picos)
    manter = [picos[0]]
    for p in picos[1:]:
        if p - manter[-1] >= ref:
            manter.append(p)
    return np.array(manter) / fs
