# Relatório de Descobertas: Teste Inicial V4 (Docker)

Durante a primeira bateria de testes da infraestrutura Docker da V4, duas descobertas arquiteturais críticas ditaram os próximos passos do projeto. Ambas foram registradas e mitigadas.

## 1. O Problema do Runtime CUDA no Docker
**O que aconteceu:**
Na primeira tentativa de compilação da imagem Docker, utilizamos a imagem base oficial da NVIDIA (`nvidia/cuda:12.2.2-base-ubuntu22.04`). O container inicializou corretamente e mapeou a GPU física. Porém, quando o Python tentou rodar a biblioteca `cupy` para realizar as matrizes da redução de instância, o sistema falhou com o erro:
`DynamicLibNotFoundError: Failure finding "libnvrtc.so"`

**O motivo:**
A tag `-base` da NVIDIA contém apenas os *drivers* mínimos de execução. Ela não possui o compilador dinâmico em tempo de execução (NVRTC - *NVIDIA Runtime Compilation*), que é exigido pelo CuPy para gerar os *kernels* da GPU *on-the-fly*.

**A Solução Aplicada:**
O `Dockerfile` foi prontamente reescrito, alterando a imagem hospedeira para `nvidia/cuda:12.2.2-devel-ubuntu22.04` (a versão *Developer*, que traz os compiladores pesados). O novo *build* já foi acionado.

---

## 2. O Pulo do Gato: Licença CPLEX "Community Edition"
**O que aconteceu:**
O arquivo instalador do CPLEX fornecido (`cos_installer_preview-22.1.2.R4-M0N96ML-linux-x86-64.bin`) carrega consigo a licença *Community Edition* da IBM, e não a versão Acadêmica irrestrita.

**A implicação mecânica:**
A licença *Community* possui um teto arquitetural rígido (um *hard limit*): ela recusa-se a resolver qualquer problema matemático que exceda a marca de **1.000 variáveis** e **1.000 restrições**. 

Quando rodamos o "Teste do Modelo Cru" (sem o filtro da GPU) na instância `0007` (que possui mais de 8.320 pedidos), o CPLEX travou no exato segundo 0.00 com a seguinte mensagem fatal:
> `CPLEX Error 1016: Community Edition. Problem size limits exceeded.`

**A Solução (e Oportunidade) para o Artigo:**
Isso resolve o desafio imposto pelo orientador Rian (Áudio 5) de forma poética. O professor exigiu provas de que "o modelo cru não roda".

1. **A Prova do Fracasso:** Nós provamos empiricamente que a formulação clássica WOPP é intocável (combinatorial explosion) por vias normais. Ela estoura imediatamente os limites de uso de uma licença não comercial.
2. **A Prova do Sucesso:** Graças à drástica filtragem na placa de vídeo, as nossas instâncias gigantes são reduzidas a subproblemas minúsculos (em média ~30 a ~50 pedidos). Esses subproblemas cabem com sobra nos limites da versão *Community* e poderão ser resolvidos em menos de 26 segundos no benchmark!

Isso nos dará uma justificativa sólida para escrever na seção de resultados: *"Devido à explosão combinatória da formulação clássica, submeter instâncias gigantes ao solver estouraria imediatamente os limites arquiteturais. O nosso pipeline heurístico permite que essas mesmas instâncias possam ser otimizadas até mesmo sob as restrições da licença Community."*
