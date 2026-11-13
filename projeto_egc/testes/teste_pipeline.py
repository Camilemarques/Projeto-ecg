"""Testa processar_sujeito com um .pkl FICTÍCIO (ECG, PPG e aceleração sintéticos,
atraso 0,25 s e depois 1,70 s; a 1ª janela começa em t = 0, para testar a borda).

Uso:  python -I testes/teste_pipeline.py
Sem PyWavelets, só testa os braços sem filtro e passa-banda.
"""
import pickle, sys, tempfile, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from pipeline import processar_sujeito
from sintetico import gerar_ecg_sintetico, gerar_ppg_sintetico

try:
    import pywt  # noqa: F401
    com_wavelet = True
except ImportError:
    com_wavelet = False

_, e, _ = gerar_ecg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=0.15)
_, p1, _ = gerar_ppg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=0.15, atraso=0.25)
_, p2, _ = gerar_ppg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=0.15, atraso=1.70)
ecg = np.r_[e, e]; bvp = np.r_[p1, p2]
rot = np.zeros(len(ecg), dtype=np.int32)
rot[0:int(540 * 700)] = 1                       # baseline desde t = 0
rot[int(630 * 700):int(1170 * 700)] = 2
acc = np.random.default_rng(0).standard_normal((int(1200 * 32), 3)) * 5 + 60
with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "SX").mkdir()
    d = {"signal": {"chest": {"ECG": ecg[:, None]}, "wrist": {"BVP": bvp[:, None], "ACC": acc}},
         "label": rot, "subject": "SX"}
    pickle.dump(d, open(Path(tmp) / "SX" / "SX.pkl", "wb"))
    t0 = time.time()
    df, tab = processar_sujeito(tmp, "SX", usar_wavelet=com_wavelet)
    print(f"tempo: {time.time() - t0:.1f} s")
pb = df[df.braco == "passa-banda"]
print(pb[["condicao", "janela", "t_ini", "atraso", "n_ecg", "se", "pp", "se_acaso", "ecg_suspeito"]].round(2).to_string(index=False))
assert set(pb.condicao) == {"baseline", "estresse"} and len(pb) == 18
assert (pb.se >= 0.95).all(), pb.se.min()
assert (pb.pp >= 0.95).all(), pb.pp.min()
assert not pb.ecg_suspeito.any()
novas = ["atraso_loo", "n_ppg", "se50", "pp50", "se100", "pp100", "se_loo", "pp_loo",
         "rmssd_ecg", "rmssd_ppg", "bvp_std", "acc_std"]
assert all(c in df.columns for c in novas)
assert (pb.se_loo >= 0.95).all(), pb.se_loo.min()      # sinal limpo: o atraso sem a janela também serve
assert (pb.se50 <= pb.se100 + 1e-9).all() and (pb.se100 <= pb.se + 1e-9).all()
assert np.isfinite(pb.acc_std).all() and (pb.acc_std > 0).all()   # o .pkl fictício tem ACC
assert (np.abs(pb.rmssd_ppg - pb.rmssd_ecg) < 30).all()
assert set(df.braco) == ({"sem filtro", "passa-banda", "wavelet"} if com_wavelet else {"sem filtro", "passa-banda"})
print("Testes do pipeline: OK" + ("" if com_wavelet else " (sem a wavelet: PyWavelets ausente)"))
