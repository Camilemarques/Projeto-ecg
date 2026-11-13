"""Confere a conversão do ECG: compara o ECG do .pkl com o arquivo bruto.

Uso (na pasta do projeto):
    python -I src/conferir_conversao.py S10.pkl S10_respiban.txt [n_linhas]

Etapa 1: para cada coluna do arquivo bruto do RespiBAN, testa duas hipóteses
  (a) o ECG do .pkl é a fórmula do README aplicada à coluna;
  (b) o ECG do .pkl são os valores brutos da coluna.
Etapa 2 (só se nenhuma coluna coincidir na etapa 1): inverte a fórmula nas
primeiras amostras do .pkl e procura essa sequência no arquivo bruto inteiro,
para achar um possível deslocamento.
Não assume qual coluna é o ECG nem o formato do cabeçalho: imprime o topo do
arquivo para vocês lerem. A etapa 1 lê só as primeiras n_linhas (padrão 300000).
Aviso: o .pkl é lido com pickle; use só o arquivo oficial da base.
"""

import pickle
import sys

import numpy as np
import pandas as pd

VCC = 3.0               # README, Seção II.1
CHAN_BIT = 2 ** 16      # README, Seção II.1
FS_ECG = 700.0          # README, Seção II.1


def ecg_mv(bruto):
    """ECG(mV) = (sinal / chan_bit - 0,5) * vcc  (README, Seção II.1)."""
    return (np.asarray(bruto, dtype=float) / CHAN_BIT - 0.5) * VCC


def topo_do_arquivo(caminho, max_linhas=40):
    """Devolve as primeiras linhas e quantas começam com '#' (cabeçalho)."""
    topo = []
    with open(caminho, "r", errors="replace") as f:
        for _ in range(max_linhas):
            linha = f.readline()
            if not linha:
                break
            topo.append(linha.rstrip("\r\n"))
    n_cab = 0
    for linha in topo:
        if linha.startswith("#"):
            n_cab += 1
        else:
            break
    return topo, n_cab


def procurar_deslocamento(df, ecg, tam=200):
    """
    Nome: procurar_deslocamento
    Objetivo: achar onde o início do ECG do .pkl aparece no arquivo bruto.
    Entradas: df (tabela do arquivo bruto inteiro); ecg (vetor do .pkl, mV);
              tam (nº de amostras usadas na busca).
    Saídas: nenhuma (imprime o resultado).
    Pré-condições: o .pkl deve ser a fórmula do README aplicada a valores
                   inteiros do conversor; senão a busca não faz sentido.
    Pós-condições: imprime a coluna, a linha e o erro máximo, ou o motivo de
                   não ter achado.
    Autoras: <nomes>
    """
    bruto_est = (ecg[:tam] / VCC + 0.5) * CHAN_BIT
    dist = float(np.max(np.abs(bruto_est - np.round(bruto_est))))
    print(f"\nEtapa 2: invertendo a fórmula nas {tam} primeiras amostras do "
          f".pkl, os valores brutos estimados vão de {bruto_est.min():.1f} a "
          f"{bruto_est.max():.1f}; a distância máxima ao inteiro mais próximo "
          f"é {dist:.3g}.")
    if dist > 1e-3:
        print("  Os valores NÃO são inteiros: o .pkl não é a fórmula do README "
              "aplicada a valores do conversor (pode ter sido filtrado ou "
              "convertido de outro jeito). Não concluam nada e me enviem "
              "esta saída.")
        return
    alvo = np.round(bruto_est).astype(np.int64)
    achados = []
    for j in range(df.shape[1]):
        col = df[j].to_numpy(dtype=np.int64)
        for k in np.flatnonzero(col == alvo[0]):
            if k + tam <= len(col) and np.array_equal(col[k:k + tam], alvo):
                achados.append((j, int(k)))
    if not achados:
        print("  Os valores são inteiros do conversor, mas não achei essa "
              "sequência em nenhuma coluna do arquivo bruto. Não concluam "
              "nada e me enviem esta saída.")
        return
    for j, k in achados:
        col = df[j].to_numpy(dtype=float)
        n = min(len(ecg), len(col) - k)
        err = float(np.max(np.abs(ecg_mv(col[k:k + n]) - ecg[:n])))
        print(f"  Achei: o ECG do .pkl começa na linha {k} (contando a partir "
              f"de 0) da coluna {j + 1} do arquivo bruto, {k / FS_ECG:.2f} s "
              f"depois do início do arquivo. Erro máximo da fórmula em {n} "
              f"amostras: {err:.3g} mV.")


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("Uso: python -I src/conferir_conversao.py S10.pkl "
                 "S10_respiban.txt [n_linhas]")
    pkl, txt = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) == 4 else 300000

    topo, n_cab = topo_do_arquivo(txt)
    print(f"=== Topo de {txt} ({n_cab} linhas de cabeçalho com '#')")
    for linha in topo[:n_cab + 3]:
        print("  " + linha[:400])

    df = pd.read_csv(txt, sep=r"\s+", header=None, skiprows=n_cab, nrows=n)
    print(f"\nLidas {len(df)} linhas e {df.shape[1]} colunas "
          f"(o README fala em 10 colunas).")

    with open(pkl, "rb") as f:
        d = pickle.load(f, encoding="latin1")
    ecg = np.asarray(d["signal"]["chest"]["ECG"], dtype=float).ravel()

    m = min(len(df), len(ecg))
    print(f"Comparando as primeiras {m} amostras.\n")
    print("coluna (de 1) | erro máx. se pkl = fórmula(coluna) | "
          "erro máx. se pkl = coluna")
    melhor_f, melhor_r = (None, np.inf), (None, np.inf)
    for j in range(df.shape[1]):
        col = df[j].to_numpy(dtype=float)[:m]
        e_f = float(np.max(np.abs(ecg_mv(col) - ecg[:m])))
        e_r = float(np.max(np.abs(col - ecg[:m])))
        print(f"{j + 1:13d} | {e_f:34.4g} | {e_r:24.4g}")
        if e_f < melhor_f[1]:
            melhor_f = (j, e_f)
        if e_r < melhor_r[1]:
            melhor_r = (j, e_r)

    print()
    if melhor_f[1] < 1e-3:
        print(f"Resultado: o ECG do .pkl é a fórmula do README aplicada à "
              f"coluna {melhor_f[0] + 1} do arquivo (contagem do README, a "
              f"partir de 1); erro máximo {melhor_f[1]:.3g} mV.")
    elif melhor_r[1] < 1e-9:
        print(f"Resultado: o .pkl contém os valores brutos da coluna "
              f"{melhor_r[0] + 1}: a fórmula do README AINDA precisa ser "
              f"aplicada.")
    else:
        print("Resultado da etapa 1: nenhuma coluna coincide amostra a "
              "amostra com o ECG do .pkl. Indo para a etapa 2 (procurar um "
              "deslocamento no arquivo inteiro).")
        df_total = pd.read_csv(txt, sep=r"\s+", header=None, skiprows=n_cab)
        procurar_deslocamento(df_total, ecg)


if __name__ == "__main__":
    main()
