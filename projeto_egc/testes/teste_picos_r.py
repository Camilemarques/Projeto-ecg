"""Testa detectar_picos_r em ECG SINTÉTICO (batimentos conhecidos).

Uso:  python -I testes/teste_picos_r.py
Só verifica que o código funciona (regra R4): o ECG real é mais difícil que
o sintético, e passar aqui NÃO prova que o detector funciona nos dados reais.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from deteccao import detectar_picos_r
from metricas import casar_batimentos, rmssd_ms, sensibilidade_pp
from sintetico import gerar_ecg_sintetico

TOL = 0.050   # s


def avaliar(t_r, ecg, fs):
    t_det = detectar_picos_r(ecg, fs)
    vp, fn, fp = casar_batimentos(t_r, t_det, TOL)
    se, pp = sensibilidade_pp(vp, fn, fp)
    dist = [np.min(np.abs(t_det - r)) for r in t_r]
    erro_t = float(np.mean([d for d in dist if d <= TOL]))
    return se, pp, erro_t, abs(rmssd_ms(t_det) - rmssd_ms(t_r)), len(t_det)


print("caso                    |  Se   |  +P   | erro tempo (ms) | erro RMSSD (ms)")
for semente in range(3):
    for nome, pol in [("normal", 1), ("invertido", -1)]:
        t_r, ecg, fs = gerar_ecg_sintetico(semente=semente, polaridade=pol)
        se, pp, et, er, _ = avaliar(t_r, ecg, fs)
        print(f"semente {semente} {nome:10s}   | {se:.3f} | {pp:.3f} | "
              f"{et * 1000:15.1f} | {er:15.1f}")
        assert se >= 0.99 and pp >= 0.99, (semente, nome, se, pp)
        assert et < 0.015, et                      # menos de 15 ms
        assert er < 5.0, er                        # RMSSD a menos de 5 ms

# ECG com rajadas de ruído (artefatos): não pode inventar nem perder muitos
t_r, ecg, fs = gerar_ecg_sintetico(semente=5, duracao=120.0)
rng = np.random.default_rng(9)
for ini in (20.0, 55.0, 90.0):                     # 3 rajadas de 1,5 s
    a, b = int(ini * fs), int((ini + 1.5) * fs)
    ecg[a:b] += 1.0 * rng.standard_normal(b - a)
se, pp, et, er, n = avaliar(t_r, ecg, fs)
print(f"com 3 rajadas de ruído   | {se:.3f} | {pp:.3f} | {et * 1000:15.1f} | "
      f"{er:15.1f}  ({n} detectados, {len(t_r)} reais)")
assert se >= 0.95 and pp >= 0.95, (se, pp)

# trecho curto demais: devolve vazio, sem erro
assert len(detectar_picos_r(np.zeros(100), 700.0)) == 0
print("Testes do detector de picos R: OK")
