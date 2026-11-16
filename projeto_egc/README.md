# Projeto Final de Expressão Gáfica: PPG de Pulso vs. ECG no WESAD

**Autoras:** Camile de Santis Marques (RA 24006992) e Luana Varela Vacari (RA 24000499)  
**Instituição:** Pontifícia Universidade Católica de Campinas (PUC-Campinas) — Engenharia Biomédica (2º semestre de 2026)

---

## 1. Objetivo e Pergunta de Pesquisa

O objetivo deste projeto é avaliar o impacto do pré-processamento digital no sinal de fotopletismografia de pulso (**PPG / BVP**, captado pelo dispositivo vestível Empatica E4) para a detecção de batimentos cardíacos e a estimativa da variabilidade da frequência cardíaca (**RMSSD**), tendo como padrão-ouro o eletrocardiograma torácico (**ECG**, captado pelo RespiBAN)[cite: 1, 2].

### A Pergunta que Guia o Projet:
> *“Filtrar o PPG de pulso melhora a detecção de batimentos em relação ao sinal sem filtro, e isso muda entre baseline e estresse?”*

Esta investigação parte da lacuna apontada na revisão sistemática de Elgendi et al. (*Communications Medicine*, 2026) e em Watanabe et al. (2025)[cite: 2]: embora o PPG de pulso seja prático para o monitoramento contínuo de estresse e saúde mental, ele é altamente suscetível a artefatos de movimento e não possui um fluxo de filtragem padronizado[cite: 2]. O estudo compara três abordagens de tratamento do PPG em condições de **repouso (*baseline*)** e **estresse**:
1. **Sem filtro** (sinal bruto como linha de base)[cite: 1, 2].
2. **Filtro Passa-Banda** (Butterworth de ordem 4, 0,5 a 4 Hz, fase zero)[cite: 1].
3. **Filtro Wavelet** (`db4`, nível 6, aproximação A6 zerada e limiarização universal suave nos detalhes D1 a D3)[cite: 1].

---

## 2. Metodologia e Pipeline de Processamento

O processamento foi padronizado com os mesmos parâmetros para todos os **15 participantes válidos** da base WESAD (S2 a S17, exceto S12), totalizando **445 janelas consecutivas e não sobrepostas de 60 segundos** (285 de *baseline* e 160 de estresse)[cite: 1]:

* **Referência (ECG):** Os picos R foram extraídos do ECG (700 Hz) utilizando um detector próprio baseado no algoritmo de Pan-Tompkins (passa-banda 5–15 Hz com fase zero, derivada, quadratura, integração em janela de 150 ms e limiar adaptativo), com refinamento do instante do pico no sinal original em ±40 ms[cite: 1].
* **Detecção no PPG:** Os picos sistólicos do BVP (64 Hz) foram detectados via `find_peaks` (distância mínima de 0,4 s e proeminência relativa de 0,3 desvios-padrão do trecho) nos três braços de filtragem[cite: 1].
* **Alinhamento Temporal:** Como os sensores foram sincronizados manualmente na coleta original (apresentando atrasos de 0,8 a 1,9 s), estimou-se o atraso ótimo por segmentos de 300 s (busca em ±4 s com passo de 0,02 s) tomando o centro do platô da curva de sensibilidade[cite: 1].
* **Métricas de Avaliação:**
  * *Principais:* Sensibilidade ($Se = \frac{VP}{VP+FN}$) e Preditividade Positiva ($+P = \frac{VP}{VP+FP}$) com tolerância de **150 ms**, acompanhadas do **nível de acaso** (mediana da $Se$ em atrasos errados) e do **ganho sobre o acaso**[cite: 1].
  * *Secundária:* Erro absoluto do **RMSSD** (em ms) entre PPG e ECG por janela[cite: 1].
  * *Análise Exploratória:* Estratificação do desempenho por nível de movimento do pulso (tercis do desvio-padrão do módulo do acelerômetro) e análise de sensibilidade para tolerâncias mais estritas (50 ms e 100 ms)[cite: 1].

---

## 3. Resultados Principais (15 Participantes)

Os valores abaixo representam a média entre as janelas de cada participante e, subsequentemente, a média entre os 15 participantes (tolerância de 150 ms)[cite: 1]:

| Condição | Tratamento (Braço) | Sensibilidade ($Se$) | Preditividade ($+P$) | $Se$ do Acaso | Ganho sobre o Acaso |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Baseline** | Sem filtro | 0,769 | 0,775 | 0,333 | +0,435 |
| **Baseline** | Passa-banda | **0,792** | **0,800** | 0,329 | **+0,463** |
| **Baseline** | Wavelet | 0,772 | 0,774 | 0,335 | +0,437 |
| **Estresse** | Sem filtro | 0,601 | 0,714 | 0,408 | +0,193 |
| **Estresse** | Passa-banda | **0,611** | **0,733** | 0,404 | **+0,208** |
| **Estresse** | Wavelet | 0,609 | 0,712 | 0,415 | +0,193 |

* **Impacto do Estresse e Movimento:** Sob estresse, a sensibilidade média do filtro passa-banda caiu de **0,792 para 0,611** (e o ganho sobre o acaso caiu de 0,463 para 0,208)[cite: 1]. A correlação de Spearman entre $Se$ e movimento do pulso foi negativa em todos os participantes ($\rho = -0,52$ no geral), mas mesmo em janelas de baixo movimento o estresse manteve $Se$ inferior ao repouso (0,685 vs. 0,861), indicando degradação intrínseca do sinal de pulso[cite: 1].
* **Estimativa de RMSSD (Resultado Negativo):** Enquanto o ECG apresentou RMSSD mediano fisiologicamente plausível (45 ms no *baseline* e 36 ms no estresse), o PPG apresentou medianas de 262 ms e 350 ms, resultando em **erros absolutos medianos de 201 ms (*baseline*) e 303 ms (estresse)** no braço passa-banda[cite: 1].

---

## 4. Conclusões

1. **Efeito limitado da filtragem:** O filtro passa-banda supera o sinal bruto em apenas **1 a 2,3 pontos percentuais** de sensibilidade (diferença estatisticamente consistente, mas de pequeno efeito prático frente à variabilidade interindividual), enquanto a wavelet projetada teve desempenho equivalente ao sinal sem filtro[cite: 1].
2. **Degradação sob estresse:** O estresse compromete severamente a detecção de batimentos no pulso, efeito explicado apenas parcialmente pelo aumento da movimentação[cite: 1].
3. **Inviabilidade do RMSSD neste arranjo:** Com a taxa de amostragem do E4 (64 Hz), detector de picos simples e tolerância de 150 ms, os falsos positivos/negativos e o *jitter* temporal do pico sistólico inflam artificialmente a variabilidade batimento a batimento[cite: 1]. Portanto, o RMSSD extraído do PPG de pulso **não é utilizável** nesta configuração — um resultado negativo relevante para aplicações de monitoramento ambulatorial[cite: 1].

---

## 5. Base de Dados e Metadados

* **Base:** WESAD (*Wearable Stress and Affect Detection*), Schmidt et al., ICMI 2018[cite: 1, 2].
* **Fonte:** [UCI Machine Learning Repository](https://doi.org/10.24432/C57K5T) (acesso em 05/11/2026)[cite: 1, 2].
* **Licença:** Uso científico e não comercial[cite: 1, 2]. Os arquivos brutos (`WESAD/S*/S*.pkl`) **não estão versionados neste repositório** por restrição de licença e tamanho (~2,1 GB)[cite: 1].
* **Canais utilizados:** ECG torácico (700 Hz, 16 bits, convertido para mV), BVP/PPG de pulso não dominante (64 Hz), aceleração triaxial do pulso (32 Hz) e rótulos de protocolo (1 = *baseline*, 2 = estresse)[cite: 1, 2].

---

## 6. Estrutura do Repositório

```text
├── src/
│   ├── leitura.py              # Leitura dos arquivos .pkl e conversão de unidades
│   ├── janelas.py              # Segmentação em janelas não sobrepostas de 60 s
│   ├── filtros.py              # Implementação dos braços: sem filtro, passa-banda e wavelet
│   ├── deteccao.py             # Detector Pan-Tompkins (ECG) e detecção de picos (PPG)
│   ├── alinhamento.py          # Sincronização temporal PPG x ECG por segmentos de 300 s
│   ├── metricas.py             # Casamento de batimentos, Se, +P, nível de acaso e RMSSD
│   ├── pipeline.py             # Orquestração do fluxo completo por participante
│   ├── rodada_final.py         # Execução em lote nos 15 participantes com checkpoints CSV
│   ├── analise.py              # Consolidação estatística (bootstrap, Wilcoxon) e geração de figuras
│   ├── sintetico.py            # Gerador de sinais sintéticos para validação unitária
│   └── conferir_conversao.py   # Verificação da conversão bruta do RespiBAN no S10
├── notebooks/
│   └── projeto_egc_final.ipynb # Notebook principal de reprodução no Google Colab
├── testes/                     # Suíte de testes unitários e de integração em sinais sintéticos
├── docs/
│   ├── decisoes_metodo.md      # Justificativas técnicas e limitações
│   ├── resultados_finais.md    # Detalhamento completo das tabelas e métricas
│   ├── desvios_protocolo.md    # Registro de alterações pós-protocolo
│   ├── roteiro_estudo.md       # Guia técnico por módulo para defesa
│   └── declaracao_ia.md        # Declaração de uso de IA generativa
└── requirements.txt            # Dependências do ambiente Python (numpy, scipy, pywt, pandas, etc.)

## Como Reproduzir

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
A. Executar testes unitários (sinais sintéticos):
python -I testes/teste_picos_r.py
python -I testes/teste_wavelet.py
python -I testes/teste_alinhamento.py
python -I testes/teste_pipeline.py

B. Executar o pipeline completo:
Baixe o arquivo WESAD.zip da fonte oficial e execute o notebook notebooks/projeto_egc_final.ipynb
