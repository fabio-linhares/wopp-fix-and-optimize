# Plano de Implementação: Otimização WOPP (SBPO 2026)

Este plano descreve a reestruturação e execução do pipeline de otimização *Fix-and-Optimize* para o WOPP (Wave Order Picking Problem), alinhado com as orientações do Professor Rian e os artigos da literatura recente (Santos & Baldotto, 2025; Leal et al., 2025).

As etapas serão desenvolvidas e commitadas em módulos autocontidos e completos para garantir rastreabilidade total.

---

## User Review Required

> [!IMPORTANT]
> **Alterações Metodológicas Relevantes:**
> 1. **Mudança de Enquadramento:** O pipeline passa a ser categorizado formalmente como um *Fix-and-Optimize*.
> 2. **Remoção de Metaheurísticas:** A comparação frágil com o baseline autoral (ILS/Tabu) foi removida.
> 3. **Novo Baseline:** Inclusão do cenário do Solver Exato sem redução para comprovar cientificamente o valor do filtro na GPU.

---

## Módulos de Implementação (Etapas Autocontidas)

### 📦 Módulo 1: Modelagem e Leitura de Dados (Data & Model Layer)

#### [MODIFY] [problem.py](file:///home/zerocopia/Downloads/sbpo%202026/Projeto_MercadoLivre_v4/src/models/problem.py)
#### [NEW] [test_problem.py](file:///home/zerocopia/Downloads/sbpo%202026/Projeto_MercadoLivre_v4/src/models/test_problem.py)

- **Objetivo:** Refinar a classe `WaveOrderPickingProblem` para leitura unificada das instâncias (Grupos A, B, C e X).
- **Ação:** Garantir que o parser leia corretamente todos os parâmetros ($|O|$, $|A|$, $|I|$, $LB$, $UB$) e construa as matrizes esparsas e densas necessárias.

---

### 📦 Módulo 2: Pré-processamento e Filtragem (Fix-and-Optimize - GPU & CPU)

#### [MODIFY] [instance_reducer.py](file:///home/zerocopia/Downloads/sbpo%202026/Projeto_MercadoLivre_v4/src/utils/instance_reducer.py)
#### [NEW] [test_reducer.py](file:///home/zerocopia/Downloads/sbpo%202026/Projeto_MercadoLivre_v4/src/utils/test_reducer.py)

- **Objetivo:** Implementar o filtro heurístico de dominância acelerado por GPU (CuPy) e em CPU (como fallback).
- **Ação:** Construir o cálculo das matrizes de conflito de rotas e dominância $O(n^2)$. Isolar o filtro de forma que ele reduza os pedidos fixando $x_o = 0$ para variáveis dominadas antes de passar para o solver MILP.

---

### 📦 Módulo 3: Motores de Otimização e Regime Flexível (Solver Layer)

#### [MODIFY] [pli_solver.py](file:///home/zerocopia/Downloads/sbpo%202026/Projeto_MercadoLivre_v4/src/solvers/pli/pli_solver.py)

- **Objetivo:** Implementar os motores de otimização linearizados.
- **Ação:** Construir as duas variantes clássicas integradas ao **Regime Flexível via Penalidade $\ell_1$**:
  1. **Formulação Inversa (Transformação de Charnes-Cooper + Envelopes de McCormick).**
  2. **Método de Dinkelbach Puro (Iterativo).**
- Garantir que as variáveis de folga e penalizações $\ell_1$ atuem em 100% dos testes para mitigar qualquer cenário de inviabilidade local gerado pelo Módulo 2.

---

### 📦 Módulo 4: Protocolo de Benchmarks e Geração de Resultados

#### [MODIFY] [run_experiments.py](file:///home/zerocopia/Downloads/sbpo%202026/Projeto_MercadoLivre_v4/run_experiments.py)

- **Objetivo:** Executar a bateria de testes e salvar as métricas para as tabelas do artigo.
- **Etapas do protocolo:**
  1. **Execução com Redução GPU (Pipeline Proposto):** Roda as instâncias nos dois motores (Inversa e Dinkelbach) sob o Regime Flexível.
  2. **Execução sem Redução (Baseline do Professor Rian):** Tenta rodar o modelo exato direto nas instâncias para documentar cientificamente o estouro de memória (OOM) ou timeout de 600 segundos.
- Salvar os resultados detalhados em arquivos CSV na pasta `results/`.

---

### 📦 Módulo 5: Artigo Científico e Documentação (Finalização)

#### [NEW] [artigo_revisado.md](file:///home/zerocopia/Downloads/sbpo%202026/Projeto_MercadoLivre_v4/docs/artigo_revisado.md)

- **Objetivo:** Atualizar a narrativa científica na seção de Resultados do artigo.
- **Mudanças:** 
  - Trocar o termo "falha do algoritmo em 80%" por "inviabilidade matemática de subproblema sob redução no regime rígido".
  - Enquadrar definitivamente a heurística como *Fix-and-Optimize*.
  - Remover comparações com metaheurísticas fracas (ILS/Tabu).

---

## Plano de Verificação

### Testes Automatizados
- Executar `pytest src/` após cada módulo completo para garantir que nenhuma regressão foi introduzida.

### Validação dos Resultados
- Verificar se todas as saídas geradas respeitam os limites operacionais ($LB$, $UB$) e a cobertura de estoque.
- Garantir que o tempo total de execução permaneça abaixo do timeout estrito de 600 segundos.
