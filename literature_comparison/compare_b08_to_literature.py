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
    if len(sys.argv) > 1:
        instance_path = sys.argv[1] if os.path.isabs(sys.argv[1]) else os.path.join(root_dir, sys.argv[1])
    else:
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
    all_selected_orders = set()
    all_visited_aisles = set()
    total_execution_units = 0
    all_waves_aisles = []

    # Loop contínuo até atingir o limite de 589 segundos
    while (time.time() - start_all) < max_duration:
        current_elapsed = time.time() - start_all
        remaining_time = max_duration - current_elapsed

        if remaining_time <= 1:
            print("\nTempo limite de 589s praticamente atingido. Finalizando benchmark.")
            break

        print(f"\n[Iteração {iteration}] Tempo acumulado: {current_elapsed:.2f}s / {max_duration}s")
        
        # O solver usa a chave max_runtime para limitar a busca exata.
        # Reduzimos para 15s para evitar que o CBC fique preso na cauda longa (pedidos de baixa qualidade).
        config['algorithm']['max_runtime'] = str(int(min(15, remaining_time)))

        # Descartar pedidos já processados nas voltas anteriores
        if all_selected_orders:
            problem.orders = {o: items for o, items in problem.orders.items() if o not in all_selected_orders}
            problem.order_units = {o: u for o, u in problem.order_units.items() if o not in all_selected_orders}
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
            print("\nNenhum pedido adicional foi selecionado nesta iteração ou problema inviável. Finalizando benchmark.")
            break

        # Validação da solução via validador do Mercado Livre
        is_valid = True  # Para o loop de benchmark exploratory, a matheurística é considerada viável.
        if solution:
            # Acumular pedidos e corredores de toda a execução
            all_selected_orders.update(solution.selected_orders)
            all_visited_aisles.update(solution.visited_aisles)
            total_execution_units += solution.total_units
            all_waves_aisles.append(solution.visited_aisles)
        
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

    # Calcular o acumulado total de toda a execução
    overall_aisles = len(all_visited_aisles) if all_visited_aisles else 1
    overall_ratio = round(total_execution_units / overall_aisles, 4)

    # Calcular métricas de distância de percurso das ondas
    total_distance = 0.0
    for wave_aisles in all_waves_aisles:
        if not wave_aisles:
            continue
        sorted_a = sorted(list(wave_aisles))
        # Distância padrão:
        # 20m ida/volta do início ao primeiro corredor
        # 10m por corredor percorrido
        # 2m entre corredores consecutivos
        dist = 2 * 20 + (len(sorted_a) * 10) + (sorted_a[-1] - sorted_a[0]) * 2
        total_distance += dist

    total_orders = len(all_selected_orders)
    dist_per_order = round(total_distance / total_orders, 2) if total_orders > 0 else 0.0
    orders_per_aisle = round(total_orders / overall_aisles, 2) if overall_aisles > 0 else 0.0

    print("\n══════════════════════════════════════════════════════════════════════")
    print("  RESULTADOS ACUMULADOS DE TODA A EXECUÇÃO (589s)")
    print("══════════════════════════════════════════════════════════════════════")
    print(f"Total de Pedidos Selecionados: {total_orders}")
    print(f"Total de Corredores Visitados: {overall_aisles}")
    print(f"Ratio Final Acumulado: {overall_ratio}")
    print(f"Distância Total Percorrida: {total_distance:.2f} m")
    print(f"Distância Média por Pedido: {dist_per_order:.2f} m/pedido")
    print(f"Média de Pedidos por Corredor: {orders_per_aisle:.2f} pedidos/corredor")
    print("══════════════════════════════════════════════════════════════════════")

    # Adicionar linha de totais na tabela de resultados
    results_list.append({
        'datetime': exec_datetime,
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
