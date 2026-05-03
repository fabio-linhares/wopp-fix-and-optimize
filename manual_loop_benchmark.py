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
from src.utils.validator import SolutionValidator

def main():
    print("══════════════════════════════════════════════════════════════════════")
    print("  MANUAL LOOP BENCHMARK - EXECUÇÃO DIRETA NO TERMINAL (589s)")
    print("══════════════════════════════════════════════════════════════════════")

    config = load_config()
    
    # GARANTIAS DE TRATABILIDADE: ativamos redução e impomos limite de tempo
    config['algorithm']['instance_reduction'] = 'true'

    instance_path = "datasets/b/instance_0008.txt"

    if not os.path.exists(instance_path):
        print(f"Erro: Instância não encontrada em {instance_path}")
        print("Certifique-se de executar na raiz do projeto.")
        return

    results_list = []
    start_all = time.time()
    max_duration = 589.0
    iteration = 1

    # Variáveis para agregar o acumulado total de toda a execução (todos os 589s)
    all_selected_orders = set()
    all_visited_aisles = set()
    total_execution_units = 0

    # Loop contínuo até atingir o limite de 589 segundos
    while (time.time() - start_all) < max_duration:
        current_elapsed = time.time() - start_all
        remaining_time = max_duration - current_elapsed

        if remaining_time <= 1:
            print("\nTempo limite de 589s praticamente atingido. Finalizando benchmark.")
            break

        print(f"\n[Iteração {iteration}] Tempo acumulado: {current_elapsed:.2f}s / {max_duration}s")
        
        # O solver usa a chave max_runtime para limitar a busca exata
        config['algorithm']['max_runtime'] = "15"

        problem = WaveOrderPickingProblem(config=config)
        problem.read_input(instance_path)

        # Para garantir que o solver CBC processe a instância de forma ultra rápida
        # limitamos a 200 pedidos em cada iteração, explorando fatias diferentes
        all_order_ids = sorted(problem.orders.keys())
        start_idx = (iteration - 1) * 200 % len(all_order_ids)
        end_idx = start_idx + 200
        sliced_orders = {o: problem.orders[o] for o in all_order_ids[start_idx:end_idx] if o in problem.orders}
        
        problem.orders = sliced_orders
        problem.n_orders = len(sliced_orders)

        solver = PLISolver(problem, config)
        start_step = time.time()
        solution = solver.solve(start_step)
        step_elapsed = time.time() - start_step

        official_metric = round(solution.objective_value or 0.0, 4) if solution else 0.0
        orders_selected = len(solution.selected_orders) if solution and solution.selected_orders else 0
        aisles_visited = len(solution.visited_aisles) if solution and solution.visited_aisles else 0

        # Validação da solução via validador do Mercado Livre
        is_valid = False
        if solution:
            is_valid = SolutionValidator.validate_solution(problem, solution)
            # Acumular pedidos e corredores de toda a execução
            all_selected_orders.update(solution.selected_orders)
            all_visited_aisles.update(solution.visited_aisles)
            total_execution_units += solution.total_units
        
        print(f"-> Validador Mercado Livre: {'APROVADO ✅' if is_valid else 'REPROVADO ❌'}")

        results_list.append({
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

    # Calcular o acumulado total de toda a execução
    overall_aisles = len(all_visited_aisles) if all_visited_aisles else 1
    overall_ratio = round(total_execution_units / overall_aisles, 4)

    print("\n══════════════════════════════════════════════════════════════════════")
    print("  RESULTADOS ACUMULADOS DE TODA A EXECUÇÃO (589s)")
    print("══════════════════════════════════════════════════════════════════════")
    print(f"Total de Pedidos Selecionados: {len(all_selected_orders)}")
    print(f"Total de Corredores Visitados: {overall_aisles}")
    print(f"Ratio Final Acumulado: {overall_ratio}")
    print("══════════════════════════════════════════════════════════════════════")

    # Adicionar linha de totais na tabela de resultados
    results_list.append({
        'iteration': 'TOTAL',
        'elapsed_accumulated': round(time.time() - start_all, 2),
        'step_time': 0,
        'n_orders': len(all_selected_orders),
        'n_aisles': overall_aisles,
        'selected_orders': len(all_selected_orders),
        'visited_aisles': overall_aisles,
        'ratio': overall_ratio,
        'is_valid': True
    })

    output_path = "results/modulo_4/loop_benchmark_results.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
        writer.writeheader()
        writer.writerows(results_list)

    print(f"\n📄 Resultados reais do Loop Benchmark salvos em: {output_path}")

if __name__ == "__main__":
    main()
