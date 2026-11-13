"""Inspeciona um arquivo .pkl do WESAD e imprime um resumo curto.

Uso (na pasta do projeto, com o caminho do arquivo de UM participante):
    python -I src/inspecionar_wesad.py dados/brutos/WESAD/S2/S2.pkl

Não altera nada: só lê e imprime. Cole a saída completa na conversa.
Aviso: o .pkl é lido com pickle, então use apenas o arquivo baixado da
página oficial da base.
"""

import pickle
import sys
from collections import Counter

import numpy as np


def descrever(obj, prefixo="", nivel=0):
    """Imprime recursivamente chaves, tipos e formas."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{prefixo}{k!r}: {type(v).__name__}", end="")
            if isinstance(v, np.ndarray):
                print(f"  forma={v.shape}  dtype={v.dtype}")
            elif isinstance(v, dict):
                print()
                descrever(v, prefixo + "    ", nivel + 1)
            else:
                print(f"  valor={str(v)[:60]!r}")
    else:
        print(f"{prefixo}{type(obj).__name__}")


def estatisticas(nome, x):
    x = np.asarray(x, dtype=float).ravel()
    print(f"  {nome}: n={len(x)}  min={x.min():.4g}  max={x.max():.4g}  "
          f"média={x.mean():.4g}  desvio={x.std():.4g}")


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python -I src/inspecionar_wesad.py caminho/S2.pkl")
    caminho = sys.argv[1]
    with open(caminho, "rb") as f:
        d = pickle.load(f, encoding="latin1")

    print(f"=== Arquivo: {caminho}")
    print("\n--- Estrutura")
    descrever(d)

    try:
        ecg = np.asarray(d["signal"]["chest"]["ECG"]).ravel()
        bvp = np.asarray(d["signal"]["wrist"]["BVP"]).ravel()
        rot = np.asarray(d["label"]).ravel()
    except KeyError as e:
        print(f"\nChave esperada não encontrada: {e}")
        return

    print("\n--- Estatísticas (sem conversão)")
    estatisticas("ECG do peito", ecg)
    estatisticas("BVP do pulso", bvp)

    print("\n--- Durações SUPONDO fs = 700 Hz (ECG) e 64 Hz (BVP)")
    print(f"  ECG: {len(ecg) / 700:.1f} s   BVP: {len(bvp) / 64:.1f} s   "
          f"rótulo (a 700 Hz): {len(rot) / 700:.1f} s")

    print("\n--- Rótulos (valor: amostras, segundos a 700 Hz)")
    for v, n in sorted(Counter(rot.tolist()).items()):
        print(f"  {v}: {n} amostras, {n / 700:.1f} s")


if __name__ == "__main__":
    main()
