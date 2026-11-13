"""Testa o script conferir_conversao.py com arquivos FICTÍCIOS.

Uso:  python -I testes/teste_conferir_conversao.py
O formato do arquivo bruto aqui (cabeçalho com '#', colunas separadas por
tab, 10 colunas) imita o topo do S10_respiban.txt real; os valores são
sorteados.
Casos: (a) .pkl = fórmula da coluna; (b) .pkl = valores brutos;
       (c) .pkl = fórmula da coluna, mas começando 1000 linhas depois.
"""

import pickle
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "src" / "conferir_conversao.py"
N = 5000
COL_ECG = 2   # posição (a partir de 0) do ECG no arquivo fictício (CH1)


def montar(pasta, pkl_bruto=False, desl=0):
    rng = np.random.default_rng(0)
    cols = rng.integers(0, 65536, size=(N, 10))
    cols[:, 0] = np.arange(N)                 # contador de linhas
    cols[:, 1] = 0                            # DI
    bruto = cols[desl:, COL_ECG]
    ecg = bruto.astype(float) if pkl_bruto else (bruto / 65536 - 0.5) * 3.0
    d = {"signal": {"chest": {"ECG": ecg[:, None]},
                    "wrist": {"BVP": rng.standard_normal((400, 1))}},
         "label": np.ones(len(ecg), dtype=np.int32), "subject": "SX"}
    with open(pasta / "SX.pkl", "wb") as f:
        pickle.dump(d, f)
    with open(pasta / "SX_respiban.txt", "w") as f:
        f.write("# OpenSignals Text File Format\n")
        f.write('# {"dispositivo": {"column": ["nSeq", "DI", "CH1"]}}\n')
        f.write("# EndOfHeader\n")
        for linha in cols:
            f.write("\t".join(str(v) for v in linha) + "\t\n")   # tab no fim


def rodar(pasta):
    r = subprocess.run([sys.executable, "-I", str(SCRIPT),
                        str(pasta / "SX.pkl"), str(pasta / "SX_respiban.txt"),
                        "3000"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


with tempfile.TemporaryDirectory() as tmp:
    a = Path(tmp) / "a"; a.mkdir(); montar(a)
    saida = rodar(a)
    assert f"coluna {COL_ECG + 1} do arquivo" in saida, saida
    assert "3 linhas de cabeçalho" in saida, saida
    assert "Etapa 2" not in saida, saida

    b = Path(tmp) / "b"; b.mkdir(); montar(b, pkl_bruto=True)
    saida = rodar(b)
    assert f"valores brutos da coluna {COL_ECG + 1}" in saida, saida

    c = Path(tmp) / "c"; c.mkdir(); montar(c, desl=1000)
    saida = rodar(c)
    assert "Etapa 2" in saida, saida
    assert (f"começa na linha 1000 (contando a partir de 0) da coluna "
            f"{COL_ECG + 1}") in saida, saida
    assert "1.43 s depois" in saida, saida          # 1000 / 700 = 1,43 s
print("Testes da conferência da conversão: OK (casos a, b e c)")
