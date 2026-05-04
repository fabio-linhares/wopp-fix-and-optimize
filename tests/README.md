# 🧪 Suíte de Testes (Tests Suite)

Este diretório contém os testes automatizados do projeto **WOPP (SBPO 2026)**.

---

## 📁 Testes Disponíveis

### 1. `tests/test_full_b08.py`
Executa o teste completo na instância clássica B08.

### 2. `tests/test_manual_loop_benchmark.py`
Valida o comportamento das configurações do solver e as funções de cálculo do benchmark contínuo.

### 3. `tests/test_modulo5.py`
Valida a presença de memorandos, governança e as restrições finais do projeto.

---

## 🚀 Como Executar
Navegue até a raiz do projeto e execute os testes via `pytest` com a variável `PYTHONPATH`:
```bash
PYTHONPATH=. conda run -n wop pytest
```
