# Plano de Implementação: Otimização WOPP (SBPO 2026)

Este documento descreve as etapas de desenvolvimento do pipeline de otimização *Fix-and-Optimize* para o WOPP (Wave Order Picking Problem). As etapas serão desenvolvidas de forma modular e autocontida para garantir rastreabilidade completa.

---

## Política de Implementação

Adotamos uma política rigorosa baseada em TDD e granularidade atômica:
1. **Commit de Testes:** Escrevemos os testes que definem o comportamento esperado.
2. **Commit de Desenvolvimento:** Desenvolvemos o código até que todos os testes sejam aprovados.
3. **Commit de Atualização e Resultados:** Commitar os testes passando e documentar no README.

---

## Mudanças decorrentes da Revisão (Rian e Artigo Atual)

### ⏪ Em relação ao que já fizemos (Módulo 3)
- No Módulo 3, a linearização inversa McCormick de $w_o = x_o z$ e $u_a = y_a z$ é o padrão exato, mas a inclusão de termos de penalidade no regime flexível causa bilinearidade não linearizada ($P_L \delta z$). Documentar isso como limitação teórica no relatório para evitar enfraquecimento e manter alinhamento com a justificativa da Tabela 4 do artigo ("Causa provável de apenas 20% de viabilidade").

### ⏩ Em relação ao que faremos (Módulos 4 e 5)
- **Remoção do Baseline Autoral:** No Módulo 4 e 5, remover completamente a Tabela 5 que compara com a metaheurística híbrida autoral (ILS + GRASP + Tabu).
- **Inclusão de Comparação com Literaturas do SBPO 2025:** Adicionar na Seção 5 uma comparação direta com os dados das tabelas de Santos & Baldotto (2025) e Leal et al. (2025), conforme Áudio 2 do orientador Rian.
- **Ajustar a coluna residual `c0=1`:** Na Tabela 4 do artigo, remover a coluna residual `$c_0=1$` (Configurações C3 e C4) originada de um teste anterior que foi removido, focando apenas nas configurações C1, C2, C5 e C6.

---

## Módulos de Desenvolvimento

### 📦 Módulo 1: Modelagem e Leitura de Dados (Data & Model Layer)
- **Objetivo:** Implementar a leitura unificada das instâncias (A, B, C e X).
- **Ação:** Garantir que o parser leia corretamente todos os parâmetros ($|O|$, $|A|$, $|I|$, $LB$, $UB$) e construa as matrizes e limites necessários.

---

### 📦 Módulo 2: Pré-processamento e Filtragem (Fix-and-Optimize - GPU & CPU)
- **Objetivo:** Implementar o filtro heurístico de dominância acelerado por GPU (CuPy) e em CPU.
- **Ação:** Construir o cálculo das matrizes de conflito de rotas e dominância $O(n^2)$. Isolar o filtro de forma que ele reduz os pedidos fixando $x_o = 0$ para variáveis dominadas antes de passar para o solver MILP.

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
  - Remover a comparação autoral de ILS/Tabu e incluir a comparação com as tabelas de Santos & Baldotto (2025) e Leal et al. (2025).

---

## Plano de Verificação

### Testes Automatizados
- Executar `pytest src/` após cada módulo completo para garantir que nenhuma regressão foi introduzida.
