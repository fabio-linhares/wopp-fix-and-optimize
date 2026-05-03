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
    print("  LOOP BENCHMARK REAL - INSTÂNCIA B08")
    print("══════════════════════════════════════════════════════════════════════")

    config = load_config()
    instance_path = "datasets/b/instance_0008.txt"

    if not os.path.exists(instance_path):
        print(f"Erro: Instância não encontrada em {instance_path}")
        return

    results_list = []
    start_all = time.time()
    
    # Execução do teste real 1: C2 com redução da GPU
    print("\n[Passo 1] Executando C2 com redução na GPU...")
    problem = WaveOrderPickingProblem(config=config)
    problem.read_input(instance_path)

    solver = PLISolver(problem, config)
    start_step = time.time()
    solution = solver.solve(start_step)
    step_elapsed = time.time() - start_step

    results_list.append({
        'iteration': 1,
        'elapsed_accumulated': round(time.time() - start_all, 2),
        'n_orders': problem.n_orders,
        'n_aisles': problem.n_aisles,
        'selected_orders': len(solution.selected_orders) if solution and solution.selected_orders else 0,
        'visited_aisles': len(solution.visited_aisles) if solution and solution.visited_aisles else 0,
        'ratio': round(solution.objective_value or 0.0, 4) if solution else 0.0
    })
    print(f"-> Passo 1 Concluído: Ratio={results_list[-1]['ratio']} em {step_elapsed:.2f}s")

    # Salvar resultados reais
    output_path = "results/modulo_4/loop_benchmark_results.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
        writer.writeheader()
        writer.writerows(results_list)

    print(f"\n📄 Resultados reais do Loop Benchmark salvos em: {output_path}")

if __name__ == "__main__":
    main()
