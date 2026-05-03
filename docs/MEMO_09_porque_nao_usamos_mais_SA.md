# Justificativa Técnica: Substituição do Simulated Annealing pela Busca Tabu

## Contexto Inicial
Durante as fases preliminares do desenvolvimento dos *baselines* estocásticos para o nosso artigo do SBPO 2026, a intenção original era utilizar o **Simulated Annealing (SA)** como um dos algoritmos de comparação contra o nosso pipeline matheurístico exato (MILP + GPU).

## O Problema com o SA
Ao reavaliarmos os resultados e os *logs* de execução da nossa primeira implementação do SA, percebemos que o desempenho do algoritmo não estava tão "bom" quanto o esperado estatisticamente. A natureza do *Wave Order Picking Problem* (WOPP) — com seu espaço de busca restrito por limites de capacidade e cobertura de itens — fazia com que o SA frequentemente ficasse preso em vales de soluções inviáveis ou necessitasse de um tempo excessivo de "resfriamento" para aceitar soluções de qualidade.

A calibração fina da taxa de resfriamento ($\alpha$), da temperatura inicial ($T_0$) e da condição de parada exigiria um esforço de sintonia (*tuning*) computacional massivo.

## A Decisão de Pivô: Adoção da Busca Tabu
Diante desse gargalo de calibração, decidimos que, em vez de desperdiçar ciclos de pesquisa tentando forçar o SA a funcionar de forma competitiva, seria mais inteligente e cientificamente pragmático trocar o critério probabilístico do SA por um mecanismo determinístico de memória: a **Busca Tabu (Tabu Search)**.

A Busca Tabu foi então acoplada diretamente à nossa implementação do *Iterated Local Search* (ILS), resultando em uma **Metaheurística Híbrida** mais poderosa e fácil de calibrar, composta por:
1. **Construção via GRASP:** Gera soluções iniciais diversificadas com um fator $\alpha_{RC} = 0,2$ e uma lista restrita de candidatos (RCL) de tamanho 5.
2. **Perturbação ILS:** Força o algoritmo a explorar novas áreas do espaço de soluções (força = $0,2$ e até 100 iterações totais).
3. **Memória Tabu (O substituto do SA):** Em vez de aceitar soluções piores com base em uma probabilidade térmica falha, a lista Tabu simplesmente "proíbe" que o algoritmo desfaça seus últimos passos (*Tabu Tenure* = 10). Isso garante a fuga de ótimos locais de forma determinística e acelerada.

## Conclusão
A migração do *Simulated Annealing* para o componente de *Busca Tabu* dentro do ILS não apenas enxugou o repositório (evitando a manutenção de múltiplos arquivos estocásticos independentes), mas também gerou um adversário (baseline) muito mais robusto, que alcançou até 88% de desempenho relativo, servindo como uma métrica de comparação digna e desafiadora para o nosso método exato de matrizes em GPU.
