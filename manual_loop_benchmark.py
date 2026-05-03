#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import csv

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import load_config
from src.models.problem import WaveOrderPickingProblem
from src.solvers.pli.pli_solver import PLISolver

def main():
    print("══════════════════════════════════════════════════════════════════════")
    print("  MANUAL LOOP BENCHMARK - EXECUÇÃO DIRETA NO TERMINAL (589s)")
    print("══════════════════════════════════════════════════════════════════════")

    config = load_config()
    instance_path = "datasets/b/instance_0008.txt"

    if not os.path.exists(instance_path):
        print(f"Erro: Instância não encontrada em {instance_path}")
        print("Certifique-se de executar na raiz do projeto.")
        return

    results_list = []
    start_all = time.time()
    max_duration = 589.0
    iteration = 1

    # Loop contínuo até atingir o limite de 589 segundos
    while (time.time() - start_all) < max_duration:
        current_elapsed = time.time() - start_all
        remaining_time = max_duration - current_elapsed

        if remaining_time <= 1:
            print("\nTempo limite de 589s praticamente atingido. Finalizando benchmark.")
            break

        print(f"\n[Iteração {iteration}] Tempo acumulado: {current_elapsed:.2f}s / {max_duration}s")
        
        # Ajusta o limite de tempo do solver de acordo com o tempo restante
        config['algorithm']['time_limit'] = min(120.0, remaining_time)

        problem = WaveOrderPickingProblem(config=config)
        problem.read_input(instance_path)

        solver = PLISolver(problem, config)
        start_step = time.time()
        solution = solver.solve(start_step)
        step_elapsed = time.time() - start_step

        official_metric = round(solution.objective_value or 0.0, 4) if solution else 0.0
        orders_selected = len(solution.selected_orders) if solution and solution.selected_orders else 0
        aisles_visited = len(solution.visited_aisles) if solution and solution.visited_aisles else 0

        results_list.append({
            'iteration': iteration,
            'elapsed_accumulated': round(time.time() - start_all, 2),
            'step_time': round(step_elapsed, 4),
            'n_orders': problem.n_orders,
            'n_aisles': problem.n_aisles,
            'selected_orders': orders_selected,
            'visited_aisles': aisles_visited,
            'ratio': official_metric
        })
        
        print(f"-> Concluído Iteração {iteration}: Ratio={official_metric} | Tempo do Passo={step_elapsed:.2f}s")
        
        iteration += 1

    output_path = "results/modulo_4/loop_benchmark_results.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
        writer.writeheader()
        writer.writerows(results_list)

    print(f"\n📄 Resultados reais do Loop Benchmark salvos em: {output_path}")

if __name__ == "__main__":
    main()
