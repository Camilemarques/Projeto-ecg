"""Filtros aplicados ao PPG: passa-banda (Aula 10) e wavelet (Aulas 8 e 9)."""

import numpy as np
from scipy import signal


def passa_banda(x, fs, f_baixa=0.5, f_alta=4.0, ordem=4):
    """
    Nome: passa_banda
    Objetivo: filtrar o PPG mantendo só a faixa [f_baixa, f_alta] Hz.
    Entradas: x (vetor); fs (Hz); f_baixa, f_alta (Hz); ordem (int).
    Saídas: y (vetor, mesmo tamanho de x).
    Pré-condições: 0 < f_baixa < f_alta < fs/2.
    Pós-condições: fase zero (filtragem direta e inversa), sem atraso.
    Autoras: <nomes>
    NOTA: 0,5 a 4 Hz é o valor fixo de referência de Watanabe et al. (2025),
          não um valor ótimo. Butterworth é a escolha desta versão inicial.
    """
    if not (0 < f_baixa < f_alta < fs / 2):
        raise ValueError("Faixa inválida para a fs informada.")
    sos = signal.butter(ordem, [f_baixa, f_alta], btype="bandpass",
                        fs=fs, output="sos")
    return signal.sosfiltfilt(sos, np.asarray(x, dtype=float))


def wavelet_denoise(x, fs, familia="db4", nivel=None, limiar="universal",
                    f_corte=4.0):
    """
    Nome: wavelet_denoise
    Objetivo: reduzir ruído e linha de base do PPG por decomposição wavelet.
    Entradas: x (vetor); fs (Hz); familia (str, família do PyWavelets);
              nivel (int ou None): níveis da decomposição; None = o nível em
              que a aproximação cobre só abaixo de 0,5 Hz (6 se fs = 64 Hz);
              limiar (str): só "universal" é aceito; f_corte (Hz): só os
              detalhes inteiramente ACIMA dessa frequência são limiarizados.
    Saídas: y (vetor, mesmo tamanho de x).
    Pré-condições: família, nível e limiar definidos ANTES dos resultados;
                   PyWavelets instalado (pip install PyWavelets).
    Pós-condições: mesmo tamanho de x.
    Autoras: <nomes>
    Método: 1) decompõe x em aproximação A_n (0 a fs/2^(n+1) Hz) e detalhes
            D_1..D_n (D_j cobre fs/2^(j+1) a fs/2^j Hz); 2) zera A_n (remove a
            linha de base abaixo de 0,5 Hz); 3) estima o ruído no detalhe mais
            fino D_1 (MAD/0,6745) e calcula o limiar universal
            sigma * sqrt(2 ln N); 4) aplica limiarização suave nos detalhes
            acima de f_corte (D_1..D_3 em 64 Hz: 4 a 32 Hz) e MANTÉM os
            detalhes da banda cardíaca (D_4..D_6: 0,5 a 4 Hz); 5) reconstrói.
    Histórico das escolhas (07/11/2026, só em sinal SINTÉTICO, nunca no WESAD):
            a 1ª versão limiarizava todos os detalhes e falhou o critério
            fixado antes (Se e +P >= 0,97 em ruído 0,2: deu +P = 0,91). Com
            ruído maior apagava o pulso (Se = 0,45 em ruído 0,4), porque o
            limiar universal é maior que os coeficientes do próprio pulso.
            Foram comparadas 8 variantes no total; esta (db4, nível 6,
            limiar universal suave só acima de 4 Hz) igualou o passa-banda.
            Ficam FIXAS para todos os participantes.
    NOTA: com esta escolha a wavelet se comporta, na prática, como um
          passa-banda 0,5-4 Hz em bandas diádicas; limiarizar a banda
          cardíaca piorou no sintético. Dizer isso no relatório.
    """
    try:
        import pywt
    except ImportError as e:
        raise ImportError("Instale o PyWavelets: pip install PyWavelets") from e
    if limiar != "universal":
        raise ValueError("Só o limiar 'universal' foi implementado.")
    x = np.asarray(x, dtype=float)
    if nivel is None:
        nivel = int(round(np.log2(fs / 1.0)))        # fs/2^(n+1) = 0,5 Hz
    nivel = min(nivel, pywt.dwt_max_level(len(x), pywt.Wavelet(familia).dec_len))
    coefs = pywt.wavedec(x, familia, level=nivel, mode="symmetric")
    sigma = np.median(np.abs(coefs[-1])) / 0.6745    # ruído, no detalhe mais fino
    thr = sigma * np.sqrt(2.0 * np.log(len(x)))
    n_ruido = int(np.floor(np.log2(fs / (2.0 * f_corte))))   # D_1..D_n_ruido: > f_corte
    saida = [np.zeros_like(coefs[0])]                # A_n = 0 (linha de base)
    for j in range(1, len(coefs)):                   # coefs[-1] = D_1, coefs[1] = D_nivel
        nivel_do_detalhe = len(coefs) - j
        c = coefs[j]
        saida.append(pywt.threshold(c, thr, mode="soft")
                     if nivel_do_detalhe <= n_ruido else c)
    y = pywt.waverec(saida, familia, mode="symmetric")
    return y[:len(x)]
