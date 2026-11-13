"""Testa janelas_da_condicao e fatiar com as contagens reais do S10.

Uso:  python -I testes/teste_janelas.py
Usa rótulos fictícios com as MESMAS durações vistas no S10 (não usa dados
reais): baseline = 826000 amostras, estresse = 507500 amostras, a 700 Hz.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from janelas import fatiar, janelas_da_condicao

FS = 700.0
rot = np.concatenate([np.zeros(65100), np.ones(826000), np.zeros(100),
                      np.full(507500, 2), np.zeros(1000)]).astype(int)

jb = janelas_da_condicao(rot, 1, FS)
je = janelas_da_condicao(rot, 2, FS)
assert len(jb) == 19, len(jb)       # 1180 s / 60 s = 19 janelas (sobra de 40 s)
assert len(je) == 12, len(je)       # 725 s / 60 s = 12 janelas (sobra de 5 s)
assert abs(jb[0][0] - 93.0) < 1e-9 and abs(jb[0][1] - 153.0) < 1e-9
assert all(abs((b - a) - 60.0) < 1e-9 for a, b in jb + je)
assert all(jb[i][1] <= jb[i + 1][0] for i in range(len(jb) - 1))   # sem sobreposição

# dois blocos separados do mesmo código: cada um conta à parte
rot2 = np.concatenate([np.ones(100 * 700), np.zeros(10 * 700),
                       np.ones(130 * 700)]).astype(int)
assert len(janelas_da_condicao(rot2, 1, FS)) == 1 + 2   # 100 s -> 1; 130 s -> 2

# código ausente
assert janelas_da_condicao(rot, 7, FS) == []

# fatiar: tamanhos coerentes nas duas taxas
t_ini, t_fim = jb[0]
assert len(fatiar(np.zeros(3847200), 700.0, t_ini, t_fim)) == 42000
assert len(fatiar(np.zeros(351744), 64.0, t_ini, t_fim)) == 3840
print("Testes das janelas: OK (baseline 19, estresse 12)")
