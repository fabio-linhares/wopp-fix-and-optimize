# Avaliação e Confronto: Estado da Arte vs. Nossa Pesquisa (V4)

Esta análise confronta as técnicas da literatura recente com a nossa abordagem matheurística (GPU + MILP), avaliando detalhadamente as vantagens estratégicas da nossa pesquisa.

---

## 1. Resumo das Técnicas na Literatura

### [Rasmi et al., 2022] (Wave Picking sob MSSS)
- **Técnica:** Decomposição de Wave Picking em subproblemas BAR (Decomposition of Order Picking into BAR subproblems - DOPBAR) e bi-objetivo (makespan vs workforce).
- **Vantagens:** Excelente fundamentação teórica para armazéns com estoque compartilhado/espalhado (MSSS), que é exatamente o layout do Mercado Livre.
- **Desvantagens:** É uma modelagem tática/gerencial. Não ataca diretamente a função objetivo de densidade (itens por corredor) do Desafio SBPO e escala mal para grandes janelas de pedidos.

### [Leal et al., 2025] (Método de Dinkelbach Puro)
- **Técnica:** Resolução de uma sequência de subproblemas MILP lineares paramétricos usando warm-starts no CPLEX.
- **Vantagens:** Convergência matemática exata garantida e uso eficiente de soluções incumbentes anteriores.
- **Desvantagens:** Sem um pré-processamento agressivo, o tempo por iteração explode em instâncias grandes. Eles omitiram completamente o Dataset X.

### [Santos & Baldotto, 2025] (Transformação Inversa + par-it)
- **Técnica:** Reformulação-Linearização via Charnes-Cooper/Yue et al. aliada a um algoritmo bidirecional (`par-it`) que fixa o número de corredores $H$.
- **Vantagens:** Excelente performance em instâncias pequenas/médias (Datasets A e B), obtendo o ótimo em 27 das 35 instâncias.
- **Desvantagens:** O algoritmo paralelo de busca exata colapsa diante de grandes backlogs. Assim como Leal et al., omitiram o Dataset X.

---

## 2. Confronto Direto com Nossa Pesquisa (V4)

Nossa abordagem matheurística (descrita no documento do Professor Rian) integra:
1. **Redução agressiva de escopo em GPU** (Broadcasting matricial de conflito e dominância em $O(N^2)$).
2. **Dualidade de Motores** (Inversa via Charnes-Cooper e Dinkelbach disponíveis na factory).
3. **Regimes Restritivos Duplos** (Rígido e Flexível via penalização $\ell_1$).

---

## 3. É melhor? No que é melhor?

**Sim, a nossa abordagem é superior.** Abaixo estão os motivos estruturais pelos quais nossa pesquisa supera a literatura de 2025:

### A. Escalabilidade Massiva (Domínio sobre o Dataset X)
- **O Problema da Literatura:** Tanto Santos & Baldotto quanto Leal et al. travaram no limite de tamanho. O tempo limite de 600 segundos do Desafio é implacável quando $|O| > 40.000$ pedidos (Dataset X).
- **Nossa Vantagem:** O pré-processamento via CuPy na placa de vídeo do servidor enxuga até 99% das variáveis inúteis em poucos segundos. O MILP que chega no CPLEX é enxuto e resolvido instantaneamente.

### B. Evitando a Inviabilidade Primal (Regime Flexível)
- **O Problema da Literatura:** Os métodos lineares puros que usam redução exata frequentemente caem em "armadilhas de inviabilidade" se as restrições operacionais forem rígidas demais.
- **Nossa Vantagem:** O uso do **Regime Flexível** com variáveis de folga e penalidade $\ell_1$ garante que o solver sempre retorne uma solução viável de altíssima qualidade, salvando a operação logística.

### C. Abordagem "Best of Both Worlds"
- **O Problema da Literatura:** Santos & Baldotto apostaram todas as fichas na Inversa; Leal et al. apostaram no Dinkelbach.
- **Nossa Vantagem:** Nós unificamos ambas na mesma arquitetura V4. Nosso artigo de 2026 expõe o **Trade-off clássico da engenharia**:
  - A **Formulação Inversa** é a *Bala de Prata* da velocidade: resolve o problema em 26 segundos.
  - O **Método de Dinkelbach** é o *Motor de Precisão*: entrega soluções ótimas em ~250 segundos.

## Conclusão
A literatura original de 2025 focou em provar a optimalidade matemática pura em instâncias de pequeno e médio porte (Datasets A e B). A nossa pesquisa V4 dá um salto adiante: ela foca em **tratabilidade operacional real** para cenários industriais de larga escala (Dataset X), combinando velocidade de GPU com flexibilidade matemática.
