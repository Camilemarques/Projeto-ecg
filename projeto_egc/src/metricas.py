"""Métricas de detecção de batimentos e de variabilidade (RMSSD).

Cada função abaixo é um subalgoritmo com cabeçalho. AJUSTAR os campos ao
modelo de cabeçalho padronizado da Aula 3, se for diferente deste.
"""

import numpy as np


def casar_batimentos(t_ref, t_det, tol):
    """
    Nome: casar_batimentos
    Objetivo: casar, um a um, os batimentos detectados com os de referência.
    Entradas: t_ref (vetor, s, crescente); t_det (vetor, s, crescente);
              tol (float, s): janela de tolerância do casamento.
    Saídas: vp, fn, fp (inteiros).
    Pré-condições: t_ref e t_det já estão no mesmo eixo de tempo (alinhados).
    Pós-condições: vp + fn = len(t_ref); vp + fp = len(t_det).
    Autoras: <nomes>
    """
    t_ref = np.asarray(t_ref, dtype=float)
    t_det = np.asarray(t_det, dtype=float)
    usado = np.zeros(len(t_det), dtype=bool)
    vp = 0
    for r in t_ref:
        if len(t_det) == 0:
            break
        dist = np.abs(t_det - r)
        dist[usado] = np.inf
        j = int(np.argmin(dist))
        if dist[j] <= tol:
            usado[j] = True
            vp += 1
    fn = len(t_ref) - vp
    fp = len(t_det) - vp
    return vp, fn, fp


def sensibilidade_pp(vp, fn, fp):
    """
    Nome: sensibilidade_pp
    Objetivo: calcular sensibilidade Se = VP/(VP+FN) e preditividade
              positiva +P = VP/(VP+FP).
    Entradas: vp, fn, fp (inteiros >= 0).
    Saídas: se, pp (float em [0, 1]); np.nan quando o denominador é zero.
    Pré-condições: contagens vindas de casar_batimentos.
    Pós-condições: valores entre 0 e 1, ou nan.
    Autoras: <nomes>
    """
    se = vp / (vp + fn) if (vp + fn) > 0 else np.nan
    pp = vp / (vp + fp) if (vp + fp) > 0 else np.nan
    return se, pp


def rmssd_ms(t_bat):
    """
    Nome: rmssd_ms
    Objetivo: calcular o RMSSD (ms) a partir dos instantes dos batimentos.
    Entradas: t_bat (vetor, s, crescente), idealmente de uma janela de 60 s.
    Saídas: rmssd (float, ms); np.nan se houver menos de 3 batimentos.
    Pré-condições: batimentos já validados (sem artefatos óbvios).
    Pós-condições: rmssd >= 0 ou nan.
    Autoras: <nomes>
    """
    t_bat = np.asarray(t_bat, dtype=float)
    if len(t_bat) < 3:
        return np.nan
    ibi_ms = np.diff(t_bat) * 1000.0
    return float(np.sqrt(np.mean(np.diff(ibi_ms) ** 2)))


def estimar_atraso(t_ref, t_det, tol, faixa=0.5, passo=0.02):
    """
    Nome: estimar_atraso
    Objetivo: estimar o atraso (s) do PPG em relação ao ECG, escolhendo o
              deslocamento que maximiza o número de batimentos casados.
    Entradas: t_ref, t_det (vetores, s); tol (s); faixa (s): busca em
              [-faixa, +faixa]; passo (s): resolução da busca.
    Saídas: atraso (float, s): valor a SUBTRAIR de t_det para alinhar.
    Pré-condições: a faixa deve ser menor que metade do intervalo médio entre
              batimentos, senão o casamento fica ambíguo.
    Pós-condições: atraso dentro de [-faixa, +faixa].
    Autoras: <nomes>
    NOTA: a faixa e o passo são parâmetros a justificar no protocolo.
    """
    t_ref = np.asarray(t_ref, dtype=float)
    t_det = np.asarray(t_det, dtype=float)
    melhor, melhor_vp, melhor_res = 0.0, -1, np.inf
    for a in np.arange(-faixa, faixa + passo / 2, passo):
        deslocado = t_det - a
        vp, _, _ = casar_batimentos(t_ref, deslocado, tol)
        # Desempate: vários atrasos casam todos os batimentos (um "platô" de
        # largura 2*tol). Escolhe o de menor distância média entre os pares,
        # que fica no centro do platô, e não na borda.
        if len(deslocado) > 0 and len(t_ref) > 0:
            d = np.min(np.abs(t_ref[:, None] - deslocado[None, :]), axis=1)
            res = float(np.mean(d[d <= tol])) if np.any(d <= tol) else np.inf
        else:
            res = np.inf
        if vp > melhor_vp or (vp == melhor_vp and res < melhor_res):
            melhor, melhor_vp, melhor_res = float(a), vp, res
    return melhor
