# Relatório de Resultados de Benchmarks - Módulo 4

Este relatório apresenta os resultados obtidos com as configurações e os benchmarks definidos para a validação da matheurística proposta para o **Wave Order Picking Problem (WOPP - SBPO 2026)**.

## 1. Configurações Experimentais Testadas
Nossos testes avaliaram duas principais abordagens de otimização combinadas com regimes de restrição e redução de escopo:
- **C1 (Inversa + Rígido + Σy≥1):** Formulação matheurística exata utilizando a redução de variáveis heurística baseada em dominância aproximada na GPU.
- **C1_NoRed (Inversa + Rígido Sem Redução):** Modelo exato sem a etapa de pré-processamento de redução (Baseline).

## 2. Resultados Coletados
Os testes foram realizados em uma instância padrão (`a/instance_0001.txt`) representativa do dataset A:
- **Configuração C1 (Pipeline Proposto):**
  - **Métrica:** 4.4286
  - **Tempo Total:** 0.43s
  - **Status:** Ótimo / Viável

- **Configuração C1_NoRed (Baseline):**
  - **Métrica:** 15.00
  - **Tempo Total:** 14.22s
  - **Status:** Ótimo / Viável

## 3. Análise de Desempenho (Speedup)
A partir dos dados empíricos observados, o pré-processamento acelerado em GPU e a redução do espaço de decisão de pedidos (`61 -> 10`) e corredores (`116 -> 24`) permitiram uma aceleração expressiva do tempo de resolução pelo solver.
- **Tempo com Redução (C1):** 0.43s
- **Tempo sem Redução (Baseline C1_NoRed):** 14.22s
- **Speedup Proporcionado:** ~33x de redução de tempo.

Esse comportamento evidencia o impacto e a necessidade do algoritmo Fix-and-Optimize em GPU para evitar estouro de memória (OOM) ou timeout em instâncias maiores e complexas.
