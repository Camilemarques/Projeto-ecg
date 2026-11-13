"""Leitura dos registros do WESAD.

Fonte dos metadados: wesad_readme.pdf (README oficial da base).
Verificado no participante S10 com src/inspecionar_wesad.py (05/11/2026).
"""

import pickle
from pathlib import Path

import numpy as np

# README, Seção II.1: todos os canais do RespiBAN (peito) a 700 Hz.
FS_ECG = 700.0
# README, Seção II.2: BVP (PPG) do Empatica E4 (pulso) a 64 Hz.
FS_BVP = 64.0
# README, Seção II.3: rótulos amostrados a 700 Hz.
FS_ROTULO = 700.0
# README, Seção II.2: aceleração do pulso (E4) a 32 Hz; unidade do .pkl não
# informada no README.
FS_ACC = 32.0
# README, Seção II.3.
ROTULOS = {"indefinido": 0, "baseline": 1, "estresse": 2,
           "amusement": 3, "meditacao": 4}   # 5, 6 e 7: ignorar

# README, Seção II.1: ECG(mV) = (sinal / chan_bit - 0.5) * vcc,
# com vcc = 3 V e chan_bit = 2**16.
VCC = 3.0
CHAN_BIT = 2 ** 16
LIMITE_ECG_MV = 0.5 * VCC   # a fórmula só produz valores em [-1,5, +1,5] mV


def converter_ecg_adc_para_mv(sinal_bruto):
    """
    Nome: converter_ecg_adc_para_mv
    Objetivo: converter o ECG bruto do RespiBAN (valor do conversor, 0 a
              2**16 - 1) para mV, pela fórmula do README (Seção II.1).
    Entradas: sinal_bruto (vetor de inteiros do arquivo SX_respiban.txt).
    Saídas: ecg_mv (vetor, mV).
    Pré-condições: valores brutos, NÃO já convertidos.
    Pós-condições: valores em [-1,5, +1,5] mV.
    Autoras: <nomes>
    """
    x = np.asarray(sinal_bruto, dtype=float)
    return (x / CHAN_BIT - 0.5) * VCC


def ler_sujeito(pasta_base, sujeito):
    """
    Nome: ler_sujeito
    Objetivo: ler o ECG do peito, o BVP do pulso e os rótulos de um sujeito.
    Entradas: pasta_base (caminho de dados/brutos/WESAD); sujeito (str, ex.
              "S10").
    Saídas: dict com "ecg" (mV), "bvp" (unidade não informada no README),
            "rotulo", "acc_pulso" (aceleração do pulso, 3 colunas; None se
            ausente) e as frequências "fs_ecg", "fs_bvp", "fs_acc".
    Pré-condições: arquivo <pasta_base>/<sujeito>/<sujeito>.pkl existe e é o
                   arquivo oficial da base (lido com pickle).
    Pós-condições: durações de ECG e BVP coincidem (tolerância de 2 s); o ECG
                   está dentro de +-1,5 mV; falha com mensagem clara se não.
    Autoras: <nomes>
    NOTA: no .pkl o ECG já vem em mV, apesar de o README chamá-lo de "raw".
          A faixa observada no S10 (-1,46 a +1,48) é a que a fórmula produz;
          valores brutos do conversor seriam da ordem de 30000. NÃO aplicar
          a fórmula uma segunda vez a estes dados.
    """
    caminho = Path(pasta_base) / sujeito / f"{sujeito}.pkl"
    with open(caminho, "rb") as f:
        dados = pickle.load(f, encoding="latin1")

    try:
        ecg = np.asarray(dados["signal"]["chest"]["ECG"]).ravel()
        bvp = np.asarray(dados["signal"]["wrist"]["BVP"]).ravel()
        rotulo = np.asarray(dados["label"]).ravel()
    except KeyError as e:
        raise KeyError(f"Estrutura inesperada em {caminho}: falta {e}. "
                       "Conferir o README da base.") from e

    dur_ecg, dur_bvp = len(ecg) / FS_ECG, len(bvp) / FS_BVP
    if abs(dur_ecg - dur_bvp) > 2.0:
        raise ValueError(f"{sujeito}: durações diferentes "
                         f"(ECG {dur_ecg:.1f} s, BVP {dur_bvp:.1f} s).")
    if np.max(np.abs(ecg)) > LIMITE_ECG_MV + 0.01:
        raise ValueError(f"{sujeito}: o ECG excede +-{LIMITE_ECG_MV} mV; "
                         "parece não estar em mV.")
    acc = dados["signal"]["wrist"].get("ACC")
    acc = None if acc is None else np.asarray(acc, dtype=float)
    return {"ecg": ecg, "bvp": bvp, "rotulo": rotulo, "acc_pulso": acc,
            "fs_ecg": FS_ECG, "fs_bvp": FS_BVP, "fs_acc": FS_ACC}
