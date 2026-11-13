# Passo 17: a Se por janela acompanha a amplitude do BVP e o movimento do pulso? (descritivo)
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from leitura import ler_sujeito


def qualidade_por_janela(pasta, sujeito, df):
    """Acrescenta a cada janela (braço passa-banda) o desvio padrão do BVP bruto e
    o do módulo da aceleração do pulso (unidade do acelerômetro NÃO confirmada)."""
    r = ler_sujeito(pasta, sujeito)
    pb = df[df.braco == 'passa-banda'].copy()
    acc = np.linalg.norm(r['acc_pulso'], axis=1)
    bvp_std, acc_std = [], []
    for a in pb.t_ini:
        b = a + 60.0
        bvp_std.append(np.std(r['bvp'][int(round(a * r['fs_bvp'])):int(round(b * r['fs_bvp']))]))
        acc_std.append(np.std(acc[int(round(a * r['fs_acc'])):int(round(b * r['fs_acc']))]))
    pb['bvp_std'], pb['acc_std'] = bvp_std, acc_std
    return pb


res = {'S10': qualidade_por_janela(PASTA_DADOS, 'S10', df10),
       'S11': qualidade_por_janela(PASTA_DADOS, 'S11', df11)}

for s, q in res.items():
    for col in ('acc_std', 'bvp_std'):
        rho, p = spearmanr(q[col], q.se)
        print(f'{s}: Spearman(Se, {col}) = {rho:+.2f}  ({len(q)} janelas; descritivo, janelas vizinhas não são independentes)')

fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for i, (s, q) in enumerate(res.items()):
    for j, col in enumerate(('acc_std', 'bvp_std')):
        for cond, cor in (('baseline', 'tab:green'), ('estresse', 'tab:orange')):
            m = q.condicao == cond
            ax[i, j].scatter(q[col][m], q.se[m], c=cor, label=cond, s=30)
        ax[i, j].set_xscale('log')
        ax[i, j].set_ylim(0, 1.02)
        ax[i, j].set_xlabel(col + ' (escala log)')
        ax[i, j].set_ylabel('Se da janela')
        ax[i, j].set_title(s)
        ax[i, j].legend(fontsize=8)
plt.tight_layout()
plt.savefig('figura_se_vs_qualidade.png', dpi=150)
plt.show()

print('\nAs 8 janelas com menor Se de cada participante:')
for s, q in res.items():
    print(s)
    print(q.sort_values('se').head(8)[['condicao', 'janela', 'se', 'pp', 'fc_ecg', 'bvp_std', 'acc_std']].round(2).to_string(index=False))
