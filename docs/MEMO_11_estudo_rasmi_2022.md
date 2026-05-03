# Estudo Pormenorizado: Rasmi et al. (2022) e a Estratégia MSSS

Análise detalhada do artigo internacional adicionado à nossa base bibliográfica e sua correlação com a arquitetura V4.

**Título:** Wave order picking under the mixed-shelves storage strategy: A solution method and advantages  
**Autores:** Seyyed Amir Babak Rasmi, Yuan Wang, Hadi Charkhgard  
**Revista:** Computers & Operations Research (Elsevier), Volume 137, 2022.

---

## 1. O Problema Abordado (A Estratégia MSSS)
O artigo estuda o problema de **Wave Picking Systems** focado em armazéns que utilizam a **Mixed-Shelves Storage Strategy (MSSS)**. 
- Na estratégia MSSS, os itens de uma mesma SKU não ficam guardados em um único local dedicado (*Dedicated Storage Strategy - DSS*). Em vez disso, estão espalhados por múltiplos corredores e prateleiras do armazém.
- Isso descreve **exatamente** o layout operacional real do Mercado Livre abordado no desafio SBPO.

## 2. A Metodologia Proposta (DOPBAR)
Para resolver esse problema, os autores integram três decisões cruciais:
1. **Order Batching** (Agrupamento de Pedidos);
2. **Batch Assignment** (Atribuição de Lotes aos coletores);
3. **Picker Routing** (Roteamento dos Coletores).

Eles propõem o algoritmo **DOPBAR** (*Decomposition of Order Picking into BAR subproblems*), uma heurística baseada em clusterização para resolver o modelo de programação linear inteira mista (MILP) bi-objetivo que visa minimizar tanto o *makespan* (tempo total de coleta) quanto a força de trabalho (número de coletores).

---

## 3. Contraponto e Alinhamento com a V4 (Nossa Arquitetura)

Adicionar Rasmi et al. (2022) à nossa bibliografia enriquece drasticamente o peso acadêmico do nosso artigo por três motivos estratégicos:

### A. Justificativa Teórica para a Complexidade
Os autores provam que, sob a estratégia MSSS, o problema de encontrar a rota mais curta do coletor deixa de ser um TSP clássico e se torna um problema combinatorialmente muito mais complexo, fortemente **NP-Hard**. Como o Mercado Livre adota o MSSS, isso justifica cientificamente por que as nossas instâncias gigantes não podem ser resolvidas de forma ingênua pelo CPLEX sem um pré-processamento.

### B. Embasamento para a Redução via GPU
O DOPBAR de Rasmi et al. recorre à decomposição do problema em subproblemas menores de clusterização para conseguir viabilidade. 
Isso nos dá a "carta branca" literária perfeita para a nossa **redução de instância vetorizada em GPU**: estamos aplicando os mesmos princípios de decomposição de problemas NP-Hard, porém acelerados por hardware gráfico massivamente paralelo ($O(n^2)$), antes que o solver MILP exato atue.

### C. Validação da Função Objetivo de Densidade
O artigo de Rasmi mostra que o maior ganho da estratégia MSSS ocorre quando o algoritmo consegue agrupar pedidos similares que compartilham corredores comuns para evitar que coletores cruzem o armazém inteiro. Isso valida exatamente a nossa função objetivo fracionária: a busca pela **máxima densidade** (itens coletados por corredor ativado).

**Veredito:** O trabalho de Rasmi et al. (2022) é a nossa melhor referência internacional. Ele consolida que a nossa arquitetura WOPP sob a ótica do Mercado Livre está perfeitamente alinhada com as fronteiras de pesquisa de Pesquisa Operacional em e-commerce.
