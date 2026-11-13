"""Roda a célula do passo 11 com dados sintéticos (atraso 0,25 s e depois 1,70 s)."""
import subprocess, sys, tempfile
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
def montar(tmp):
    return f'''
import sys, numpy as np
sys.path.insert(0, {str(RAIZ / "src")!r})
from sintetico import gerar_ecg_sintetico, gerar_ppg_sintetico
from leitura import ROTULOS, FS_ROTULO
_, e, _ = gerar_ecg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=0.15)
_, p1, _ = gerar_ppg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=0.15, atraso=0.25)
_, p2, _ = gerar_ppg_sintetico(duracao=600, semente=1, rr_medio=0.85, rr_dp=0.15, atraso=1.70)
ecg = np.r_[e, e]; bvp = np.r_[p1, p2]
rot = np.zeros(len(ecg), dtype=np.int32); rot[int(30*700):int(570*700)] = 1; rot[int(630*700):int(1170*700)] = 2
r = {{'ecg': ecg, 'bvp': bvp, 'rotulo': rot, 'fs_ecg': 700.0, 'fs_bvp': 64.0}}
SUJEITO = 'SX'; USAR_WAVELET = False; RAIZ_REPO = {tmp!r}
exec(open({str(RAIZ / "notebooks" / "celula_passo11_janelas.py")!r}).read())
assert (df[df.braco == 'passa-banda'].se > 0.95).all(), df
assert (df.se_acaso < 0.7).all()
assert (df[df.braco == 'passa-banda'].pp > 0.95).all(), df
print("Célula do passo 11: OK")
'''
with tempfile.TemporaryDirectory() as tmp:
    r = subprocess.run([sys.executable, "-I", "-c", montar(tmp)], capture_output=True, text=True)
    print(r.stdout[-2500:]); print(r.stderr[-1500:])
    assert r.returncode == 0
    assert (Path(tmp) / "resultados" / "janelas_SX.csv").exists()
