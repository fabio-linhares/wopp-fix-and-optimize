# Resumo Executivo da Pesquisa: WOPP Matheurístico Acelerado por GPU

## 1. O Problema: Wave Order Picking (WOPP)
O estudo ataca o **Problema de Seleção em Ondas de Pedidos**, um gargalo crítico na logística de *e-commerce*. O objetivo do problema é maximizar a produtividade da separação de itens dentro de um armazém. Matematicamente, busca-se selecionar um conjunto de pedidos (*wave*) que maximize o "volume processado" utilizando a menor quantidade possível de "corredores" (esforço logístico de deslocamento). O grande obstáculo computacional é que essa formulação gera um problema de otimização combinatória com uma **função objetivo fracionária** altamente complexa.

## 2. A Solução Proposta: Um Pipeline Matheurístico
Em vez de depender apenas de aproximações heurísticas ou forçar um modelo exato que travaria por falta de tempo ou memória, a pesquisa propõe uma **Matheurística Acelerada**:
1. **Redução em GPU (O "Filtro"):** Antes de calcular a melhor rota, a placa de vídeo (GPU) cruza todos os pedidos usando multiplicação de matrizes ($\mathcal{O}(n^2)$). Ela expurga $>99\%$ dos pedidos "ruins" ou dominados. O que antes causava estouro de memória (OOM), agora roda em frações de segundo.
2. **Subproblema MILP (O "Motor Exato"):** Os "pedidos de elite" que sobrevivem à GPU são entregues ao CPLEX para que a matemática exata ache a melhor combinação possível.
3. **Regime Flexível (O "Salva-vidas"):** Como a GPU deleta muitos pedidos, tentar bater metas rígidas travava o sistema (inviabilidade). A pesquisa introduz um regime flexível (penalidade exata) que permite violar limites físicos em casos extremos, pagando multas ($10^3$) na função objetivo para garantir que a operação logística nunca pare.

## 3. O Benchmark e o *Trade-off*
A arquitetura foi submetida a um estresse massivo (210 testes paralelos, limite de 10 minutos por teste) resolvendo as métricas de linearização Inversa e Paramétrica (Dinkelbach).
O resultado mais brilhante da pesquisa foi a descoberta empírica de um **Cardápio de Decisão** estratégico para gerentes de armazém:
* **"Bala de Prata" (Formulação Inversa):** Se o caminhão está saindo e o armazém só tem 30 segundos para gerar uma rota, usa-se a Inversa. Ela resolve o problema na média em apenas **26 segundos**, mas com qualidade menor (métrica $4.80$).
* **"Motor de Precisão" (Dinkelbach):** Se o armazém tem tempo para planejar a onda, aciona-se o Dinkelbach. Ele demora 10 vezes mais (**257 segundos**), mas entrega uma qualidade exponencialmente maior (métrica $95.08$).

## 4. Conclusão e Relevância Científica
O artigo prova que injetar matemática exata (MILP) na logística de e-commerce é viável, desde que as arquiteturas clássicas sejam modernizadas. Ao atrelar a força bruta da **GPU** a um **regime flexível** de restrições, o pipeline superou com folga o desempenho de metaheurísticas puras tradicionais (ILS, SA, GRASP), entregando soluções logísticas executáveis em janelas de tempo táticas reais.
