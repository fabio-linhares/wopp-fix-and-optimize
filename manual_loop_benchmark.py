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
    print("  MANUAL LOOP BENCHMARK - EXECUÇÃO DIRETA NO TERMINAL")
    print("══════════════════════════════════════════════════════════════════════")

    config = load_config()
    # Forçamos uma configuração viável para demonstrar o benchmark
    config['algorithm']['time_limit'] = 180  # Limite por iteração para não demorar demais
    
    instance_path = "datasets/b/instance_0008.txt"

    if not os.path.exists(instance_path):
        print(f"Erro: Instância não encontrada em {instance_path}")
        print("Certifique-se de executar na raiz do projeto.")
        return

    results_list = []
    start_all = time.time()
    
    # 3 Iterações Reais
    for i in range(1, 4):
        print(f"\n[Iteração {i}/3] Carregando e resolvendo instância B08...")
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
            'iteration': i,
            'elapsed_accumulated': round(time.time() - start_all, 2),
            'step_time': round(step_elapsed, 4),
            'n_orders': problem.n_orders,
            'n_aisles': problem.n_aisles,
            'selected_orders': orders_selected,
            'visited_aisles': aisles_visited,
            'ratio': official_metric
        })
        
        print(f"-> Concluído Iteração {i}: Ratio={official_metric} | Tempo do Passo={step_elapsed:.2f}s")

    output_path = "results/modulo_4/loop_benchmark_results.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
        writer.writeheader()
        writer.writerows(results_list)

    print(f"\n📄 Resultados salvos com sucesso em: {output_path}")

if __name__ == "__main__":
    main()
