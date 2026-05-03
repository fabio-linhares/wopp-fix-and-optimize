# Explicação da Suíte de Testes: Módulo 3 (Motores de Otimização e Regime Flexível)

Este documento detalha os testes criados para validar os motores de otimização no `PLISolver`.

---

## 1. `test_solver_inverse` (Formulações e Linearização Inversa)
- **Razão de ser:** Valida o funcionamento do solver MILP via transformação Inversa de Charnes-Cooper.
- **O que valida:** 
  - Correto comportamento do linearizador inverso.
  - Criação das variáveis de decisão corretas para pedidos e corredores.

---

## 2. `test_solver_dinkelbach` (Método iterativo de Dinkelbach)
- **Razão de ser:** Garante que o laço de convergência do método de Dinkelbach funciona iterativamente conforme o esperado.
- **O que valida:**
  - Convergência do método até a tolerância estipulada no artigo.

---

## 💡 Significado do Percentual nos Resultados do Pytest

Nos relatórios de execução gerados pelo framework `pytest` (como `module_3_tests.txt`), aparecem marcadores de percentual ao lado de cada linha de teste (Ex: `[ 50%]`, `[100%]`).

- **O que este percentual significa:** Ele representa o **progresso de execução** da bateria de testes em relação ao total de testes coletados naquela sessão.
- **Por que é aceitável:** Se o teste exibe `PASSED` ao lado do percentual de progresso, significa que ele passou com **100% de sucesso**.
