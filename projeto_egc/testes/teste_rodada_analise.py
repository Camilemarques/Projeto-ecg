"""Testa rodar_participantes e gerar_tudo de ponta a ponta com um zip FICTÍCIO.

Uso:  python -I testes/teste_rodada_analise.py
Cinco participantes sintéticos (ruído e movimento diferentes), mais um participante
inexistente para testar o tratamento de falhas. Sem PyWavelets, só 2 braços.
Passar aqui NÃO prova que a análise funciona nos dados reais.
"""
import pickle, sys, tempfile, zipfile
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from analise import gerar_tudo
from rodada_final import rodar_participantes
from sintetico import gerar_ecg_sintetico, gerar_ppg_sintetico

try:
    import pywt  # noqa: F401
    com_wavelet = True
except ImportError:
    com_wavelet = False

SUJ = ["S2", "S3", "S4", "S5", "S6"]


def fabricar(semente, ruido, mov):
    _, e, _ = gerar_ecg_sintetico(duracao=420, semente=semente, rr_medio=0.8, rr_dp=0.12)
    _, p, _ = gerar_ppg_sintetico(duracao=420, semente=semente, rr_medio=0.8, rr_dp=0.12,
                                  atraso=0.3 + 0.4 * semente, ruido=ruido)
    ecg = np.r_[e, e]; bvp = np.r_[p, p]
    rot = np.zeros(len(ecg), dtype=np.int32)
    rot[int(10 * 700):int(370 * 700)] = 1
    rot[int(430 * 700):int(790 * 700)] = 2
    acc = np.random.default_rng(semente).standard_normal((int(840 * 32), 3)) * mov + 60
    return {"signal": {"chest": {"ECG": ecg[:, None]}, "wrist": {"BVP": bvp[:, None], "ACC": acc}},
            "label": rot, "subject": "x"}


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    zpath = tmp / "WESAD.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        for k, s in enumerate(SUJ):
            pk = tmp / f"{s}.pkl"
            pickle.dump(fabricar(k, 0.1 + 0.1 * k, 2 + 3 * k), open(pk, "wb"))
            z.write(pk, f"WESAD/{s}/{s}.pkl")
            pk.unlink()
    dados, res = tmp / "dados" / "WESAD", tmp / "res"
    estado = rodar_participantes(SUJ + ["S99"], zpath, dados, res, usar_wavelet=com_wavelet)
    assert [estado[s] for s in SUJ] == ["ok"] * 5, estado
    assert estado["S99"] not in ("ok", "pulado"), estado
    assert (res / "erros.txt").exists()
    assert not any(dados.rglob("*.pkl")), "os .pkl extraídos deviam ter sido apagados"
    estado2 = rodar_participantes(SUJ, zpath, dados, res, usar_wavelet=com_wavelet)
    assert set(estado2.values()) == {"pulado"}, estado2          # retoma sem refazer
    t = gerar_tudo(res, esperados=SUJ + ["S99"])
    figs = sorted(p.name for p in (res / "figuras").glob("*.png"))
    print("figuras:", figs)
    assert len(figs) >= 4, figs
    assert (res / "tabelas" / "por_participante.csv").exists()
    assert "movimento_por_condicao" in t and not t["movimento_por_condicao"].empty
    assert t["por_participante"].sujeito.nunique() == 5
print("Testes da rodada e da análise: OK" + ("" if com_wavelet else " (sem a wavelet: PyWavelets ausente)"))
