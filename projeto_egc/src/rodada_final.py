"""Rodada dos participantes: extrai o .pkl do zip, processa, grava um CSV por
participante e apaga o .pkl (poupa disco). Retoma de onde parou."""

import time
import traceback
import zipfile
from pathlib import Path

from pipeline import processar_sujeito

TODOS = [f"S{i}" for i in range(2, 18) if i != 12]       # S2 a S17, sem S12 (15 participantes)


def extrair_pkl(zip_wesad, sujeito, pasta_dados):
    """
    Nome: extrair_pkl
    Objetivo: extrair só <sujeito>.pkl do zip do WESAD.
    Entradas: zip_wesad (caminho do zip); sujeito (str); pasta_dados (pasta que
              termina em 'WESAD', onde ficará <sujeito>/<sujeito>.pkl).
    Saídas: caminho do .pkl extraído (Path).
    Pré-condições: o zip tem o arquivo WESAD/<sujeito>/<sujeito>.pkl.
    Pós-condições: o .pkl existe em pasta_dados/<sujeito>/.
    Autoras: <nomes>
    """
    membro = f"WESAD/{sujeito}/{sujeito}.pkl"
    destino = Path(pasta_dados).parent
    with zipfile.ZipFile(zip_wesad) as z:
        z.extract(membro, destino)
    return Path(pasta_dados) / sujeito / f"{sujeito}.pkl"


def rodar_participantes(sujeitos, zip_wesad, pasta_dados, pasta_resultados,
                        refazer=False, apagar_pkl=True, usar_wavelet=True):
    """
    Nome: rodar_participantes
    Objetivo: processar vários participantes, um de cada vez, com checkpoint.
    Entradas: sujeitos (lista de str); zip_wesad (caminho); pasta_dados (pasta
              'WESAD' de trabalho); pasta_resultados (onde gravar os CSV);
              refazer (bool): refaz mesmo que o CSV exista; apagar_pkl (bool):
              apaga o .pkl extraído depois de processar; usar_wavelet (bool).
    Saídas: dict {sujeito: 'ok' | 'pulado' | mensagem de erro}.
    Pré-condições: o código de src/ importável; espaço em disco para 1 .pkl
                   (cerca de 0,9 GB) por vez.
    Pós-condições: pasta_resultados/janelas_<sujeito>.csv para cada 'ok';
                   falhas vão para pasta_resultados/erros.txt e NÃO param a rodada.
    Autoras: <nomes>
    """
    pasta_res = Path(pasta_resultados)
    pasta_res.mkdir(parents=True, exist_ok=True)
    estado = {}
    for s in sujeitos:
        saida = pasta_res / f"janelas_{s}.csv"
        if saida.exists() and not refazer:
            print(f"{s}: já existe, pulado")
            estado[s] = "pulado"
            continue
        pkl = Path(pasta_dados) / s / f"{s}.pkl"
        extraido_agora = False
        t0 = time.time()
        try:
            if not pkl.exists():
                extrair_pkl(zip_wesad, s, pasta_dados)
                extraido_agora = True
            df, tab = processar_sujeito(pasta_dados, s, usar_wavelet=usar_wavelet)
            df.to_csv(saida, index=False)
            pb = df[df.braco == "passa-banda"]
            partes = [f"{c}: {len(g)} janelas, Se {g.se.mean():.2f}"
                      for c, g in pb.groupby("condicao")]
            print(f"{s}: ok em {time.time() - t0:.0f} s | " + " | ".join(partes)
                  + f" | ECG suspeito: {int(pb.ecg_suspeito.sum())}")
            estado[s] = "ok"
        except Exception as e:                                   # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"
            print(f"{s}: FALHOU ({msg})")
            with open(pasta_res / "erros.txt", "a") as f:
                f.write(f"{s}\n{traceback.format_exc()}\n")
            estado[s] = msg
        finally:
            if apagar_pkl and extraido_agora and pkl.exists():
                pkl.unlink()
    falhas = [s for s, v in estado.items() if v not in ("ok", "pulado")]
    print(f"\nResumo: {sum(v == 'ok' for v in estado.values())} ok, "
          f"{sum(v == 'pulado' for v in estado.values())} pulados, {len(falhas)} falhas"
          + (f": {falhas}" if falhas else ""))
    return estado
