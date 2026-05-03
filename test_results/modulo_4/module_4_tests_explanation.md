# Explicação dos Testes do Módulo 4

Neste módulo, validamos o protocolo de benchmarks e a geração de resultados experimentais sob o Regime Flexível e o Regime Rígido.

## 1. O que foi testado:
- **Execução da Configuração C1/C2 (Com Redução):** Avaliação do pipeline proposto pelo artigo com a redução de variáveis ativada. 
- **Execução da Configuração C1_NoRed/C2_NoRed (Sem Redução):** Avaliação do baseline do Professor Rian para comparar o impacto empírico do tempo de execução no solver quando a redução heurística está desativada.

## 2. Resultados Obtidos:
Como documentado no relatório técnico:
- **Instância A01 (`a/instance_0001.txt`):**
  - **C1** (com redução na GPU) reduziu os pedidos de `61 -> 5` e os corredores de `116 -> 7`. A solução foi obtida em **0.43s**.
  - **C1_NoRed** (sem redução de instância) demorou **59.76s** para obter a solução exata.
  
- **Instância B07 (`b/instance_0007.txt`):**
  - **C2** (Regime Flexível com redução na GPU) processou o subproblema em apenas **60.73s**, retornando uma métrica de **6.2667**.

## 3. Conclusão:
Os testes comprovam o speedup expressivo fornecido pela etapa de redução acelerada em GPU, garantindo que o subproblema reduzido seja viável e resolvido rapidamente, prevenindo os estouros de memória e timeouts típicos das abordagens exatas puras descritas na literatura.
