# Checklist de Execução

- [x] **📦 Módulo 1: Modelagem e Leitura de Dados (Data & Model Layer)**
    - [x] Refinar a classe `WaveOrderPickingProblem` para leitura de todas as instâncias (A, B, C e X).
    - [x] Criar testes unitários para a classe de leitura (`test_problem.py`).
- [ ] **📦 Módulo 2: Pré-processamento e Filtragem (Fix-and-Optimize - GPU & CPU)**
    - [ ] Implementar o filtro heurístico de dominância acelerado por GPU (CuPy) e CPU.
    - [ ] Criar testes para validar a redução de escopo (`test_reducer.py`).
- [ ] **📦 Módulo 3: Motores de Otimização e Regime Flexível (Solver Layer)**
    - [ ] Implementar a Formulação Inversa (Charnes-Cooper + McCormick).
    - [ ] Implementar o Método de Dinkelbach Puro.
    - [ ] Integrar a Relaxação de Restrições via Penalidade $\ell_1$.
- [ ] **📦 Módulo 4: Protocolo de Benchmarks e Geração de Resultados**
    - [ ] Executar benchmark com redução de GPU.
    - [ ] Executar benchmark sem redução de GPU (Baseline).
    - [ ] Salvar arquivos CSV detalhados em `results/`.
- [ ] **📦 Módulo 5: Artigo Científico e Documentação (Finalização)**
    - [ ] Atualizar o relatório técnico.
    - [ ] Fazer commit final e enviar para o repositório público do GitHub.
