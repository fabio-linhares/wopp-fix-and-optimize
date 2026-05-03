# Explicação da Suíte de Testes: Módulo 1 (Modelagem e Leitura de Dados)

Este documento detalha os testes unitários criados para validar a leitura das instâncias e o pré-processamento de dados do problema WOPP.

---

## 1. `test_read_valid_instance` (Happy Path)
- **Razão de ser:** Garante que o parser da classe `WaveOrderPickingProblem` lê e interpreta corretamente uma instância válida padrão do problema.
- **O que valida:** 
  - Dimensões do problema: número de pedidos ($|O|$), itens ($|I|$) e corredores ($|A|$).
  - Limites operacionais da wave: $LB$ e $UB$.
  - Mapeamento completo dos itens por pedido.
  - Mapeamento completo dos itens por corredor.

---

## 2. `test_problem_fallback_preprocess` (Processamento de Dados)
- **Razão de ser:** Valida as rotinas de agregação sequencial dos dados após a leitura.
- **O que valida:**
  - O cálculo correto do total de unidades demandadas por cada pedido.
  - A estruturação correta das matrizes esparsas de itens por corredor e itens por pedido.

---

## 3. `test_empty_instance` (Error Path / Robustez)
- **Razão de ser:** Certifica que o código se comporta de maneira previsível quando o arquivo de entrada não existe ou está inacessível.
- **O que valida:**
  - Garante que a classe trata a ausência do arquivo exibindo um erro no console, sem quebrar o fluxo de execução (retornando `self` com estruturas de dados vazias).

---

## 4. `test_edge_case_zero_orders` (Edge Case / Caso de Borda)
- **Razão de ser:** Avalia a robustez do pipeline de processamento em situações de borda matemática (zero pedidos ou zero corredores).
- **O que valida:**
  - Certifica que as matrizes de agregação de dados não geram erros de divisão por zero ou quebras de memória quando os conjuntos são vazios.
