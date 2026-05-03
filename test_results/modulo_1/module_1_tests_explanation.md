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

---

## 5. `test_wave_bounds_consistency` (Validação de limites)
- **Razão de ser:** Testa a persistência correta dos limites superior e inferior ($LB$, $UB$) definidos para o tamanho da wave.
- **O que valida:**
  - Garante que os limites são passados corretamente e mantidos inalterados pela classe.

---

## 6. `test_all_order_items_uniqueness` (Unicidade de itens)
- **Razão de ser:** Valida a propriedade de identificação de itens únicos demandados.
- **O que valida:**
  - Confirma se a propriedade `all_order_items` contém exatamente os IDs únicos de itens presentes na totalidade dos pedidos.

---

## 7. `test_order_units_sum` (Somatório de itens por pedido)
- **Razão de ser:** Garante o cálculo correto do volume total de unidades associadas a um pedido.
- **O que valida:**
  - Soma de forma precisa a quantidade de itens individuais requeridos em um pedido esparso.

---

## 8. `test_invalid_line_format` (Formato inválido de arquivo)
- **Razão de ser:** Testa o tratamento de arquivos com cabeçalhos corrompidos ou mal formados.
- **O que valida:**
  - O parser detecta o erro de formatação na leitura inicial e encerra o parsing daquele arquivo graciosamente.

---

## 💡 Significado do Percentual nos Resultados do Pytest

Nos relatórios de execução gerados pelo framework `pytest` (como `module_1_tests.txt`), aparecem marcadores de percentual ao lado de cada linha de teste (Ex: `[ 12%]`, `[100%]`).

- **O que este percentual significa:** Ele representa o **progresso de execução** da bateria de testes em relação ao total de testes coletados, e **não** o percentual de sucesso do teste individual.
- **Por que é aceitável:** Se o teste exibe `PASSED` ao lado do percentual de progresso, significa que ele passou com **100% de sucesso**. O `[100%]` exibido na última linha simplesmente indica que todos os testes daquela sessão foram executados até o final.
