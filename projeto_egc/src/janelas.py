"""Seleção de trechos e janelas a partir dos rótulos do WESAD."""

import numpy as np


def janelas_da_condicao(rotulo, codigo, fs, dur_s=60.0):
    """
    Nome: janelas_da_condicao
    Objetivo: dividir cada bloco contínuo de uma condição em janelas
              consecutivas, sem sobreposição, de dur_s segundos.
    Entradas: rotulo (vetor de códigos, amostrado a fs); codigo (int, ex.:
              1 = baseline, 2 = estresse); fs (Hz, taxa do vetor de rótulos);
              dur_s (float, s).
    Saídas: lista de (t_ini, t_fim) em segundos desde o início do registro.
    Pré-condições: rotulo e os sinais usam o mesmo eixo de tempo (README do
                   WESAD: rótulos a 700 Hz, mesmo início do RespiBAN).
    Pós-condições: janelas não se sobrepõem; a sobra de cada bloco menor que
                   dur_s é descartada; lista vazia se o código não existir.
    Autoras: <nomes>
    NOTA: "janelas consecutivas, sem sobreposição, sobra descartada" é uma
          regra a registrar no protocolo, antes de calcular resultados.
    """
    rotulo = np.asarray(rotulo).ravel()
    idx = np.flatnonzero(rotulo == codigo)
    if idx.size == 0:
        return []
    quebras = np.flatnonzero(np.diff(idx) > 1)          # fim de cada bloco
    ini = idx[np.r_[0, quebras + 1]]
    fim = idx[np.r_[quebras, idx.size - 1]] + 1
    n_jan = int(round(dur_s * fs))
    saida = []
    for a, b in zip(ini, fim):
        for i in range(int((b - a) // n_jan)):
            saida.append(((a + i * n_jan) / fs, (a + (i + 1) * n_jan) / fs))
    return saida


def fatiar(x, fs, t_ini, t_fim):
    """
    Nome: fatiar
    Objetivo: recortar de um sinal o trecho entre t_ini e t_fim (s).
    Entradas: x (vetor); fs (Hz, taxa de x); t_ini, t_fim (s).
    Saídas: trecho (vetor).
    Pré-condições: 0 <= t_ini < t_fim <= duração de x.
    Pós-condições: len(trecho) = round((t_fim - t_ini) * fs).
    Autoras: <nomes>
    """
    return np.asarray(x)[int(round(t_ini * fs)):int(round(t_fim * fs))]
