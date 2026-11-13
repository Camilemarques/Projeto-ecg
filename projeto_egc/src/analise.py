"""Análise final: tabelas e figuras a partir dos CSV por participante.

Unidade de análise: o participante (média das janelas de cada participante).
Janelas vizinhas não são independentes; p-valores e intervalos são descritivos.
"""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CONDICOES = ("baseline", "estresse")
ORDEM_BRACOS = ("sem filtro", "passa-banda", "wavelet")


def carregar_resultados(pasta, esperados=None):
    """
    Nome: carregar_resultados
    Objetivo: juntar os CSV janelas_<sujeito>.csv de uma pasta.
    Entradas: pasta (caminho); esperados (lista de participantes ou None).
    Saídas: df (tabela única) e faltando (lista dos esperados sem CSV).
    Pré-condições: ao menos um CSV na pasta.
    Pós-condições: nenhuma linha é descartada.
    Autoras: <nomes>
    """
    arquivos = sorted(Path(pasta).glob("janelas_*.csv"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum janelas_*.csv em {pasta}")
    df = pd.concat([pd.read_csv(f) for f in arquivos], ignore_index=True)
    faltando = sorted(set(esperados) - set(df.sujeito)) if esperados else []
    return df, faltando


def _bracos(df):
    return [b for b in ORDEM_BRACOS if b in set(df.braco)]


def por_participante(df):
    """Média das janelas de cada participante, por condição e braço."""
    cols = [c for c in ("se", "pp", "se_acaso", "se50", "se100", "se_loo", "pp_loo") if c in df]
    g = df.groupby(["sujeito", "condicao", "braco"])
    out = g[cols].mean()
    out["n_janelas"] = g.size()
    out["ganho_sobre_acaso"] = out["se"] - out["se_acaso"]
    return out.reset_index()


def resumo_entre_participantes(part):
    """Média, desvio padrão, mínimo e máximo, entre participantes."""
    cols = ["se", "pp", "se_acaso", "ganho_sobre_acaso"]
    r = part.groupby(["condicao", "braco"])[cols].agg(["mean", "std", "min", "max"])
    r["n_participantes"] = part.groupby(["condicao", "braco"]).sujeito.nunique()
    return r.round(3)


def diferencas_pareadas(part, comparacoes, metricas=("se", "pp"), n_boot=10000, semente=0):
    """
    Diferença entre dois braços, participante a participante, por condição:
    média, IC95% por bootstrap sobre participantes e p de Wilcoxon (descritivo).
    """
    linhas = []
    for cond in CONDICOES:
        for b1, b2 in comparacoes:
            for m in metricas:
                p = part[part.condicao == cond].pivot(index="sujeito", columns="braco", values=m)
                if b1 not in p or b2 not in p:
                    continue
                d = (p[b1] - p[b2]).dropna().to_numpy()
                if len(d) < 3:
                    continue
                rng = np.random.default_rng(semente)
                med = rng.choice(d, size=(n_boot, len(d)), replace=True).mean(axis=1)
                lo, hi = np.percentile(med, [2.5, 97.5])
                try:
                    pw = float(wilcoxon(d).pvalue)
                except ValueError:                                  # todas as diferenças são zero
                    pw = float("nan")
                linhas.append(dict(condicao=cond, comparacao=f"{b1} - {b2}", metrica=m,
                                   n=len(d), media=d.mean(), ic95_inf=lo, ic95_sup=hi,
                                   p_wilcoxon=pw))
    return pd.DataFrame(linhas).round(4)


def _com_movimento(df):
    """Acrescenta o nível de movimento (tercis de acc_std de TODAS as janelas, só a
    aceleração, sem olhar a Se) a cada linha; devolve (df, (q1, q2))."""
    base = df[df.braco == "passa-banda"][["sujeito", "condicao", "janela", "acc_std"]].dropna()
    if base.empty:
        return pd.DataFrame(), (np.nan, np.nan)
    q1, q2 = base.acc_std.quantile([1 / 3, 2 / 3]).to_numpy()
    base["movimento"] = np.where(base.acc_std <= q1, "1 baixo",
                                 np.where(base.acc_std <= q2, "2 médio", "3 alto"))
    d = df.merge(base[["sujeito", "condicao", "janela", "movimento"]],
                 on=["sujeito", "condicao", "janela"])
    return d, (float(q1), float(q2))


def estratificar_movimento(df):
    """Se média por nível de movimento e braço (baseline e estresse juntos) e os limites."""
    d, lim = _com_movimento(df)
    if d.empty:
        return pd.DataFrame(), lim
    g = d.groupby(["movimento", "braco"])
    tab = g[["se", "pp", "se_acaso"]].mean()
    tab["n_janelas"] = g.size()
    return tab.round(3), lim


def movimento_por_condicao(df):
    """Mesma tabela, mas dentro de cada condição (movimento e estresse andam juntos;
    esta tabela separa os dois efeitos)."""
    d, _ = _com_movimento(df)
    if d.empty:
        return pd.DataFrame()
    g = d.groupby(["condicao", "movimento", "braco"])
    tab = g[["se", "pp", "se_acaso"]].mean()
    tab["n_janelas"] = g.size()
    return tab.round(3)


def sensibilidade(df):
    """Se por tolerância (50, 100 e 150 ms) e com o atraso estimado sem a janela."""
    cols = [c for c in ("se50", "se100", "se", "se_loo") if c in df]
    return df.groupby(["condicao", "braco"])[cols].mean().round(3)


def erro_rmssd(df):
    """
    Erro absoluto do RMSSD do PPG em relação ao do ECG (ms), por condição e braço.
    Só janelas com ECG plausível. Duas versões: todas as janelas e só as com Se >= 0,8.
    """
    d = df[~df.ecg_suspeito].copy()
    d["erro"] = (d.rmssd_ppg - d.rmssd_ecg).abs()
    d = d.dropna(subset=["erro"])
    todas = d.groupby(["condicao", "braco"]).erro.agg(["mean", "median", "count"])
    boas = d[d.se >= 0.8].groupby(["condicao", "braco"]).erro.agg(["mean", "median", "count"])
    return todas.round(1), boas.round(1)


def correlacao_movimento(df):
    """Spearman entre Se (passa-banda) e acc_std / bvp_std, por participante e geral."""
    pb = df[df.braco == "passa-banda"]
    linhas = []
    for nome, g in list(pb.groupby("sujeito")) + [("todos", pb)]:
        for col in ("acc_std", "bvp_std"):
            h = g[["se", col]].dropna()
            if len(h) >= 5 and h[col].nunique() > 1 and h.se.nunique() > 1:
                linhas.append(dict(sujeito=nome, variavel=col, rho=spearmanr(h[col], h.se)[0],
                                   n_janelas=len(h)))
    return pd.DataFrame(linhas).round(2)


def figuras(df, part, pasta_fig):
    pasta_fig = Path(pasta_fig)
    pasta_fig.mkdir(parents=True, exist_ok=True)
    bracos = _bracos(df)
    cores = {"sem filtro": "tab:gray", "passa-banda": "tab:red", "wavelet": "tab:blue"}

    # 1) Se por participante, baseline e estresse, braço passa-banda, com o acaso
    pb = part[part.braco == "passa-banda"]
    sujeitos = sorted(pb.sujeito.unique(), key=lambda s: int(s[1:]))
    fig, ax = plt.subplots(figsize=(11, 4))
    x = np.arange(len(sujeitos))
    for k, (cond, cor) in enumerate((("baseline", "tab:green"), ("estresse", "tab:orange"))):
        g = pb[pb.condicao == cond].set_index("sujeito").reindex(sujeitos)
        ax.bar(x + (k - 0.5) * 0.38, g.se, width=0.36, color=cor, label=f"Se, {cond}")
        ax.scatter(x + (k - 0.5) * 0.38, g.se_acaso, color="k", marker="_", s=120,
                   label="Se do acaso" if k == 0 else None)
    ax.set_xticks(x)
    ax.set_xticklabels(sujeitos)
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Se (média das janelas)")
    ax.set_title("Passa-banda: sensibilidade por participante (traço preto = nível de acaso)")
    ax.legend(fontsize=8, ncol=3, loc="upper center")
    fig.tight_layout()
    fig.savefig(pasta_fig / "fig1_se_por_participante.png", dpi=150)
    plt.close(fig)

    # 2) Se por braço, uma linha por participante (pareado)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, cond in zip(axs, CONDICOES):
        g = part[part.condicao == cond].pivot(index="sujeito", columns="braco", values="se")
        for _, linha in g[bracos].iterrows():
            ax.plot(range(len(bracos)), linha.to_numpy(), color="0.7", lw=0.8, marker="o", ms=3)
        ax.plot(range(len(bracos)), g[bracos].mean().to_numpy(), color="k", lw=2, marker="s")
        ax.set_xticks(range(len(bracos)))
        ax.set_xticklabels(bracos)
        ax.set_title(cond)
        ax.set_ylim(0, 1.02)
    axs[0].set_ylabel("Se por participante (cinza) e média (preto)")
    fig.tight_layout()
    fig.savefig(pasta_fig / "fig2_se_por_braco_pareada.png", dpi=150)
    plt.close(fig)

    # 3) Se por nível de movimento
    tab, _ = estratificar_movimento(df)
    if not tab.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        niveis = sorted(tab.index.get_level_values(0).unique())
        larg = 0.8 / len(bracos)
        for k, b in enumerate(bracos):
            vals = [tab.loc[(n, b), "se"] if (n, b) in tab.index else np.nan for n in niveis]
            ax.bar(np.arange(len(niveis)) + (k - (len(bracos) - 1) / 2) * larg, vals,
                   width=larg * 0.95, color=cores[b], label=b)
        ax.set_xticks(range(len(niveis)))
        ax.set_xticklabels(niveis)
        ax.set_ylim(0, 1.18)
        ax.set_ylabel("Se média das janelas")
        ax.set_xlabel("movimento do pulso (tercis de acc_std)")
        ax.legend(fontsize=8, ncol=len(bracos), loc="upper center")
        fig.tight_layout()
        fig.savefig(pasta_fig / "fig3_se_por_movimento.png", dpi=150)
        plt.close(fig)

    # 4) erro de RMSSD
    d = df[~df.ecg_suspeito].copy()
    d["erro"] = (d.rmssd_ppg - d.rmssd_ecg).abs()
    d = d.dropna(subset=["erro"])
    if not d.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        dados = [d[d.braco == b].erro.to_numpy() for b in bracos]
        ax.boxplot(dados, showfliers=False)
        ax.set_xticklabels(bracos)
        ax.set_ylabel("erro absoluto do RMSSD (ms)")
        ax.set_xlabel("valores extremos (outliers) não mostrados")
        fig.tight_layout()
        fig.savefig(pasta_fig / "fig4_erro_rmssd.png", dpi=150)
        plt.close(fig)


def gerar_tudo(pasta_resultados, esperados=None):
    """
    Nome: gerar_tudo
    Objetivo: gerar as tabelas e figuras finais a partir dos CSV por participante.
    Entradas: pasta_resultados (pasta com janelas_*.csv); esperados (lista).
    Saídas: dict com as tabelas (DataFrames).
    Pré-condições: CSV gerados por rodar_participantes.
    Pós-condições: grava tabelas/*.csv e figuras/*.png dentro de pasta_resultados e
                   imprime um resumo; avisa quais participantes estão faltando.
    Autoras: <nomes>
    """
    pasta = Path(pasta_resultados)
    df, faltando = carregar_resultados(pasta, esperados)
    (pasta / "tabelas").mkdir(exist_ok=True)
    part = por_participante(df)
    bracos = _bracos(df)
    comps = [("passa-banda", "sem filtro")]
    if "wavelet" in bracos:
        comps += [("wavelet", "sem filtro"), ("wavelet", "passa-banda")]
    mov, limites = estratificar_movimento(df)
    rm_todas, rm_boas = erro_rmssd(df)
    t = {"por_participante": part, "resumo": resumo_entre_participantes(part),
         "diferencas_pareadas": diferencas_pareadas(part, comps, metricas=("se", "pp", "ganho_sobre_acaso")),
         "movimento": mov, "movimento_por_condicao": movimento_por_condicao(df), "sensibilidade": sensibilidade(df), "rmssd_todas": rm_todas,
         "rmssd_se80": rm_boas, "correlacao_movimento": correlacao_movimento(df),
         "controle": df.groupby(["sujeito", "braco"]).agg(
             janelas=("janela", "size"), ecg_suspeito=("ecg_suspeito", "sum")).reset_index()}
    for nome, tab in t.items():
        tab.to_csv(pasta / "tabelas" / f"{nome}.csv")
    figuras(df, part, pasta / "figuras")

    n_part = df.sujeito.nunique()
    print(f"{n_part} participantes, {len(df) // max(1, len(bracos))} janelas.")
    if faltando:
        print(f"ATENÇÃO: faltam {faltando}")
    print(f"Janelas com ECG suspeito (FC fora de 40-180 bpm): "
          f"{int(df[df.braco == bracos[0]].ecg_suspeito.sum())}")
    print("\nResumo entre participantes:\n", t["resumo"].to_string())
    print("\nDiferenças pareadas (média, IC95% por bootstrap, p de Wilcoxon descritivo):\n",
          t["diferencas_pareadas"].to_string(index=False))
    print(f"\nSe por nível de movimento (limites de acc_std: {limites[0]:.2f} e {limites[1]:.2f}):\n",
          mov.to_string())
    print("\nSe por nível de movimento, dentro de cada condição:\n", t["movimento_por_condicao"].to_string())
    print("\nSensibilidade (tolerância e atraso sem a janela):\n", t["sensibilidade"].to_string())
    print("\nErro de RMSSD (ms), todas as janelas:\n", rm_todas.to_string())
    print("\nErro de RMSSD (ms), só janelas com Se >= 0,8:\n", rm_boas.to_string())
    print("\nCorrelação (Spearman) Se x movimento/amplitude:\n", t["correlacao_movimento"].to_string(index=False))
    return t
