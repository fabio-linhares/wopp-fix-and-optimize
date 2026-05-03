# Explicação dos Testes do Módulo 4

Neste módulo, validamos o protocolo de benchmarks e a geração de resultados experimentais sob o Regime Flexível e o Regime Rígido.

## 1. O que foi testado:
- **Execução da Configuração C1 (Com Redução):** Avaliação do pipeline proposto pelo artigo com a redução de variáveis ativada. 
- **Execução da Configuração C1_NoRed (Sem Redução):** Avaliação do baseline do Professor Rian para comparar o impacto empírico do tempo de execução no solver quando a redução heurística está desativada.

## 2. Resultados Obtidos:
Como pode ser visto em `module_4_tests.txt`:
- A configuração **C1** (com redução na GPU) reduziu os pedidos de `61 -> 10` e os corredores de `116 -> 24`. A solução foi obtida em **0.44s**.
- A configuração **C1_NoRed** (sem redução de instância) demorou **14.23s** para obter a solução exata.

## 3. Conclusão:
Os testes comprovam o speedup expressivo fornecido pela etapa de redução acelerada em GPU, validando a matheurística proposta.
