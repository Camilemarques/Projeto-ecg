"""Teste com sinal sintético: verifica métricas, alinhamento e filtro.

Uso (a partir da pasta do projeto):  python -I testes/teste_sintetico.py
Não usa dados reais: serve só para checar que o código funciona (regra R4).
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from deteccao import detectar_picos_ppg
from filtros import passa_banda
from metricas import (casar_batimentos, estimar_atraso, rmssd_ms,
                      sensibilidade_pp)
from sintetico import gerar_ppg_sintetico

TOL = 0.150  # s, a declarar no protocolo


def avaliar(t_r, x, fs):
    t_det = detectar_picos_ppg(x, fs)
    atraso = estimar_atraso(t_r, t_det, TOL)
    t_al = t_det - atraso
    vp, fn, fp = casar_batimentos(t_r, t_al, TOL)
    se, pp = sensibilidade_pp(vp, fn, fp)
    erro = abs(rmssd_ms(t_al) - rmssd_ms(t_r))
    return atraso, se, pp, erro


# 1) casar_batimentos e métricas com contagem conhecida
vp, fn, fp = casar_batimentos([1, 2, 3, 4], [1.05, 2.5, 3.02, 9.0], 0.15)
assert (vp, fn, fp) == (2, 2, 2), (vp, fn, fp)
se, pp = sensibilidade_pp(vp, fn, fp)
assert abs(se - 0.5) < 1e-12 and abs(pp - 0.5) < 1e-12

# 2) RMSSD com resultado conhecido: IBIs 1,0 / 1,1 / 1,0 s -> diffs 100, -100
assert abs(rmssd_ms([0, 1.0, 2.1, 3.1]) - 100.0) < 1e-9

# 3) pipeline em PPG sintético, atraso verdadeiro 0,25 s
print("semente | braço       | atraso (s) |   Se  |   +P  | erro RMSSD (ms)")
for semente in range(3):
    t_r, ppg, fs = gerar_ppg_sintetico(atraso=0.25, semente=semente)
    for nome, x in [("sem filtro", ppg),
                    ("passa-banda", passa_banda(ppg, fs))]:
        a, se, pp, e = avaliar(t_r, x, fs)
        print(f"{semente:7d} | {nome:11s} | {a:10.2f} | {se:5.2f} | "
              f"{pp:5.2f} | {e:8.1f}")
print("Testes de contagem e de RMSSD: OK")
