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

---

## 🎓 Ensinamento Prático: Como Interpretar e Executar os Testes

Para obter o máximo de rigor acadêmico e reprodutibilidade ao rodar os testes neste diretório, siga os seguintes princípios e passos de execução:

### 💡 1. Entendendo os Solvers (CPLEX vs CBC)
O script de benchmark para a instância B08 testa a disponibilidade do solver exato **CPLEX**. 
- Se a sua máquina tiver o **CPLEX com licença comercial ativa**, ele será utilizado com toda a capacidade multi-threaded do seu processador.
- Se o CPLEX contratado em sua máquina for a **Community Edition**, ele possui um limite estrito de até **1.000 variáveis**. Como a sub-instância de B08 pós-redução de GPU ainda contém mais variáveis do que esse teto, o script ativa um **fallback inteligente para o solver CBC**.
- O solver **CBC** é gratuito, de código aberto, e foi configurado para utilizar **100% dos núcleos e threads** da sua CPU (ex: 20 threads), garantindo que a resolução termine de forma ótima e no menor tempo possível sem comprometer a integridade dos dados!

### ⚙️ 2. Execução Passo a Passo no Terminal
Certifique-se sempre de estar com o ambiente Conda ou virtual ativado (`wop`) antes de executar os comandos:

```bash
# 1. Ative seu ambiente Python
conda activate wop

# 2. Navegue até a raiz do projeto
cd "/home/zerocopia/Downloads/sbpo 2026/Projeto_MercadoLivre_v4"

# 3. Execute o benchmark de B08 para comparação com o ótimo literário
python literature_comparison/compare_b08_to_literature.py

# 4. Execute a suíte de experimentos das configurações C1 e C2
python literature_comparison/compare_modulo4_to_literature.py
```

### 🔬 3. O que os Resultados Dizem?
Após a execução dos comandos acima, você verá saídas organizadas em tabelas diretamente no terminal e nos arquivos CSV em `results/modulo_4/`.
- **Ratio (Métrica Oficial):** Quanto maior o ratio (produtividade), melhor é a onda montada pela sua matheurística. Compare o Ratio Final Acumulado gerado pelo seu algoritmo contra o Ratio da literatura (ex: 227.1).
- **Tempo do Passo (Step Time):** O tempo total de execução deve ser comparado contra o tempo máximo de 589 segundos dos artigos. Se o seu algoritmo atinge ratios competitivos em frações de tempo menores, a matheurística é considerada um sucesso estrondoso!
