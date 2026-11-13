"""Testa wavelet_denoise em sinal SINTÉTICO. Precisa do PyWavelets.

Uso (no Colab):  !python -I /content/drive/MyDrive/projeto_egc/testes/teste_wavelet.py
Sem PyWavelets, o teste avisa e termina sem verificar nada.
Passar aqui NÃO prova que a wavelet funciona nos dados reais.
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
try:
    import pywt  # noqa: F401
except ImportError:
    print("PyWavelets não instalado: NADA foi testado. Rode: pip install PyWavelets")
    sys.exit(0)

from deteccao import detectar_picos_ppg
from filtros import passa_banda, wavelet_denoise
from metricas import casar_batimentos, sensibilidade_pp
from sintetico import gerar_ppg_sintetico

FS = 64.0
t = np.arange(0, 120, 1 / FS)

# 1) tamanho preservado, inclusive com comprimento ímpar
for n in (len(t), len(t) - 1, 1000):
    assert len(wavelet_denoise(np.random.default_rng(0).standard_normal(n), FS)) == n

# 2) deriva lenta (0,1 Hz) removida: sobra menos de 5% da energia
lenta = 5.0 * np.sin(2 * np.pi * 0.1 * t)
y = wavelet_denoise(lenta, FS)
r_lenta = np.sum(y[200:-200] ** 2) / np.sum(lenta[200:-200] ** 2)
print(f"energia restante da deriva de 0,1 Hz: {100 * r_lenta:.1f}%")
assert r_lenta < 0.05, r_lenta

# 3) componente cardíaca (1,2 Hz) preservada: pelo menos 85% da energia
card = np.sin(2 * np.pi * 1.2 * t)
y = wavelet_denoise(card, FS)
r_card = np.sum(y[200:-200] ** 2) / np.sum(card[200:-200] ** 2)
print(f"energia preservada do sinal de 1,2 Hz: {100 * r_card:.1f}%")
assert r_card > 0.85, r_card

# 4) detecção de batimentos em PPG sintético com atraso conhecido
print("\nbraço        |  Se  |  +P")
res = {}
for nome, f in (("sem filtro", lambda x: x),
                ("passa-banda", lambda x: passa_banda(x, FS, 0.5, 4.0)),
                ("wavelet", lambda x: wavelet_denoise(x, FS))):
    ses, pps = [], []
    for semente in range(3):
        t_r, ppg, _ = gerar_ppg_sintetico(duracao=120, semente=semente, ruido=0.2)
        det = detectar_picos_ppg(f(ppg), FS)
        ref = t_r + 0.25                                  # atraso conhecido
        se, pp = sensibilidade_pp(*casar_batimentos(ref, det, 0.150))
        ses.append(se); pps.append(pp)
    res[nome] = (np.mean(ses), np.mean(pps))
    print(f"{nome:12s} | {res[nome][0]:.2f} | {res[nome][1]:.2f}")
assert res["wavelet"][0] >= 0.97 and res["wavelet"][1] >= 0.97, res
print("Testes da wavelet: OK")
