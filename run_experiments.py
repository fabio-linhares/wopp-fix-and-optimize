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

"""

Benchmark automatizado para o pipeline WOP (Wave Order Picking).

Executa todas as 35 instâncias (20 A + 15 B) com 6 configurações (C1–C6),
coleta métricas e salva os resultados em CSV.

Uso:
    python run_experiments.py                           # Roda tudo
    python run_experiments.py --config C1               # Apenas config C1
    python run_experiments.py --config C1 C2            # C1 e C2
    python run_experiments.py --instance a/instance_0001.txt  # Apenas uma instância
    python run_experiments.py --dataset a               # Apenas conjunto A
    python run_experiments.py --timeout 300              # Timeout 300s por instância
    python run_experiments.py --gpu-speedup             # Mede speedup GPU vs CPU
"""

import sys
import os
import time
import csv
import argparse
import copy
import glob
import traceback

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import load_config
from src.models.problem import WaveOrderPickingProblem
from src.utils.instance_reducer import InstanceReducer


# ═══════════════════════════════════════════════════════════════════
# Definição das configurações experimentais (conforme o plano atualizado)
# ═══════════════════════════════════════════════════════════════════

CONFIGURATIONS = {
    'C1': {
        'name': 'Inversa + Rígido + Σy≥1',
        'linearizer': 'inverse',
        'soft_constraints': False,
        'use_c0': False,
        'instance_reduction': True,
    },
    'C2': {
        'name': 'Inversa + Flexível + Σy≥1',
        'linearizer': 'inverse',
        'soft_constraints': True,
        'use_c0': False,
        'instance_reduction': True,
    },
    'C5': {
        'name': 'Dinkelbach + Rígido + Σy≥1',
        'linearizer': 'dinkelbach',
        'soft_constraints': False,
        'use_c0': False,
        'instance_reduction': True,
    },
    'C6': {
        'name': 'Dinkelbach + Flexível + Σy≥1',
        'linearizer': 'dinkelbach',
        'soft_constraints': True,
        'use_c0': False,
        'instance_reduction': True,
    },
    'C1_NoRed': {
        'name': 'Inversa + Rígido Sem Redução (Baseline)',
        'linearizer': 'inverse',
        'soft_constraints': False,
        'use_c0': False,
        'instance_reduction': False,
    },
    'C5_NoRed': {
        'name': 'Dinkelbach + Rígido Sem Redução (Baseline)',
        'linearizer': 'dinkelbach',
        'soft_constraints': False,
        'use_c0': False,
        'instance_reduction': False,
    },
}



def apply_config(base_config, experiment_cfg):
    """
    Aplica uma configuração experimental ao config base, sem modificar o original.

    Returns:
        dict: cópia do config com as alterações da configuração experimental.
    """
    config = copy.deepcopy(base_config)

    # Algorithm
    if 'algorithm' not in config:
        config['algorithm'] = {}
    config['algorithm']['linearizer'] = experiment_cfg['linearizer']
    if 'instance_reduction' in experiment_cfg:
        config['algorithm']['instance_reduction'] = str(experiment_cfg['instance_reduction']).lower()

    # Constraints
    if 'constraints' not in config:
        config['constraints'] = {}
    config['constraints']['soft_constraints'] = experiment_cfg['soft_constraints']

    # Objective
    if 'objective' not in config:
        config['objective'] = {}
    config['objective']['use_c0'] = experiment_cfg['use_c0']


    return config


def discover_instances(datasets_dir, dataset_filter=None, instance_filter=None):
    """
    Descobre todas as instâncias disponíveis.

    Args:
        datasets_dir: diretório base dos datasets
        dataset_filter: 'a', 'b', ou None para ambos
        instance_filter: caminho relativo de uma instância específica

    Returns:
        list of (dataset_name, instance_path) tuples, sorted
    """
    if instance_filter:
        # Instância específica
        full_path = os.path.join(datasets_dir, instance_filter)
        if not os.path.exists(full_path):
            full_path = instance_filter  # Pode ser caminho absoluto
        if os.path.exists(full_path):
            # Determinar dataset
            if '/a/' in full_path or full_path.startswith('a/'):
                ds = 'A'
            elif '/b/' in full_path or full_path.startswith('b/'):
                ds = 'B'
            else:
                ds = '?'
            return [(ds, full_path)]
        else:
            print(f"  ERRO: Instância não encontrada: {instance_filter}")
            return []

    instances = []
    for ds_name in ['a', 'b']:
        if dataset_filter and ds_name != dataset_filter.lower():
            continue
        ds_dir = os.path.join(datasets_dir, ds_name)
        if not os.path.isdir(ds_dir):
            continue
        for f in sorted(glob.glob(os.path.join(ds_dir, 'instance_*.txt'))):
            instances.append((ds_name.upper(), f))

    return instances


def run_single_experiment(instance_path, config, config_id, config_name, timeout):
    """
    Executa um único experimento (1 instância × 1 configuração).

    Returns:
        dict: resultado com todas as métricas coletadas
    """
    from src.solvers.pli.pli_solver import PLISolver

    instance_name = os.path.basename(instance_path)

    result = {
        'config_id': config_id,
        'config_name': config_name,
        'instance': instance_name,
        'instance_path': instance_path,
        'n_orders_original': 0,
        'n_aisles_original': 0,
        'n_orders_reduced': 0,
        'n_aisles_reduced': 0,
        'official_metric': 0.0,
        'n_selected_orders': 0,
        'n_visited_aisles': 0,
        'total_units': 0,
        'is_feasible': False,
        'solver_status': 'error',
        'time_total': 0.0,
        'time_reduction': 0.0,
        'time_solver': 0.0,
        'error': '',
    }

    try:
        # Carregar problema
        problem = WaveOrderPickingProblem(config=config)
        problem.read_input(instance_path)

        result['n_orders_original'] = problem.n_orders
        result['n_aisles_original'] = problem.n_aisles

        # Configurar timeout
        config_copy = copy.deepcopy(config)
        config_copy['algorithm']['max_runtime'] = timeout

        # Criar e executar solver
        solver = PLISolver(problem, config_copy)

        start = time.time()
        solution = solver.solve(start)
        elapsed = time.time() - start

        result['time_total'] = round(elapsed, 4)

        if solution and solution.selected_orders:
            result['n_selected_orders'] = len(solution.selected_orders)
            result['n_visited_aisles'] = len(solution.visited_aisles)
            result['total_units'] = solution.total_units
            result['official_metric'] = round(solution.objective_value or 0.0, 6)
            result['is_feasible'] = solution.is_feasible or False
            result['solver_status'] = 'optimal'
        else:
            result['solver_status'] = 'no_solution'

    except Exception as e:
        result['error'] = str(e)
        result['solver_status'] = 'error'
        traceback.print_exc()

    return result


def measure_gpu_speedup(instance_path, config):
    """
    Mede o speedup da redução de instância GPU vs CPU.

    Returns:
        dict: {gpu_time, cpu_time, speedup, n_orders, n_aisles}
    """
    problem = WaveOrderPickingProblem(config=config)
    problem.read_input(instance_path)

    result = {
        'instance': os.path.basename(instance_path),
        'n_orders': problem.n_orders,
        'n_aisles': problem.n_aisles,
        'gpu_time': None,
        'cpu_time': None,
        'speedup': None,
        'gpu_available': False,
        'error': '',
    }

    # Estimar memória necessária para a matriz de conflito:
    # expanded_i & expanded_j → (n_orders, n_orders, n_aisles) int8
    mem_bytes = problem.n_orders * problem.n_orders * problem.n_aisles
    mem_gb = mem_bytes / (1024**3)

    # Limites: 6 GB para GPU (8 GB VRAM menos overhead), 24 GB para CPU (32 GB RAM menos OS)
    GPU_MEM_LIMIT_GB = 6.0
    CPU_MEM_LIMIT_GB = 24.0

    # CPU
    if mem_gb > CPU_MEM_LIMIT_GB:
        print(f"  ⚠ Instância muito grande para redução CPU ({mem_gb:.1f} GB necessários) — pulando")
        result['error'] = f'CPU_OOM_estimated_{mem_gb:.1f}GB'
        return result

    reducer_cpu = InstanceReducer(use_gpu=False)
    kept_o_cpu, kept_a_cpu, timings_cpu = reducer_cpu.reduce(
        problem.orders, problem.aisles, problem.n_items, problem.order_units
    )
    result['cpu_time'] = round(timings_cpu.get('total', 0), 6)

    # GPU
    if mem_gb > GPU_MEM_LIMIT_GB:
        print(f"  ⚠ Instância muito grande para GPU ({mem_gb:.1f} GB) — apenas CPU")
        result['error'] = f'GPU_OOM_estimated_{mem_gb:.1f}GB'
        return result

    reducer_gpu = InstanceReducer(use_gpu=True)
    if reducer_gpu.use_gpu:
        result['gpu_available'] = True
        try:
            # Warm-up (JIT compilation)
            reducer_gpu.reduce(
                problem.orders, problem.aisles, problem.n_items, problem.order_units
            )
            # Timed run
            kept_o_gpu, kept_a_gpu, timings_gpu = reducer_gpu.reduce(
                problem.orders, problem.aisles, problem.n_items, problem.order_units
            )
            result['gpu_time'] = round(timings_gpu.get('total', 0), 6)
            if result['gpu_time'] > 0:
                result['speedup'] = round(result['cpu_time'] / result['gpu_time'], 2)
        except Exception as e:
            err_msg = str(e)
            if 'OutOfMemory' in err_msg or 'out of memory' in err_msg.lower():
                print(f"  ⚠ GPU OOM ({problem.n_orders} pedidos × {problem.n_aisles} corredores) — apenas CPU")
                result['gpu_time'] = None
                result['speedup'] = None
                result['error'] = 'GPU_OOM'
            else:
                print(f"  ⚠ GPU erro: {e}")
                result['error'] = str(e)
        finally:
            # Liberar memória GPU
            try:
                import cupy as cp
                cp.get_default_memory_pool().free_all_blocks()
            except Exception:
                pass
    else:
        print("  ⚠ GPU não disponível — apenas CPU")

    return result


def save_results_csv(results, output_path):
    """Salva resultados em CSV."""
    if not results:
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fieldnames = list(results[0].keys())
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n  📄 Resultados salvos em: {output_path}")


def print_results_table(results):
    """Imprime uma tabela formatada dos resultados."""
    try:
        from prettytable import PrettyTable
    except ImportError:
        # Fallback simples
        for r in results:
            print(f"  {r['config_id']:3s} | {r['instance']:20s} | "
                  f"obj={r['official_metric']:10.4f} | t={r['time_total']:7.2f}s | "
                  f"{r['solver_status']}")
        return

    table = PrettyTable()
    table.field_names = [
        'Config', 'Instância', 'Pedidos', 'Corredores',
        'Métrica', 'Tempo(s)', 'Status', 'Viável'
    ]
    table.align = 'r'
    table.align['Config'] = 'l'
    table.align['Instância'] = 'l'
    table.align['Status'] = 'l'

    for r in results:
        orders_str = f"{r['n_orders_original']}→{r['n_selected_orders']}"
        aisles_str = f"{r['n_aisles_original']}→{r['n_visited_aisles']}"
        table.add_row([
            r['config_id'],
            r['instance'],
            orders_str,
            aisles_str,
            f"{r['official_metric']:.4f}",
            f"{r['time_total']:.2f}",
            r['solver_status'],
            '✓' if r['is_feasible'] else '✗',
        ])

    print(table)


def print_summary(results):
    """Imprime estatísticas agregadas por configuração."""
    from collections import defaultdict

    by_config = defaultdict(list)
    for r in results:
        by_config[r['config_id']].append(r)

    print(f"\n{'='*70}")
    print(f"  RESUMO POR CONFIGURAÇÃO")
    print(f"{'='*70}")

    try:
        from prettytable import PrettyTable
        table = PrettyTable()
        table.field_names = [
            'Config', 'Nome', 'N', 'Métrica Média',
            'Métrica Med.', 'Tempo Médio', '% Ótimos', '% Viáveis'
        ]
        table.align = 'r'
        table.align['Config'] = 'l'
        table.align['Nome'] = 'l'

        for cfg_id in sorted(by_config.keys()):
            runs = by_config[cfg_id]
            metrics = [r['official_metric'] for r in runs if r['official_metric'] > 0]
            times = [r['time_total'] for r in runs]
            n_optimal = sum(1 for r in runs if r['solver_status'] == 'optimal')
            n_feasible = sum(1 for r in runs if r['is_feasible'])

            avg_metric = sum(metrics) / len(metrics) if metrics else 0
            sorted_metrics = sorted(metrics)
            med_metric = sorted_metrics[len(sorted_metrics)//2] if sorted_metrics else 0
            avg_time = sum(times) / len(times) if times else 0
            pct_optimal = n_optimal / len(runs) * 100 if runs else 0
            pct_feasible = n_feasible / len(runs) * 100 if runs else 0

            table.add_row([
                cfg_id,
                CONFIGURATIONS[cfg_id]['name'],
                len(runs),
                f"{avg_metric:.4f}",
                f"{med_metric:.4f}",
                f"{avg_time:.2f}s",
                f"{pct_optimal:.0f}%",
                f"{pct_feasible:.0f}%",
            ])

        print(table)
    except ImportError:
        for cfg_id in sorted(by_config.keys()):
            runs = by_config[cfg_id]
            metrics = [r['official_metric'] for r in runs if r['official_metric'] > 0]
            avg = sum(metrics) / len(metrics) if metrics else 0
            print(f"  {cfg_id}: {len(runs)} runs, avg metric={avg:.4f}")


def print_gpu_speedup_table(speedup_results):
    """Imprime tabela de speedup GPU vs CPU."""
    print(f"\n{'='*70}")
    print(f"  SPEEDUP GPU vs CPU (Redução de Instância)")
    print(f"{'='*70}")

    try:
        from prettytable import PrettyTable
        table = PrettyTable()
        table.field_names = [
            'Instância', 'Pedidos', 'Corredores',
            'CPU (s)', 'GPU (s)', 'Speedup'
        ]
        table.align = 'r'
        table.align['Instância'] = 'l'

        for r in speedup_results:
            cpu_str = f"{r['cpu_time']:.6f}" if r['cpu_time'] is not None else 'N/A'
            gpu_str = f"{r['gpu_time']:.6f}" if r['gpu_time'] is not None else 'N/A'
            spd_str = f"{r['speedup']:.2f}x" if r['speedup'] is not None else 'N/A'
            err_str = r.get('error', '')
            if err_str:
                spd_str = err_str
            table.add_row([
                r['instance'],
                r['n_orders'],
                r['n_aisles'],
                cpu_str,
                gpu_str,
                spd_str,
            ])

        print(table)
    except ImportError:
        for r in speedup_results:
            print(f"  {r['instance']}: CPU={r['cpu_time']:.6f}s, "
                  f"GPU={r.get('gpu_time', 'N/A')}s, speedup={r.get('speedup', 'N/A')}")


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def _run_experiment_wrapper(args):
    # Desempacotar argumentos para o ProcessPoolExecutor
    idx, total, inst_path, ds_name, config, cfg_id, cfg_name, timeout = args
    inst_name = os.path.basename(inst_path)
    
    print(f"  [{idx}/{total}] Iniciando: {cfg_id} | [{ds_name}] {inst_name}")
    
    result = run_single_experiment(
        inst_path, config, cfg_id, cfg_name, timeout
    )
    result['dataset'] = ds_name
    
    # Imprimir progresso quando terminar
    metric = result['official_metric']
    status = result['solver_status']
    t = result['time_total']
    feasible = '✓' if result['is_feasible'] else '✗'
    print(f"  [{idx}/{total}] Concluído: {cfg_id} | {inst_name} → métrica={metric:.4f} | tempo={t:.2f}s | {status} | viável={feasible}")
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description='Benchmark automatizado WOP — 6 configurações × 35 instâncias'
    )
    parser.add_argument(
        '--config', nargs='+', choices=list(CONFIGURATIONS.keys()),
        help='Configurações a testar (ex: C1 C2). Default: todas.'
    )
    parser.add_argument(
        '--instance', type=str, default=None,
        help='Instância específica (ex: a/instance_0001.txt)'
    )
    parser.add_argument(
        '--dataset', choices=['a', 'b'],
        help='Filtrar por dataset (a ou b). Default: ambos.'
    )
    parser.add_argument(
        '--timeout', type=int, default=600,
        help='Timeout por instância em segundos (default: 600)'
    )
    parser.add_argument(
        '--gpu-speedup', action='store_true',
        help='Medir speedup GPU vs CPU na redução de instância'
    )
    parser.add_argument(
        '--output', type=str, default='results/modulo_4/experiments.csv',
        help='Caminho do CSV de saída (default: results/modulo_4/experiments.csv)'
    )
    parser.add_argument(
        '--workers', type=int, default=1,
        help='Número de processos paralelos (default: 1)'
    )

    args = parser.parse_args()

    # Carregar configuração base
    base_config = load_config('config.ini')

    # Descobrir instâncias
    datasets_dir = base_config.get('paths', {}).get('instances_dir', 'datasets')
    instances = discover_instances(datasets_dir, args.dataset, args.instance)

    if not instances:
        print("Nenhuma instância encontrada!")
        return

    # Configurações a testar
    config_ids = args.config or list(CONFIGURATIONS.keys())

    total_runs = len(instances) * len(config_ids)
    print(f"\n{'═'*70}")
    print(f"  BENCHMARK WOP — {len(instances)} instâncias × {len(config_ids)} configurações = {total_runs} execuções")
    print(f"  Timeout: {args.timeout}s por instância")
    print(f"  Solver: {base_config.get('algorithm', {}).get('solver', 'CBC')}")
    print(f"  Workers paralelos: {args.workers}")
    print(f"{'═'*70}\n")

    # ─── Medir speedup GPU vs CPU (opcional) ───
    if args.gpu_speedup:
        print(f"\n{'─'*70}")
        print(f"  MEDINDO SPEEDUP GPU vs CPU")
        print(f"{'─'*70}")

        speedup_results = []
        for ds_name, inst_path in instances:
            inst_name = os.path.basename(inst_path)
            print(f"\n  [{ds_name}] {inst_name}...")
            result = measure_gpu_speedup(inst_path, base_config)
            speedup_results.append(result)

        print_gpu_speedup_table(speedup_results)

        # Salvar CSV de speedup
        speedup_csv = args.output.replace('.csv', '_gpu_speedup.csv')
        save_results_csv(speedup_results, speedup_csv)

    # ─── Preparar tarefas ───
    tasks = []
    run_count = 0
    for cfg_id in config_ids:
        cfg = CONFIGURATIONS[cfg_id]
        config = apply_config(base_config, cfg)
        for ds_name, inst_path in instances:
            run_count += 1
            tasks.append((
                run_count, total_runs, inst_path, ds_name, 
                config, cfg_id, cfg['name'], args.timeout
            ))

    # ─── Executar experimentos ───
    all_results = []
    import concurrent.futures
    import multiprocessing

    if args.workers > 1:
        print(f"  Iniciando execução paralela com {args.workers} workers...")
        mp_context = multiprocessing.get_context('spawn')
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers, mp_context=mp_context) as executor:
            # Usar map para manter alguma ordem se possível, ou list(executor.map)
            all_results = list(executor.map(_run_experiment_wrapper, tasks))
    else:
        for t in tasks:
            all_results.append(_run_experiment_wrapper(t))

    # Ordenar resultados pelo ID original para manter a consistência da saída
    # Não estritamente necessário já que list(map) mantém a ordem das tasks

    # ─── Resultados ───
    print(f"\n\n{'═'*70}")
    print(f"  RESULTADOS COMPLETOS")
    print(f"{'═'*70}")

    print_results_table(all_results)
    print_summary(all_results)

    # Salvar CSV
    save_results_csv(all_results, args.output)

    # Resumo final
    total_time = sum(r['time_total'] for r in all_results)
    n_feasible = sum(1 for r in all_results if r['is_feasible'])
    n_optimal = sum(1 for r in all_results if r['solver_status'] == 'optimal')
    print(f"\n  Tempo total acumulado: {total_time:.2f}s ({total_time/60:.1f}min)")
    print(f"  Soluções ótimas: {n_optimal}/{len(all_results)}")
    print(f"  Soluções viáveis: {n_feasible}/{len(all_results)}")


if __name__ == '__main__':
    main()
