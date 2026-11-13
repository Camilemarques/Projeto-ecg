"""Testa a fórmula de conversão do ECG e as validações de ler_sujeito.

Uso:  python -I testes/teste_conversao_leitura.py
Usa um arquivo fictício com a mesma estrutura do WESAD (não usa dados reais).
"""

import pickle
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from leitura import converter_ecg_adc_para_mv, ler_sujeito

# Fórmula do README: (x/2**16 - 0,5) * 3
assert converter_ecg_adc_para_mv(32768) == 0.0
assert converter_ecg_adc_para_mv(0) == -1.5
assert abs(converter_ecg_adc_para_mv(65535) - 1.5) < 1e-4


def gravar(pasta, ecg_amp):
    rng = np.random.default_rng(0)
    d = {"signal": {"chest": {"ECG": rng.uniform(-1, 1, (70000, 1)) * ecg_amp},
                    "wrist": {"BVP": rng.standard_normal((6400, 1))}},
         "label": np.ones(70000, dtype=np.int32), "subject": "SX"}
    (pasta / "SX").mkdir()
    with open(pasta / "SX" / "SX.pkl", "wb") as f:
        pickle.dump(d, f)


with tempfile.TemporaryDirectory() as tmp:
    ok = Path(tmp) / "ok"; ok.mkdir(); gravar(ok, 1.4)
    r = ler_sujeito(ok, "SX")
    assert len(r["ecg"]) == 70000 and r["fs_ecg"] == 700.0

    ruim = Path(tmp) / "ruim"; ruim.mkdir(); gravar(ruim, 30000.0)
    try:
        ler_sujeito(ruim, "SX")
        raise SystemExit("FALHA: ECG fora de mV deveria ser recusado")
    except ValueError:
        pass
print("Testes de conversão e de validação da leitura: OK")
