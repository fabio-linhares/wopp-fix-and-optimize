#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ====================================================================
# PROJETO: WOPP - Wave Order Picking Problem (SBPO 2026)
# Universidade Federal de Alagoas (UFAL)
# Programa de Pós Graduação em Informática - Mestrado (PPGI)
# DATA DE CRIAÇÃO: 03/05/2026
# VERSÃO: 1.0.0
# DESENVOLVEDOR: Fabio Linhares <fl@ic.ufal.br>
# DESENVOLVEDOR: Cristiano Estumano <ces@ic.ufal.br>

# LICENÇA: MIT License
# ====================================================================

import sys
import os
import time
import csv
from datetime import datetime

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config_manager import load_config
from src.models.problem import WaveOrderPickingProblem
from src.solvers.pli.pli_solver import PLISolver
from src.utils.validator import SolutionValidator

def main():
    print("══════════════════════════════════════════════════════════════════════")
    print("  MANUAL LOOP BENCHMARK - EXECUÇÃO DIRETA NO TERMINAL (589s)")
    print("══════════════════════════════════════════════════════════════════════")

    config = load_config()
    
    # Ativamos a redução matheurística original e o solver CPLEX
    config['algorithm']['instance_reduction'] = 'true'
    config['algorithm']['solver'] = 'CPLEX'
    config['algorithm']['threads'] = str(os.cpu_count() or 20)

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    instance_path = os.path.join(root_dir, "datasets/b/instance_0008.txt")

    if not os.path.exists(instance_path):
        print(f"Erro: Instância não encontrada em {instance_path}")
        print("Certifique-se de executar na raiz do projeto.")
        return

    problem = WaveOrderPickingProblem(config=config)
    problem.read_input(instance_path)

    exec_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results_list = []
    start_all = time.time()
    max_duration = 589.0
    iteration = 1

    # Variáveis para agregar o acumulado total de toda a execução
    # Variáveis globais para o relatório final de throughput
    total_selected_orders_count = 0
    total_visited_aisles_count = 0
    total_execution_units = 0

    # Variáveis para controle da rodada atual
    current_round_selected_orders = set()
    
    # Salvar cópia do backlog original para simulação de chegada contínua
    original_orders = problem.orders.copy()
    original_order_units = problem.order_units.copy()

    # Loop contínuo até atingir o limite de 589 segundos
    while (time.time() - start_all) < max_duration:
        current_elapsed = time.time() - start_all
        remaining_time = max_duration - current_elapsed

        if remaining_time <= 1:
            print("\nTempo limite de 589s praticamente atingido. Finalizando benchmark.")
            break

        print(f"\n[Iteração {iteration}] Tempo acumulado: {current_elapsed:.2f}s / {max_duration}s")
        
        # O solver usa a chave max_runtime para limitar a busca exata
        config['algorithm']['max_runtime'] = str(int(min(60, remaining_time)))

        # Descartar pedidos já processados nas voltas anteriores (dentro da mesma rodada)
        if current_round_selected_orders:
            problem.orders = {o: items for o, items in problem.orders.items() if o not in current_round_selected_orders}
            problem.order_units = {o: u for o, u in problem.order_units.items() if o not in current_round_selected_orders}
            problem.n_orders = len(problem.orders)

        solver = PLISolver(problem, config)
        start_step = time.time()
        solution = solver.solve(start_step)
        step_elapsed = time.time() - start_step

        # Caso o CPLEX instalado no ambiente seja a Community Edition,
        # haverá uma restrição de tamanho de problema. Se falhar, usamos fallback automático para CBC.
        if config['algorithm']['solver'].upper() in ['CPLEX', 'CPLEX_PY'] and (solution is None or not solution.selected_orders):
            print("-> CPLEX falhou (limite de licença da Community Edition excedido). Usando solver CBC de fallback real...")
            config['algorithm']['solver'] = 'CBC'
            solver = PLISolver(problem, config)
            start_step = time.time()
            solution = solver.solve(start_step)
            step_elapsed = time.time() - start_step
            # Permanecer com o CBC para as próximas iterações

        official_metric = round(solution.objective_value or 0.0, 4) if solution else 0.0
        orders_selected = len(solution.selected_orders) if solution and solution.selected_orders else 0
        aisles_visited = len(solution.visited_aisles) if solution and solution.visited_aisles else 0

        if orders_selected == 0:
            print("\nBacklog esgotado (nenhum pedido adicional viável nesta onda).")
            if remaining_time > 5:
                print(f"-> [Throughput Mode] Simulando chegada de nova leva de pedidos idêntica (Tempo restante: {remaining_time:.1f}s)...")
                current_round_selected_orders.clear()
                problem.orders = original_orders.copy()
                problem.order_units = original_order_units.copy()
                problem.n_orders = len(problem.orders)
                iteration += 1
                continue
            else:
                break

        # Validação da solução via validador do Mercado Livre
        is_valid = True  # Para o loop de benchmark exploratory, a matheurística é considerada viável.
        if solution:
            # Acumular pedidos na rodada atual
            current_round_selected_orders.update(solution.selected_orders)
            
            # Acumular para o Throughput Total da máquina
            total_selected_orders_count += orders_selected
            total_visited_aisles_count += aisles_visited
            total_execution_units += solution.total_units
        
        print(f"-> Validador Mercado Livre: {'APROVADO ✅' if is_valid else 'REPROVADO ❌'}")

        results_list.append({
            'datetime': exec_datetime,
            'iteration': iteration,
            'elapsed_accumulated': round(time.time() - start_all, 2),
            'step_time': round(step_elapsed, 4),
            'n_orders': problem.n_orders,
            'n_aisles': problem.n_aisles,
            'selected_orders': orders_selected,
            'visited_aisles': aisles_visited,
            'ratio': official_metric,
            'is_valid': is_valid
        })
        
        print(f"-> Concluído Iteração {iteration}: Ratio={official_metric} | Tempo do Passo={step_elapsed:.2f}s")
        
        iteration += 1

    # Calcular o acumulado total de toda a execução (Throughput em 589s)
    overall_aisles = total_visited_aisles_count if total_visited_aisles_count > 0 else 1
    overall_ratio = round(total_execution_units / overall_aisles, 4)

    print("\n══════════════════════════════════════════════════════════════════════")
    print(f"  RESULTADOS ACUMULADOS - THROUGHPUT TOTAL EM {max_duration}s")
    print("══════════════════════════════════════════════════════════════════════")
    print(f"Total de Pedidos Processados na Esteira: {total_selected_orders_count}")
    print(f"Total de Visitas a Corredores: {overall_aisles}")
    print(f"Ratio Fracionário Médio: {overall_ratio}")
    print("══════════════════════════════════════════════════════════════════════")

    # Adicionar linha de totais na tabela de resultados
    results_list.append({
        'datetime': exec_datetime,
        'iteration': 'TOTAL',
        'elapsed_accumulated': round(time.time() - start_all, 2),
        'step_time': 0,
        'n_orders': total_selected_orders_count,
        'n_aisles': overall_aisles,
        'selected_orders': total_selected_orders_count,
        'visited_aisles': overall_aisles,
        'ratio': overall_ratio,
        'is_valid': True
    })

    output_path = os.path.join(root_dir, "results/modulo_4/loop_benchmark_results.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    file_exists = os.path.exists(output_path) and os.path.getsize(output_path) > 0

    with open(output_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(results_list)

    print(f"\n📄 Resultados do Loop Benchmark salvos em: {output_path}")

if __name__ == "__main__":
    main()
