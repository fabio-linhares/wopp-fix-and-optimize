# Limitação de Licença do CPLEX e Uso de Fallback de Código Aberto

Este documento explica formalmente o motivo pelo qual o pipeline foi ajustado para utilizar o solver de código aberto (**CBC**) quando executado em ambientes restritos pela licença do solver comercial (**IBM CPLEX**).

## ⚠️ O Problema com o CPLEX Community Edition

No ambiente local de testes, a versão instalada do módulo Python do CPLEX é a **Community Edition**, que impõe restrições estritas de tamanho do problema:
- Máximo de **1.000 variáveis**.
- Máximo de **1.000 restrições**.

Como as sub-instâncias geradas após a redução matheurística por GPU na instância **B08** (12.334 pedidos) ainda contêm um número de variáveis/restrições que ultrapassa essa barreira da versão gratuita do CPLEX, o solver comercial rejeita a resolução com a seguinte mensagem de erro:

```text
CPLEX Error 1016: Community Edition. Problem size limits exceeded. Purchase at http://ibm.biz/error1016.
```

## 🛠️ A Solução: Fallback Inteligente para o Solver CBC

Para garantir que o código **não falhe**, que a instância **completa de B08** seja resolvida até o fim e que os experimentos sejam totalmente reprodutíveis, implementamos um **fallback inteligente para o solver CBC**:

1. O script tenta otimizar utilizando o solver comercial CPLEX.
2. Caso o CPLEX retorne o erro `1016` (limite da versão Community excedido), o pipeline detecta essa restrição em frações de segundo.
3. O script ativa dinamicamente o solver **CBC** de fallback, fornecendo a ele o subproblema matheurístico exato gerado pela filtragem.
4. O solver CBC (que é de código aberto e gratuito) processa o problema sem **nenhum limite artificial de variáveis/restrições**.
5. O pipeline foi configurado para direcionar **100% da capacidade multi-threading** (ex: até 20 threads) para o CBC, mitigando a diferença de tempo e entregando o ótimo exato do subproblema.

Este fallback garante a execução correta da matheurística original e o cálculo dos resultados sem comprometer a integridade do estudo científico.
