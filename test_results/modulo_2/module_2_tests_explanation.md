# Explicação da Suíte de Testes: Módulo 2 (Pré-processamento e Filtragem - GPU/CPU)

Este documento detalha os testes criados para validar a redução heurística de instâncias através do `InstanceReducer`.

---

## 1. `test_reducer_cpu` (Caso base de dominância)
- **Razão de ser:** Valida o algoritmo de dominância atuando em CPU para garantir que pedidos dominados por outro com score de eficiência superior sejam identificados e filtrados corretamente.
- **O que valida:** 
  - Identificação de conflito entre pedidos no mesmo corredor.
  - Correto descarte do pedido menos eficiente.

---

## 2. `test_reducer_empty_input` (Edge case de entradas vazias)
- **Razão de ser:** Confirma a robustez do reducer ao receber instâncias sem pedidos ou corredores.
- **O que valida:**
  - Retorno imediato de listas vazias sem quebrar o processamento.

---

## 3. `test_reducer_no_domination` (Casos sem dominância)
- **Razão de ser:** Testa se pedidos que operam em corredores completamente independentes não sofrem qualquer filtragem indevida.
- **O que valida:**
  - Preservação da integridade de todos os pedidos não conflitantes.

---

## 4. `test_reducer_use_gpu_fallback` (Fallback do hardware)
- **Razão de ser:** Certifica que o `InstanceReducer` possui o mecanismo de fallback automático ativado quando a GPU ou o módulo `CuPy` não estão disponíveis.
- **O que valida:**
  - Ativação do módulo NumPy caso `cupy` não possa ser inicializado.

---

## 💡 Significado do Percentual nos Resultados do Pytest

Nos relatórios de execução gerados pelo framework `pytest` (como `module_2_tests.txt`), aparecem marcadores de percentual ao lado de cada linha de teste (Ex: `[ 25%]`, `[100%]`).

- **O que este percentual significa:** Ele representa o **progresso de execução** da bateria de testes em relação ao total de testes coletados naquela sessão.
- **Por que é aceitável:** Se o teste exibe `PASSED` ao lado do percentual de progresso, significa que ele passou com **100% de sucesso**.
