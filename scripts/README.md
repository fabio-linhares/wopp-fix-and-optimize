# 📜 Scripts de Execução e Automação

Este diretório contém os scripts principais de automação, execução de experimentos e benchmark contínuo do projeto **WOPP (SBPO 2026)**.

---

## 📁 Scripts Disponíveis

### 1. `scripts/run_experiments.py`
Roda os experimentos principais da matheurística em múltiplas configurações (ex: C1, C2) salvando os dados e tempos em CSV.

### 2. `scripts/run_loop_benchmark.py`
Executa o teste de benchmark de 589 segundos contra a literatura em loop contínuo para o backlog de pedidos residuais.

### 3. `scripts/run_tests.py`
Orquestrador interativo para execução simplificada dos testes pytest do projeto.

---

## 🚀 Como Executar
Navegue até a raiz do projeto e execute qualquer script usando o ambiente conda:
```bash
PYTHONPATH=. conda run -n wop python scripts/run_experiments.py --help
```
