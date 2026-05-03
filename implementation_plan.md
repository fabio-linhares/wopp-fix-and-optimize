# Plano de Implementação: Otimização WOPP (SBPO 2026)

Este documento descreve as etapas de desenvolvimento do pipeline de otimização *Fix-and-Optimize* para o WOPP (Wave Order Picking Problem). As etapas serão desenvolvidas de forma modular e autocontida para garantir rastreabilidade completa.

---

## Política de Implementação

Adotamos uma política rigorosa baseada em TDD e granularidade atômica:
1. **Commit de Testes:** Escrevemos os testes que definem o comportamento esperado.
2. **Commit de Desenvolvimento:** Desenvolvemos o código até que todos os testes sejam aprovados.
3. **Commit de Atualização e Resultados:** Commitar os testes passando e documentar no README.

---

## Módulos de Desenvolvimento

### 📦 Módulo 1: Modelagem e Leitura de Dados (Data & Model Layer)
- **Objetivo:** Implementar a leitura unificada das instâncias (A, B, C e X).
- **Ação:** Garantir que o parser leia corretamente todos os parâmetros ($|O|$, $|A|$, $|I|$, $LB$, $UB$) e construa as matrizes e limites necessários.

---

### 📦 Módulo 2: Pré-processamento e Filtragem (Fix-and-Optimize - GPU & CPU)
- **Objetivo:** Implementar o filtro heurístico de dominância acelerado por GPU (CuPy) e em CPU.
- **Ação:** Construir o cálculo das matrizes de conflito de rotas e dominância $O(n^2)$. Isolar o filtro de forma que ele reduza os pedidos fixando $x_o = 0$ para variáveis dominadas antes de passar para o solver MILP.

---

### 📦 Módulo 3: Motores de Otimização e Regime Flexível (Solver Layer)
- **Objetivo:** Implementar os motores de otimização linearizados.
- **Ação:** Construir as duas variantes clássicas integradas ao **Regime Flexível via Penalidade $\ell_1$**:
  1. **Formulação Inversa (Transformação de Charnes-Cooper + Envelopes de McCormick).**
  2. **Método de Dinkelbach Puro (Iterativo).**

---

### 📦 Módulo 4: Protocolo de Benchmarks e Geração de Resultados
- **Objetivo:** Executar a bateria de testes e salvar as métricas para as tabelas do artigo.
- **Etapas do protocolo:**
  1. **Execução com Redução GPU (Pipeline Proposto):** Roda as instâncias nos dois motores (Inversa e Dinkelbach) sob o Regime Flexível.
  2. **Execução sem Redução (Baseline):** Tenta rodar o modelo exato direto nas instâncias para documentar cientificamente o estouro de memória (OOM) ou timeout de 600 segundos.

---

### 📦 Módulo 5: Artigo Científico e Documentação (Finalização)
- **Objetivo:** Atualizar a narrativa científica na seção de Resultados do artigo acadêmico.
- **Mudanças:** 
  - Enquadrar definitivamente a heurística como *Fix-and-Optimize*.
  - Demonstrar as vantagens e trade-offs da aceleração por GPU.

---

## Plano de Verificação

### Testes Automatizados
- Executar `pytest src/` após cada módulo completo para garantir que nenhuma regressão foi introduzida.
