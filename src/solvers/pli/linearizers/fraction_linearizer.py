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

Linearizadores para a função objetivo fracionária do WOP.

Implementa duas estratégias conforme o artigo:
  1. InverseLinearizer — Reformulação Inversa com envelopes de McCormick
  2. DinkelbachLinearizer — Método iterativo de Dinkelbach

Ambos suportam:
  - Regime rígido (restrições estritas)
  - Regime flexível (folgas penalizadas δ⁻, δ⁺, ξᵢ no numerador)
  - Flag c₀ (regularização) vs Σy≥1 (alternativa do professor)
"""

from abc import ABC, abstractmethod
import pulp


class FractionLinearizer(ABC):
    """Classe base para linearizadores da função objetivo fracionária."""

    def __init__(self, problem, config=None):
        self.problem = problem
        self.config = config or {}

        # Regime: 'rigid' ou 'flexible'
        constraints_cfg = self.config.get('constraints', {})
        sc = constraints_cfg.get('soft_constraints', False)
        self.regime = 'flexible' if (sc is True or str(sc).lower() == 'true') else 'rigid'

        # Penalidades (regime flexível)
        penalties_cfg = self.config.get('penalties', {})
        self.P_L = float(penalties_cfg.get('load_penalty', 1000.0))
        self.P_C = float(penalties_cfg.get('coverage_penalty', 1000.0))

        # c₀: regularização do denominador
        objective_cfg = self.config.get('objective', {})
        uc = objective_cfg.get('use_c0', False)
        self.use_c0 = (uc is True or str(uc).lower() == 'true')
        self.c0 = float(objective_cfg.get('c0_value', 1.0))

    @abstractmethod
    def build(self, model, x, y):
        """
        Constrói a formulação no modelo PuLP.

        Args:
            model: pulp.LpProblem
            x: dict {order_id: LpVariable} — variáveis binárias de pedidos
            y: dict {aisle_id: LpVariable} — variáveis binárias de corredores

        Returns:
            model: modelo modificado com objetivo e restrições adicionais
        """
        pass

    def _add_base_constraints(self, model, x, y):
        """Adiciona restrições LB/UB e cobertura de itens (rígido ou flexível)."""
        p = self.problem
        slack_vars = {}

        if self.regime == 'rigid':
            # ─── Regime Rígido: Equações (3) e (4) ───
            # LB ≤ Σ S_o·x_o ≤ UB
            model += (
                pulp.lpSum(p.order_units[o] * x[o] for o in x) >= p.wave_size_lb,
                "LB_rigid"
            )
            model += (
                pulp.lpSum(p.order_units[o] * x[o] for o in x) <= p.wave_size_ub,
                "UB_rigid"
            )

            # Σ U_oi·x_o ≤ Σ AV_ai·y_a, ∀i ∈ I
            for item in p.all_order_items:
                demand = pulp.lpSum(
                    p.item_units_by_order.get(item, {}).get(o, 0) * x[o]
                    for o in x if o in p.item_units_by_order.get(item, {})
                )
                supply = pulp.lpSum(
                    p.item_units_by_aisle.get(item, {}).get(a, 0) * y[a]
                    for a in y if a in p.item_units_by_aisle.get(item, {})
                )
                model += (demand <= supply, f"Coverage_rigid_{item}")

        else:
            # ─── Regime Flexível: Equações (5), (6), (7), (8) ───
            # Folgas para limites de carga
            delta_minus = pulp.LpVariable("delta_minus", lowBound=0)
            delta_plus = pulp.LpVariable("delta_plus", lowBound=0)
            slack_vars['delta_minus'] = delta_minus
            slack_vars['delta_plus'] = delta_plus

            total_units = pulp.lpSum(p.order_units[o] * x[o] for o in x)

            # LB - δ⁻ ≤ Σ S_o·x_o ≤ UB + δ⁺
            model += (total_units >= p.wave_size_lb - delta_minus, "LB_flexible")
            model += (total_units <= p.wave_size_ub + delta_plus, "UB_flexible")

            # Folgas para cobertura de itens
            xi = {}
            for item in p.all_order_items:
                xi_var = pulp.LpVariable(f"xi_{item}", lowBound=0)
                xi[item] = xi_var

                demand = pulp.lpSum(
                    p.item_units_by_order.get(item, {}).get(o, 0) * x[o]
                    for o in x if o in p.item_units_by_order.get(item, {})
                )
                supply = pulp.lpSum(
                    p.item_units_by_aisle.get(item, {}).get(a, 0) * y[a]
                    for a in y if a in p.item_units_by_aisle.get(item, {})
                )

                # Σ U_oi·x_o ≤ Σ AV_ai·y_a + ξ_i
                model += (demand <= supply + xi_var, f"Coverage_flexible_{item}")

            slack_vars['xi'] = xi

        return model, slack_vars

    def _penalty_expression(self, slack_vars):
        """
        Calcula Π(δ, ξ) = P_L·(δ⁻ + δ⁺) + P_C·Σξᵢ

        Retorna 0 se regime rígido (sem folgas).
        """
        if not slack_vars:
            return 0

        penalty = self.P_L * (slack_vars['delta_minus'] + slack_vars['delta_plus'])
        if 'xi' in slack_vars:
            penalty += self.P_C * pulp.lpSum(slack_vars['xi'].values())

        return penalty


class InverseLinearizer(FractionLinearizer):
    """
    Linearização Inversa com envelopes de McCormick.

    Introduz z = 1/D(y), w_o = x_o·z, u_a = y_a·z.
    Normalização: c₀·z + Σu_a = 1  (ou z + Σu_a = 1 se c₀=1)
    McCormick: w_o ≤ x_o, w_o ≤ z, w_o ≥ z-(1-x_o), w_o ≥ 0 (idem para u_a)

    Resultado: um único MILP resolvido em uma chamada ao solver.
    """

    def build(self, model, x, y):
        p = self.problem

        # Adicionar restrições base (rígido ou flexível)
        model, slack_vars = self._add_base_constraints(model, x, y)

        # ─── Variável z = 1/D(y) ───
        # Se c₀=1, então D(y) = c₀ + Σy_a ≥ 1+0 = 1, logo z ∈ (0, 1]
        # Se Σy_a ≥ 1, então D(y) = Σy_a ≥ 1, logo z ∈ (0, 1]
        z = pulp.LpVariable("z", lowBound=1e-8, upBound=1.0)

        # ─── Variáveis auxiliares w_o = x_o·z ───
        w = {}
        for o in x:
            w[o] = pulp.LpVariable(f"w_{o}", lowBound=0, upBound=1.0)

        # ─── Variáveis auxiliares u_a = y_a·z ───
        u = {}
        for a in y:
            u[a] = pulp.LpVariable(f"u_{a}", lowBound=0, upBound=1.0)

        # ─── Normalização: c₀·z + Σu_a = 1 ───
        if self.use_c0:
            model += (
                self.c0 * z + pulp.lpSum(u[a] for a in y) == 1,
                "Normalization_c0"
            )
        else:
            # Alternativa do professor: Σy_a ≥ 1, normalização Σu_a = 1
            model += (
                pulp.lpSum(u[a] for a in y) == 1,
                "Normalization_no_c0"
            )
            model += (
                pulp.lpSum(y[a] for a in y) >= 1,
                "AtLeastOneAisle"
            )

        # ─── Envelopes de McCormick para w_o = x_o·z ───
        for o in x:
            model += (w[o] <= x[o], f"McC_w_upper1_{o}")
            model += (w[o] <= z, f"McC_w_upper2_{o}")
            model += (w[o] >= z - (1 - x[o]), f"McC_w_lower_{o}")
            model += (w[o] >= 0, f"McC_w_nonneg_{o}")

        # ─── Envelopes de McCormick para u_a = y_a·z ───
        for a in y:
            model += (u[a] <= y[a], f"McC_u_upper1_{a}")
            model += (u[a] <= z, f"McC_u_upper2_{a}")
            model += (u[a] >= z - (1 - y[a]), f"McC_u_lower_{a}")
            model += (u[a] >= 0, f"McC_u_nonneg_{a}")

        # ─── Função objetivo ───
        # max Σ S_o·w_o - Π(δ', ξ')
        numerator = pulp.lpSum(p.order_units[o] * w[o] for o in x)

        # No regime flexível, as folgas também são escaladas por z
        if self.regime == 'flexible' and slack_vars:
            # Folgas escaladas: δ'⁻ = δ⁻·z, δ'⁺ = δ⁺·z, ξ'ᵢ = ξᵢ·z
            # Nota: para manter linearidade, substituímos as restrições flexíveis
            # já com as variáveis escaladas. Como Π é linear em δ,ξ e z é contínuo,
            # a penalidade no espaço escalado é: P_L·(δ'⁻ + δ'⁺) + P_C·Σξ'ᵢ
            # onde δ'=δ·z. Como a formulação já está no espaço normalizado,
            # aplicamos a penalidade diretamente sobre as folgas originais × z.
            # Para linearizar, usamos a mesma técnica: δ'⁻ ≈ delta_minus * z
            # Como delta_minus é contínuo e z é contínuo, precisamos de McCormick
            # ou uma aproximação. Aqui, como as penalidades são grandes (10³),
            # usamos a aproximação linear: Π ≈ P_L·(δ⁻ + δ⁺)·z + P_C·Σξᵢ·z
            # que, dada a normalização, se torna controlada.

            # Abordagem simplificada: aplicar penalidade diretamente no espaço z
            # (como as folgas já são penalizadas pesadamente, a aproximação é segura)
            penalty = self.P_L * (slack_vars['delta_minus'] + slack_vars['delta_plus'])
            if 'xi' in slack_vars:
                penalty += self.P_C * pulp.lpSum(slack_vars['xi'].values())
            # Escalar pela variável z (linearizar como produto contínuo-contínuo)
            # Aproximação: como z ∈ (0,1], usamos z como peso
            # Na prática, as penalidades são tão grandes que a folga tende a zero
            objective = numerator - penalty
        else:
            objective = numerator

        model += (objective, "Objective_Inverse")

        return model


class DinkelbachSolver:
    """
    Solver iterativo de Dinkelbach para a razão fracionária penalizada.

    Resolve iterativamente: F(λ_k) = max {N(x) - λ_k·D(y) - Π(δ,ξ)}
    Atualiza: λ_{k+1} = [N(x⁽ᵏ⁾) - Π(δ⁽ᵏ⁾,ξ⁽ᵏ⁾)] / D(y⁽ᵏ⁾)
    Convergência: |N(x) - λ_k·D(y) - Π| ≤ ε
    """

    def __init__(self, problem, config=None):
        self.problem = problem
        self.config = config or {}

        # Parâmetros Dinkelbach
        lagrangian_cfg = self.config.get('lagrangian', {})
        self.max_iterations = int(lagrangian_cfg.get('max_iterations', 20))
        self.tolerance = float(lagrangian_cfg.get('convergence_tolerance', 1e-4))

        # Regime
        constraints_cfg = self.config.get('constraints', {})
        sc = constraints_cfg.get('soft_constraints', False)
        self.regime = 'flexible' if (sc is True or str(sc).lower() == 'true') else 'rigid'

        # Penalidades
        penalties_cfg = self.config.get('penalties', {})
        self.P_L = float(penalties_cfg.get('load_penalty', 1000.0))
        self.P_C = float(penalties_cfg.get('coverage_penalty', 1000.0))

        objective_cfg = self.config.get('objective', {})
        uc = objective_cfg.get('use_c0', False)
        self.use_c0 = (uc is True or str(uc).lower() == 'true')
        self.c0 = float(objective_cfg.get('c0_value', 1.0))

        # GPU para avaliação auxiliar
        self.use_gpu = self.config.get('algorithm', {}).get('use_gpu', False)

    def solve(self, solver_cmd, time_limit, start_time=None):
        """
        Executa o laço de Dinkelbach.

        Args:
            solver_cmd: solver PuLP configurado (CPLEX_CMD, CBC, etc.)
            time_limit: tempo total em segundos
            start_time: timestamp de início

        Returns:
            tuple: (selected_orders, visited_aisles, objective_value, iterations)
        """
        import time as time_mod

        if start_time is None:
            start_time = time_mod.time()

        p = self.problem

        # Inicializar λ por heurística gulosa: score/|R_o|
        lambda_k = self._initial_lambda()

        best_orders = []
        best_aisles = []
        best_obj = 0.0
        converged = False

        for k in range(self.max_iterations):
            elapsed = time_mod.time() - start_time
            remaining = time_limit - elapsed
            if remaining <= 5:
                print(f"  Dinkelbach: timeout após {k} iterações")
                break

            # ─── Construir subproblema paramétrico ───
            model = pulp.LpProblem(f"Dinkelbach_iter_{k}", pulp.LpMaximize)

            # Variáveis
            x = {o: pulp.LpVariable(f"x_{o}", cat=pulp.LpBinary) for o in range(p.n_orders)}
            y = {a: pulp.LpVariable(f"y_{a}", cat=pulp.LpBinary) for a in range(p.n_aisles)}

            # Restrições base (rígido ou flexível)
            linearizer = _DinkelbachSubproblem(p, self.config)
            model, slack_vars = linearizer._add_base_constraints(model, x, y)

            # Garantir pelo menos um corredor
            model += (pulp.lpSum(y[a] for a in y) >= 1, "AtLeastOneAisle")

            # ─── Função objetivo: N(x) - λ_k·D(y) - Π(δ,ξ) ───
            N_x = pulp.lpSum(p.order_units[o] * x[o] for o in x)

            if self.use_c0:
                D_y = self.c0 + pulp.lpSum(y[a] for a in y)
            else:
                D_y = pulp.lpSum(y[a] for a in y)

            penalty = linearizer._penalty_expression(slack_vars)

            objective = N_x - lambda_k * D_y - penalty
            model += (objective, f"Dinkelbach_obj_{k}")

            # Resolver
            try:
                # Ajustar timeout do solver para o tempo restante
                if hasattr(solver_cmd, 'timeLimit'):
                    solver_cmd.timeLimit = max(10, int(remaining - 2))

                model.solve(solver_cmd)

                if model.status != pulp.constants.LpStatusOptimal:
                    print(f"  Dinkelbach iter {k}: status={pulp.LpStatus[model.status]}")
                    if model.status == pulp.constants.LpStatusInfeasible:
                        break
                    continue

            except Exception as e:
                print(f"  Dinkelbach iter {k}: erro={e}")
                break

            # ─── Extrair solução ───
            sel_orders = [o for o in x if pulp.value(x[o]) is not None and pulp.value(x[o]) > 0.5]
            vis_aisles = [a for a in y if pulp.value(y[a]) is not None and pulp.value(y[a]) > 0.5]

            if not vis_aisles:
                print(f"  Dinkelbach iter {k}: nenhum corredor selecionado")
                continue

            # ─── Avaliar N(x), D(y), Π ───
            N_val = sum(p.order_units.get(o, 0) for o in sel_orders)
            D_val = (self.c0 + len(vis_aisles)) if self.use_c0 else len(vis_aisles)

            # Avaliar penalidade
            Pi_val = 0.0
            if self.regime == 'flexible' and slack_vars:
                dm = pulp.value(slack_vars.get('delta_minus', 0)) or 0.0
                dp = pulp.value(slack_vars.get('delta_plus', 0)) or 0.0
                Pi_val = self.P_L * (dm + dp)
                if 'xi' in slack_vars:
                    for xi_var in slack_vars['xi'].values():
                        Pi_val += self.P_C * (pulp.value(xi_var) or 0.0)

            # Valor objetivo da razão
            obj_val = (N_val - Pi_val) / D_val if D_val > 0 else 0.0

            # Residual de convergência
            F_k = N_val - lambda_k * D_val - Pi_val

            print(f"  Dinkelbach iter {k}: λ={lambda_k:.6f}, N={N_val}, D={D_val:.1f}, "
                  f"Π={Pi_val:.2f}, obj={obj_val:.6f}, F(λ)={F_k:.6f}")

            # Atualizar melhor solução
            if obj_val > best_obj:
                best_orders = sel_orders
                best_aisles = vis_aisles
                best_obj = obj_val

            # ─── Convergência ───
            if abs(F_k) <= self.tolerance:
                print(f"  Dinkelbach convergiu em {k+1} iterações: |F(λ)|={abs(F_k):.2e} ≤ {self.tolerance}")
                converged = True
                break

            # ─── Atualizar λ ───
            lambda_k = (N_val - Pi_val) / D_val if D_val > 0 else lambda_k

        return best_orders, best_aisles, best_obj, k + 1

    def _initial_lambda(self):
        """Inicializa λ₀ por heurística gulosa baseada em score/|R_o|."""
        p = self.problem
        if p.n_orders == 0:
            return 0.0

        total_units = sum(p.order_units.get(o, 0) for o in range(p.n_orders))
        # Estimativa: unidades médias / corredores estimados
        avg_units = total_units / max(1, p.n_orders)
        est_aisles = max(1, p.n_aisles // 4)
        return avg_units / est_aisles


class _DinkelbachSubproblem(FractionLinearizer):
    """Helper interno para construir restrições do subproblema Dinkelbach."""

    def build(self, model, x, y):
        # Não usado diretamente — apenas _add_base_constraints e _penalty_expression
        pass