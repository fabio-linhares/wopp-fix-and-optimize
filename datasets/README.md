# 📚 Detalhamento dos Datasets (WOPP - SBPO 2026)

Este diretório contém as instâncias reais utilizadas para testar e validar o pipeline de otimização *Fix-and-Optimize* no **Wave Order Picking Problem (WOPP)**.

Para garantir a portabilidade do projeto e respeitar os limites de tamanho de repositório, as instâncias completas não são enviadas para o GitHub, mas todas as suas especificações estão catalogadas abaixo.

---

## 📂 Visão Geral dos Grupos de Instâncias

O repositório está estruturado em 3 conjuntos (datasets) com diferentes graus de complexidade e dimensões:

### 1. Dataset A (Pequeno Porte)
* **Total de Instâncias:** 20 instâncias (`instance_0001.txt` a `instance_0020.txt`).
* **Características:** Instâncias de pequeno porte ideais para testes rápidos, validação de corretude do pipeline e benchmarking de exatidão.
* **Instância Menor:** `instance_0002.txt` ou `instance_0020.txt` (muito pequenas, apenas alguns pedidos).
* **Instância Maior:** `instance_0014.txt` (~353 KB).

### 2. Dataset B (Médio Porte)
* **Total de Instâncias:** 15 instâncias (`instance_0001.txt` a `instance_0015.txt`).
* **Características:** Conjunto clássico de médio porte para validar o método de Dinkelbach e a Reformulação Inversa.
* **Instância Menor:** `instance_0007.txt` (~57 KB).
* **Instância Maior:** `instance_0011.txt` (~2.25 MB).

### 3. Dataset X (Larga Escala - Massivo)
* **Total de Instâncias:** 15 instâncias (`instance_0001.txt` a `instance_0015.txt`).
* **Características:** Conjunto complexo de larga escala desenvolvido para testar a escalabilidade do algoritmo, a aceleração paralela por GPU e a robustez contra estouros de memória (OOM).
* **Instância Menor:** `instance_0002.txt` (~91 KB).
* **Instância Maior:** `instance_0014.txt` (~2.95 MB, contém 68.064 pedidos e 54.106 itens).

---

## 📄 Estrutura e Formato do Arquivo de Instância (`.txt`)

Os arquivos de instâncias seguem um formato de texto plano altamente otimizado e estruturado:

### 1. Linha de Cabeçalho (Linha 1)
Informa as dimensões globais do problema.
```text
[Número de Pedidos] [Número de Corredores] [Número de Itens]
```
*Exemplo:* `61 155 116` (61 pedidos, 155 corredores e 116 itens únicos).

### 2. Linhas de Pedidos e Corredores (Linha 2 até N-1)
As linhas subsequentes mapeiam o conteúdo de cada entidade.
* **Linhas 2 a `|O|+1`:** Representam as demandas dos pedidos.
* **Linhas `|O|+2` a `|O|+|A|+1`:** Representam o estoque dos corredores.

O formato de cada uma dessas linhas é:
```text
[N_Itens] [ID_Item_1] [Quantidade_1] [ID_Item_2] [Quantidade_2] ...
```
*Exemplo:* `3 13 1 36 1 135 1`
Indica que a entidade possui 3 itens distintos: o item 13 (1 unidade), o item 36 (1 unidade) e o item 135 (1 unidade).

### 3. Linha de Capacidade (Última Linha)
Informa as restrições operacionais da onda de pedidos.
```text
[Lower Bound (LB)] [Upper Bound (UB)]
```
*Exemplo:* `30 68`
Indica que a soma de todas as unidades dos pedidos selecionados na onda deve ser **no mínimo 30** e **no máximo 68**.

---

## 🧠 Como o Pipeline Processa as Instâncias

O pipeline de leitura unificado (`WaveOrderPickingProblem.read_input`):
1. Lê o cabeçalho para dimensionar as matrizes.
2. Faz o parsing sequencial na CPU para extrair o conteúdo de cada pedido e corredor.
3. Transfere os dados esparsos para a GPU em **chunks/partições** (lotes de 10.000 pedidos por vez) para as instâncias gigantes do Dataset X, evitando estouros de VRAM (`OutOfMemory`).
4. Aplica o filtro de dominância em GPU para remover variáveis irrelevantes e resolver o subproblema no solver exato a tempo.
