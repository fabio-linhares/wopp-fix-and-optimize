# Explicação da Suíte de Testes: Módulo 5 (Artigo Científico e Documentação)

Este documento detalha os testes unitários criados para validar a finalização, corretude das tabelas e a indexação dos memorandos de governança do projeto WOPP.

---

## 1. `test_docs_presence` (Documentos e Indexação)
- **Razão de ser:** Garante que os novos memorandos de governança criados (`MEMO_16` e `MEMO_17`) e o arquivo de índice mestre da base de conhecimento (`index.md`) estão presentes e válidos no diretório `docs/`.
- **O que valida:** 
  - Presença dos arquivos markdown de documentação estrutural do projeto.

---

## 2. `test_results_presence` (Consolidação das Tabelas)
- **Razão de ser:** Valida a existência do diretório de resultados onde os benchmarks contínuos e os experimentos contra a literatura foram gerados.
- **O que valida:**
  - A integridade dos diretórios de saída onde as métricas oficiais do artigo foram exportadas (`results/modulo_4/`).

---

## 3. `test_removal_of_residual_column` (Limpeza da Tabela 4)
- **Razão de ser:** Certifica que a coluna residual de configurações descontinuadas (`c_0=1`) foi corretamente removida ou ajustada nos planos de implementação do projeto.
- **O que valida:**
  - Garante que a narrativa de desenvolvimento está alinhada com as orientações finais de revisão.

---

## 💡 Significado do Percentual nos Resultados do Pytest

Nos relatórios de execução gerados pelo framework `pytest` (como `module_5_tests.txt`), aparecem marcadores de percentual ao lado de cada linha de teste (Ex: `[ 33%]`, `[100%]`).

- **O que este percentual significa:** Ele representa o **progresso de execução** da bateria de testes em relação ao total de testes coletados, e **não** o percentual de sucesso do teste individual.
- **Por que é aceitável:** Se o teste exibe `PASSED` ao lado do percentual de progresso, significa que ele passou com **100% de sucesso**. O `[100%]` exibido na última linha simplesmente indica que todos os testes daquela sessão foram executados até o final.
