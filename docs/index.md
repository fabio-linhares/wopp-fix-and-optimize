# Zero-Indexer: Base de Conhecimento WOPP (V4)

Bem-vindo ao índice mestre de documentação do Projeto Mercado Livre (SBPO 2026).
Todos os registros arquiteturais, descobertas matemáticas e especificações do desafio estão organizados abaixo sob o prefixo `MEMO_`, seguindo nossas diretrizes de governança.

## 📖 Especificações Básicas do Desafio
- [MEMO_01: O Problema](MEMO_01_problema.md) — Visão geral da operação logística.
- [MEMO_02: O Desafio](MEMO_02_desafio.md) — Regras de submissão e escopo.
- [MEMO_03: Função Objetivo](MEMO_03_funcao_objetivo.md) — Detalhamento da métrica de densidade fracionária (itens por corredor).
- [MEMO_04: Instâncias](MEMO_04_instancias.md) — Estrutura e tamanho dos datasets (A, B e X).
- [MEMO_05: Validação](MEMO_05_validacao.md) — Critérios de viabilidade de uma wave.

## 🔬 Pesquisa e Descobertas (V4)
- [MEMO_06: Descobertas Docker & CPLEX](MEMO_06_descobertas_docker.md) — Registro sobre a infraestrutura CUDA e como o limite da licença *Community* do CPLEX prova a inviabilidade do modelo "cru".
- [MEMO_07: Análise do Repositório 2025](MEMO_07_analise_meli_2025.md) — Investigação profunda sobre os vencedores do SBPO 2025 e por que a redução de escopo (nossa arquitetura de GPU) é a estratégia campeã.
- [MEMO_08: Resumo da Pesquisa](MEMO_08_resumo_pesquisa.md) — Visão geral da pesquisa, abrangendo a implementação da GPU.
- [MEMO_09: SA vs Busca Tabu](MEMO_09_porque_nao_usamos_mais_SA.md) — Justificativa técnica detalhando a substituição do Simulated Annealing pela Busca Tabu como baseline de comparação.
- [MEMO_10: Estudo Pormenorizado dos Artigos de 2025](MEMO_10_estudo_papers_2025.md) — Análise técnica das obras de Santos & Baldotto e Leal et al., e como a V4 supera as limitações destas abordagens originais.
- [MEMO_11: Estudo Rasmi et al. (2022)](MEMO_11_estudo_rasmi_2022.md) — Análise técnica do artigo internacional sobre a estratégia de armazenamento mixed-shelves (MSSS).
- [MEMO_12: Confronto e Avaliação Bibliográfica](MEMO_12_avaliacao_confronto_pesquisa.md) — Estudo comparativo e estratégico demonstrando a superioridade da V4 contra a literatura de 2025.
- [MEMO_13: O Resuminho (Explicação Simples)](MEMO_13_resuminho.md) — Visão geral lúdica e conceitual do projeto, detalhando o problema, o filtro de GPU e os resultados em linguagem simples.
- [MEMO_14: Plano de Implementação](MEMO_14_implementation_plan.md) — O plano de reestruturação do pipeline de otimização em módulos.
- [MEMO_15: Checklist de Execução](MEMO_15_task.md) — Acompanhamento detalhado do progresso das tarefas de desenvolvimento.

---
*Indexador atualizado automaticamente. Use estes links para navegar pela teoria antes de alterar a implementação.*
