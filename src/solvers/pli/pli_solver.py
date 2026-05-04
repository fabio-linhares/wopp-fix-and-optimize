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
Solver PLI (Programação Linear Inteira) para Wave Order Picking.

Implementa o pipeline do artigo:
  1. Redução de instância (GPU/CPU)
  2. Modelagem MILP via PuLP
  3. Resolução por CPLEX (ou fallback CBC)
  4. Reavaliação na métrica oficial

Suporta:
  - Linearização Inversa (McCormick) — uma chamada ao solver
  - Método de Dinkelbach — laço iterativo
  - Regime rígido e flexível

Nota metodológica: Nas configurações rígidas, a redução agressiva induz inviabilidade matemática do subproblema. Esse comportamento não caracteriza erro de implementação nem falha do algoritmo; ele indica que a redução heurística, ao remover parcela expressiva das variáveis candidatas, torna o subproblema remanescente incapaz de satisfazer todas as restrições originais. Esse diagnóstico motiva a avaliação do regime flexível.
"""

from src.solvers.base_solver import BaseSolver
from src.models.solution import WaveOrderPickingSolution
from src.utils.instance_reducer import InstanceReducer
from src.solvers.pli.linearizers.fraction_linearizer import (
    InverseLinearizer,
    DinkelbachSolver,
)
import os
import pulp
import time
import sys


class PLISolver(BaseSolver):
    """
    Solver MILP para Wave Order Picking.

    Integra redução de instância, modelagem e resolução conforme o artigo.
    """

    def __init__(self, problem, config=None):
        super().__init__(problem, config)

        # Configurações do solver
        algo_cfg = self.config.get('algorithm', {})
        self.solver_name = algo_cfg.get('solver', 'CPLEX')
        self.time_limit = int(algo_cfg.get('max_runtime', 600))
        self.use_gpu = algo_cfg.get('use_gpu', 'false')
        if isinstance(self.use_gpu, str):
            self.use_gpu = self.use_gpu.lower() == 'true'

        # Tipo de linearização: 'inverse' ou 'dinkelbach'
        self.linearizer_type = algo_cfg.get('linearizer', 'inverse')

        # Redução de instância
        self.do_reduction = algo_cfg.get('instance_reduction', 'true')
        if isinstance(self.do_reduction, str):
            self.do_reduction = self.do_reduction.lower() == 'true'

    def _create_solver_cmd(self, time_remaining):
        """
        Cria o solver PuLP com os parâmetros do protocolo experimental.

        Parâmetros fixos (artigo):
          - Threads: 19
          - FeasibilityTol: 10⁻⁶
          - OptimalityTol: 10⁻⁶
          - epgap: 0.01 (1%)
          - TimeLimit: tempo restante
        """
        time_limit_int = max(10, int(time_remaining))

        if self.solver_name.upper() in ['CPLEX', 'CPLEX_PY']:
            try:
                import cplex
                print("  Usando solver CPLEX via módulo Python (CPLEX_PY)")
                return pulp.CPLEX_PY(timeLimit=time_limit_int, msg=True)
            except ImportError:
                pass

            cplex_path = self.config.get('cplex', {}).get('path', '/opt/ibm/ILOG/CPLEX_Studio2212')
            cplex_exec = os.path.join(cplex_path, 'cplex', 'bin', 'x86-64_linux', 'cplex')

            if not os.path.exists(cplex_exec):
                cplex_exec = self._find_cplex()

            if cplex_exec and os.path.exists(cplex_exec):
                # Parâmetros do protocolo experimental
                cplex_options = [
                    f"set timelimit {time_limit_int}",
                    "set threads 19",
                    "set simplex tolerances feasibility 1e-6",
                    "set simplex tolerances optimality 1e-6",
                    "set mip tolerances mipgap 0.01",
                ]

                try:
                    from src.utils.check_solvers import is_nixos
                    if is_nixos():
                        from src.utils.check_solvers import NixOSCplexSolver
                        return NixOSCplexSolver(cplex_path, timeLimit=time_limit_int, msg=True)
                    else:
                        return pulp.CPLEX_CMD(
                            path=cplex_exec,
                            timeLimit=time_limit_int,
                            msg=True,
                            options=cplex_options,
                        )
                except Exception as e:
                    print(f"  CPLEX CMD falhou: {e}. Usando fallback.")

        # Fallback: CBC
        print(f"  Usando solver CBC (fallback)")
        import os
        num_threads = max(1, os.cpu_count() or 4)
        return pulp.PULP_CBC_CMD(timeLimit=time_limit_int, msg=False, threads=num_threads)

    def _find_cplex(self):
        """Procura executável CPLEX em locais comuns."""
        paths = [
            '/opt/ibm/ILOG/CPLEX_Studio2212/cplex/bin/x86-64_linux/cplex',
            '/opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex',
        ]
        env_path = os.environ.get('CPLEX_STUDIO_DIR', '')
        if env_path:
            paths.insert(0, os.path.join(env_path, 'cplex/bin/x86-64_linux/cplex'))

        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def solve(self, start_time=None):
        """
        Resolve o problema WOP com o pipeline completo.

        Returns:
            WaveOrderPickingSolution
        """
        start_time = start_time or time.time()
        p = self.problem

        print(f"\n{'='*60}")
        print(f"  PLI SOLVER — {self.linearizer_type.upper()}")
        print(f"  {p.n_orders} pedidos, {p.n_aisles} corredores, {p.n_items} itens")
        print(f"  LB={p.wave_size_lb}, UB={p.wave_size_ub}")
        print(f"  Regime: {self.config.get('constraints', {}).get('soft_constraints', 'false')}")
        print(f"  c₀: {self.config.get('objective', {}).get('use_c0', 'false')}")
        print(f"{'='*60}")

        # ─── Etapa 1: Redução de instância ───
        if self.do_reduction and p.n_orders > 10:
            try:
                reducer = InstanceReducer(use_gpu=self.use_gpu)
                kept_orders, kept_aisles, timings = reducer.reduce(
                    p.orders, p.aisles, p.n_items, p.order_units
                )
                reducer.print_report(p.n_orders, p.n_aisles, len(kept_orders), len(kept_aisles))
            except (MemoryError, Exception) as e:
                err_msg = str(e)
                if 'OutOfMemory' in err_msg or 'MemoryError' in type(e).__name__ or 'memory' in err_msg.lower():
                    # Liberar memória GPU
                    try:
                        import cupy as _cp
                        _cp.get_default_memory_pool().free_all_blocks()
                    except Exception:
                        pass

                    # Tentar com CPU (NumPy) como fallback
                    if self.use_gpu:
                        print(f"  ⚠ Redução GPU OOM ({p.n_orders} pedidos) — tentando CPU...")
                        try:
                            reducer_cpu = InstanceReducer(use_gpu=False)
                            kept_orders, kept_aisles, timings = reducer_cpu.reduce(
                                p.orders, p.aisles, p.n_items, p.order_units
                            )
                            reducer_cpu.print_report(p.n_orders, p.n_aisles, len(kept_orders), len(kept_aisles))
                        except Exception as e2:
                            print(f"  ⚠ Redução CPU também falhou: {e2} — sem redução")
                            kept_orders = list(range(p.n_orders))
                            kept_aisles = list(range(p.n_aisles))
                    else:
                        print(f"  ⚠ Redução OOM ({p.n_orders} pedidos) — sem redução")
                        kept_orders = list(range(p.n_orders))
                        kept_aisles = list(range(p.n_aisles))
                else:
                    print(f"  ⚠ Erro na redução: {e} — sem redução")
                    kept_orders = list(range(p.n_orders))
                    kept_aisles = list(range(p.n_aisles))
        else:
            kept_orders = list(range(p.n_orders))
            kept_aisles = list(range(p.n_aisles))

        # Verificar tempo
        elapsed = time.time() - start_time
        remaining = self.time_limit - elapsed
        if remaining < 1:
            print("  Timeout após redução de instância")
            return p.create_solution([], [])

        # ─── Etapa 2: Modelagem e resolução ───
        if self.linearizer_type == 'dinkelbach':
            solution = self._solve_dinkelbach(kept_orders, kept_aisles, remaining, start_time)
        else:
            solution = self._solve_inverse(kept_orders, kept_aisles, remaining, start_time)

        # ─── Etapa 3: Reavaliação na métrica oficial ───
        if solution and solution.selected_orders and solution.visited_aisles:
            official_obj = self._official_metric(solution)
            print(f"\n  Métrica oficial (Σ S_o·x_o / Σ y_a): {official_obj:.6f}")
            solution.set_objective_value(official_obj)

        total_time = time.time() - start_time
        print(f"  Tempo total: {total_time:.2f}s\n")

        return solution

    def _solve_inverse(self, kept_orders, kept_aisles, time_remaining, start_time):
        """Resolve usando linearização Inversa (McCormick)."""
        p = self.problem

        # Construir modelo
        model = pulp.LpProblem("WOP_Inverse", pulp.LpMaximize)

        # Variáveis de decisão (apenas para pedidos/corredores mantidos)
        x = {o: pulp.LpVariable(f"x_{o}", cat=pulp.LpBinary) for o in kept_orders}
        y = {a: pulp.LpVariable(f"y_{a}", cat=pulp.LpBinary) for a in kept_aisles}

        # Aplicar linearização
        linearizer = InverseLinearizer(p, self.config)
        model = linearizer.build(model, x, y)

        # Resolver
        solver_cmd = self._create_solver_cmd(time_remaining)

        try:
            t0 = time.time()
            model.solve(solver_cmd)
            solve_time = time.time() - t0

            status = model.status
            print(f"  Status: {pulp.LpStatus[status]}, Tempo solver: {solve_time:.2f}s")

            if status == pulp.constants.LpStatusOptimal:
                sel_orders = [o for o in kept_orders if pulp.value(x[o]) is not None and pulp.value(x[o]) > 0.5]
                vis_aisles = [a for a in kept_aisles if pulp.value(y[a]) is not None and pulp.value(y[a]) > 0.5]

                solution = p.create_solution(sel_orders, vis_aisles)
                solution.set_feasibility(self._is_solution_feasible(solution))
                return solution
            else:
                print(f"  Solução não ótima: {pulp.LpStatus[status]}")
                return p.create_solution([], [])

        except Exception as e:
            print(f"  Erro na resolução Inversa: {e}")
            return p.create_solution([], [])

    def _solve_dinkelbach(self, kept_orders, kept_aisles, time_remaining, start_time):
        """Resolve usando método iterativo de Dinkelbach."""
        p = self.problem

        # Criar solver de Dinkelbach com subproblema reduzido
        # Precisamos criar um sub-problema com apenas os pedidos/corredores mantidos
        dinkelbach = DinkelbachSolver(p, self.config)

        solver_cmd = self._create_solver_cmd(time_remaining)

        sel_orders, vis_aisles, obj_val, n_iters = dinkelbach.solve(
            solver_cmd, time_remaining, start_time
        )

        print(f"  Dinkelbach: {n_iters} iterações, obj={obj_val:.6f}")

        solution = p.create_solution(sel_orders, vis_aisles)
        solution.set_feasibility(self._is_solution_feasible(solution))
        return solution

    def _official_metric(self, solution):
        """
        Calcula a métrica oficial do desafio:  Σ S_o·x_o / Σ y_a
        SEM c₀, SEM penalidades.
        """
        p = self.problem
        total_units = sum(p.order_units.get(o, 0) for o in solution.selected_orders)
        n_aisles = len(solution.visited_aisles)
        if n_aisles == 0:
            return 0.0
        return total_units / n_aisles

    def _is_solution_feasible(self, solution):
        """Verifica viabilidade na formulação original (rígida)."""
        p = self.problem
        total_units = sum(p.order_units.get(o, 0) for o in solution.selected_orders)

        # Verificar LB/UB
        if total_units < p.wave_size_lb or total_units > p.wave_size_ub:
            return False

        # Verificar cobertura de itens
        for item in p.all_order_items:
            demand = sum(
                p.item_units_by_order.get(item, {}).get(o, 0)
                for o in solution.selected_orders
            )
            supply = sum(
                p.item_units_by_aisle.get(item, {}).get(a, 0)
                for a in solution.visited_aisles
            )
            if demand > supply:
                return False

        return True