"""Testa o alinhamento em sinais SINTÉTICOS com atraso conhecido.

Uso:  python -I testes/teste_alinhamento.py
Passar aqui NÃO prova que o alinhamento funciona nos dados reais.
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from alinhamento import atraso_do_segmento, atraso_sem_janela, atrasos_por_segmento, platao_central, segmento_de
from sintetico import gerar_ecg_sintetico, gerar_ppg_sintetico

# platô: centro da faixa contínua; ignora um segundo platô distante
lags = np.arange(-1, 1.001, 0.1)
ses = np.where((lags > 0.05) & (lags < 0.45), 1.0, 0.2)
ses[-1] = 1.0
c, a, b = platao_central(lags, ses)
assert abs(c - 0.25) < 0.06 and a < b < 0.5, (c, a, b)

# atraso muda no meio do registro: 0,25 s depois 1,70 s (maior que o intervalo entre batimentos)
for rr_dp in (0.15,):
    t_r, e, _ = gerar_ecg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=rr_dp)
    _, p1, _ = gerar_ppg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=rr_dp, atraso=0.25)
    _, p2, _ = gerar_ppg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=rr_dp, atraso=1.70)
    from deteccao import detectar_picos_r, detectar_picos_ppg
    ecg = np.r_[e, e]; ppg = np.r_[p1, p2]
    tr = detectar_picos_r(ecg, 700.0)
    tp = detectar_picos_ppg(ppg, 64.0)
    tab = atrasos_por_segmento(tr, tp, 1200.0)
    print("segmento | atraso | Se max | Se acaso")
    for s in tab:
        print(f"{s['ini']:4.0f}-{s['fim']:4.0f} | {s['atraso']:6.2f} | {s['se_max']:.2f} | {s['se_acaso']:.2f}")
    assert all(abs(s["atraso"] - 0.25) < 0.05 for s in tab[:2]), tab
    assert all(abs(s["atraso"] - 1.70) < 0.05 for s in tab[2:]), tab
    assert all(s["se_max"] >= 0.98 for s in tab)
    assert abs(atraso_do_segmento(tab, 100.0) - tab[0]["atraso"]) < 1e-9
    assert abs(atraso_do_segmento(tab, 1100.0) - tab[-1]["atraso"]) < 1e-9
# atraso SEM a janela: recupera o atraso e ignora os batimentos da janela
seg = segmento_de(tab, 700.0)                                   # segmento 600-900 s, atraso 1,70 s
lag_sem = atraso_sem_janela(tr, tp, seg, (720.0, 780.0))
assert abs(lag_sem - 1.70) < 0.05, lag_sem
ref_antes = tr[(tr >= seg["ini"]) & (tr < seg["fim"])]
assert np.isnan(atraso_sem_janela(tr, tp, seg, (720.0, 780.0), min_ref=len(ref_antes)))   # sobram poucos
assert abs(atraso_do_segmento(tab, 700.0) - 1.70) < 0.05
print("Testes do alinhamento: OK")
