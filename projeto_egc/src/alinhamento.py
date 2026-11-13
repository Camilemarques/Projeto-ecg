"""Alinhamento temporal entre o PPG (punho, E4) e o ECG (peito, RespiBAN).

Os dois aparelhos foram sincronizados à mão (README do WESAD) e, no S10, o
melhor atraso ficou entre 0,8 e 1,9 s, bem acima do atraso fisiológico do
pulso. Como os batimentos são quase periódicos, o atraso só é identificado a
menos de um intervalo entre batimentos; por isso a busca é ampla e feita em
trechos longos (300 s), não em janelas de 60 s.
"""

import numpy as np

from metricas import casar_batimentos, sensibilidade_pp


def curva_se_atraso(t_ref, t_det, tol, atrasos):
    """
    Nome: curva_se_atraso
    Objetivo: calcular a sensibilidade (Se) para cada atraso candidato.
    Entradas: t_ref (vetor, s): batimentos do ECG; t_det (vetor, s): picos do
              PPG; tol (s): tolerância do casamento; atrasos (vetor, s).
    Saídas: ses (vetor): Se para cada atraso (atraso subtraído de t_det).
    Pré-condições: t_ref e t_det no mesmo relógio, crescentes.
    Pós-condições: len(ses) = len(atrasos).
    Autoras: <nomes>
    """
    return np.array([sensibilidade_pp(*casar_batimentos(t_ref, t_det - L, tol))[0]
                     for L in atrasos])


def platao_central(atrasos, ses, folga=0.01):
    """
    Nome: platao_central
    Objetivo: achar o centro da faixa CONTÍNUA de atrasos em volta do
              máximo cuja Se é no máximo `folga` menor que a máxima.
    Entradas: atrasos (vetor, s); ses (vetor); folga (float).
    Saídas: centro, inicio, fim (s).
    Pré-condições: len(atrasos) = len(ses) > 0, atrasos crescentes.
    Pós-condições: inicio <= centro <= fim.
    Autoras: <nomes>
    NOTA: com tolerância larga vários atrasos acertam tudo; o argmax cai na
          borda desse platô e subestimaria/superestimaria o atraso.
    """
    atrasos, ses = np.asarray(atrasos), np.asarray(ses)
    j = int(np.argmax(ses))
    bom = ses >= ses[j] - folga
    i0 = i1 = j
    while i0 > 0 and bom[i0 - 1]:
        i0 -= 1
    while i1 < len(bom) - 1 and bom[i1 + 1]:
        i1 += 1
    return 0.5 * (atrasos[i0] + atrasos[i1]), atrasos[i0], atrasos[i1]


def atrasos_por_segmento(t_ref, t_det, duracao, seg_s=300.0, lim_s=4.0,
                         passo_s=0.02, tol=0.150):
    """
    Nome: atrasos_por_segmento
    Objetivo: estimar um atraso para cada segmento consecutivo de seg_s s.
    Entradas: t_ref, t_det (vetores, s); duracao (s): do registro; seg_s (s);
              lim_s (s): busca em [-lim_s, +lim_s]; passo_s (s); tol (s).
    Saídas: lista de dicts com ini, fim, atraso, se_max, se_acaso (mediana da
            curva Se x atraso, que serve de nível de referência do acaso).
    Pré-condições: t_det cobre o registro inteiro (inclusive as bordas).
    Pós-condições: um item por segmento completo, em ordem de tempo.
    Autoras: <nomes>
    """
    atrasos = np.arange(-lim_s, lim_s + 1e-9, passo_s)
    saida = []
    for ini in np.arange(0.0, duracao - seg_s + 1e-9, seg_s):
        fim = ini + seg_s
        ref = t_ref[(t_ref >= ini) & (t_ref < fim)]
        det = t_det[(t_det >= ini - lim_s - 1) & (t_det < fim + lim_s + 1)]
        ses = curva_se_atraso(ref, det, tol, atrasos)
        centro, _, _ = platao_central(atrasos, ses)
        saida.append({"ini": float(ini), "fim": float(fim), "atraso": float(centro),
                      "se_max": float(ses.max()), "se_acaso": float(np.median(ses))})
    return saida


def segmento_de(tabela, t):
    """
    Nome: segmento_de
    Objetivo: devolver o segmento (dict de atrasos_por_segmento) que contém t.
    Entradas: tabela (saída de atrasos_por_segmento); t (s).
    Saídas: dict do segmento (ini, fim, atraso, se_max, se_acaso).
    Pré-condições: tabela não vazia.
    Pós-condições: instantes além do último segmento usam o último; antes do
                   primeiro, o primeiro.
    Autoras: <nomes>
    """
    for seg in tabela:
        if seg["ini"] <= t < seg["fim"]:
            return seg
    return tabela[-1] if t >= tabela[-1]["fim"] else tabela[0]


def atraso_do_segmento(tabela, t):
    """
    Nome: atraso_do_segmento
    Objetivo: devolver o atraso do segmento que contém o instante t.
    Entradas: tabela (saída de atrasos_por_segmento); t (s).
    Saídas: atraso (s).
    Pré-condições: tabela não vazia.
    Pós-condições: ver segmento_de.
    Autoras: <nomes>
    """
    return segmento_de(tabela, t)["atraso"]


def atraso_sem_janela(t_ref, t_det, seg, janela, lim_s=4.0, passo_s=0.02,
                      tol=0.150, min_ref=20):
    """
    Nome: atraso_sem_janela
    Objetivo: estimar o atraso de um segmento SEM usar os batimentos de ECG da
              janela que vai ser avaliada (análise de sensibilidade: o atraso
              deixa de ser escolhido nos mesmos dados que a Se mede).
    Entradas: t_ref, t_det (vetores, s); seg (dict do segmento); janela
              (t_ini, t_fim) em s; lim_s, passo_s, tol como em
              atrasos_por_segmento; min_ref: mínimo de batimentos restantes.
    Saídas: atraso (s) ou nan se sobrarem menos de min_ref batimentos.
    Pré-condições: t_ref e t_det no mesmo relógio, crescentes.
    Pós-condições: a janela não influencia o atraso devolvido.
    Autoras: <nomes>
    """
    atrasos = np.arange(-lim_s, lim_s + 1e-9, passo_s)
    ref = t_ref[(t_ref >= seg["ini"]) & (t_ref < seg["fim"])]
    ref = ref[(ref < janela[0]) | (ref >= janela[1])]
    if len(ref) < min_ref:
        return float("nan")
    det = t_det[(t_det >= seg["ini"] - lim_s - 1) & (t_det < seg["fim"] + lim_s + 1)]
    ses = curva_se_atraso(ref, det, tol, atrasos)
    return float(platao_central(atrasos, ses)[0])
