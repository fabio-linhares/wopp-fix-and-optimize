# Comparação com a Literatura (Literature Comparison)

Este diretório contém os scripts de benchmark e experimentos voltados para a validação dos resultados contra a literatura científica e os artigos publicados na área (ex: Leal et al., 2025).

## 📄 Scripts Disponíveis

### 1. `compare_b08_to_literature.py`
Executa o benchmark em loop contínuo até atingir o limite de tempo literário de **589 segundos** na instância **B08** completa (12.334 pedidos).
- **Redução:** Ativa a redução matheurística original via GPU.
- **Fallbacks:** Em caso de limite de licença do CPLEX (Ex: Community Edition), utiliza automaticamente o solver **CBC** multi-threaded de fallback para garantir uma resolução de alta performance e viável.
- **Saída:** Grava o histórico detalhado em `results/modulo_4/loop_benchmark_results.csv`.

#### Como Executar:
```bash
python literature_comparison/compare_b08_to_literature.py
```

---

### 2. `compare_modulo4_to_literature.py`
Executa a suíte de experimentos experimentais (configurações C1 e C2) em instâncias específicas contra a literatura.
- **Saída:** Grava e consolida os resultados em `results/modulo_4/experiments.csv`.

#### Como Executar:
```bash
python literature_comparison/compare_modulo4_to_literature.py
```

## 🗃️ Resultados e Métricas

Os resultados gerados por estes scripts alimentam os relatórios e comparativos salvos no diretório `results/modulo_4/`.
