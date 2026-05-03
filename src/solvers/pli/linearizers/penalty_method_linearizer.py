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

from src.solvers.pli.linearizers.fraction_linearizer import FractionLinearizer
import pulp


class PenaltyMethodLinearizer(FractionLinearizer):
    """
    Implementa a linearização usando o método de penalidades.
    Adiciona termos de penalidade à função objetivo para penalizar violações de restrições.
    
    Este método é uma alternativa que pode ser usada tanto com o CPLEX quanto com heurísticas.
    """
    
    def __init__(self, problem, big_m=1000, penalty_weight=1000.0):
        """
        Inicializa o linearizador de método de penalidade.
        
        Args:
            problem: O problema a ser resolvido
            big_m: Valor para a constante big-M
            penalty_weight: Peso das penalidades na função objetivo
        """
        super().__init__(problem, big_m)
        self.penalty_weight = penalty_weight
    
    def apply(self, model, variables):
        """
        Aplica o método de penalidade ao modelo.
        
        Args:
            model: O modelo de PLI
            variables: Dicionário com as variáveis do modelo
            
        Returns:
            tuple: (modelo modificado, expressão da função objetivo)
        """
        # Extrair variáveis do modelo
        x = variables['x']  # Variáveis de seleção de pedidos
        y = variables['y']  # Variáveis de seleção de corredores
        
        # Inicializar com q = 0 (para compatibilidade com Dinkelbach)
        q_value = 0.0
        
        # Construir expressão da função objetivo base (como em Dinkelbach)
        base_objective = pulp.lpSum(
            self.problem.order_units[o] * x[o] for o in range(self.problem.n_orders)
        ) - q_value * pulp.lpSum(y[a] for a in range(self.problem.n_aisles))
        
        # Adicionar penalidades para violações de restrições
        penalties = self._calculate_penalties(model, x, y, variables)
        
        # Função objetivo final: base - penalidades
        objective_expr = base_objective - self.penalty_weight * penalties
        
        return model, objective_expr
    
    def _calculate_penalties(self, model, x, y, variables):
        """
        Calcula os termos de penalidade para as restrições.
        
        Args:
            model: O modelo de PLI
            x: Variáveis de seleção de pedidos
            y: Variáveis de seleção de corredores
            variables: Dicionário de todas as variáveis
        
        Returns:
            pulp.LpExpression: Expressão representando as penalidades
        """
        penalties = pulp.LpExpression()
        
        # 1. Penalidade para o limite inferior de unidades
        if hasattr(self.problem, 'wave_size_lb') and self.problem.wave_size_lb > 0:
            # Criar variável para medir a violação do limite inferior
            v_lb = pulp.LpVariable("violation_lb", lowBound=0)
            variables['v_lb'] = v_lb
            
            # Definir a violação: max(0, LB - soma das unidades)
            units_sum = pulp.lpSum(self.problem.order_units[o] * x[o] for o in range(self.problem.n_orders))
            model += v_lb >= self.problem.wave_size_lb - units_sum, "LB_violation"
            
            # Adicionar à penalidade total
            penalties += v_lb
        
        # 2. Penalidade para o limite superior de unidades
        if hasattr(self.problem, 'wave_size_ub') and self.problem.wave_size_ub < float('inf'):
            # Criar variável para medir a violação do limite superior
            v_ub = pulp.LpVariable("violation_ub", lowBound=0)
            variables['v_ub'] = v_ub
            
            # Definir a violação: max(0, soma das unidades - UB)
            units_sum = pulp.lpSum(self.problem.order_units[o] * x[o] for o in range(self.problem.n_orders))
            model += v_ub >= units_sum - self.problem.wave_size_ub, "UB_violation"
            
            # Adicionar à penalidade total
            penalties += v_ub
        
        # 3. Penalidades para as restrições de cobertura de itens
        for item in self.problem.all_order_items:
            # Demanda do item nos pedidos selecionados
            item_demand = pulp.lpSum(
                self.problem.item_units_by_order.get(item, {}).get(o, 0) * x[o]
                for o in range(self.problem.n_orders)
                if item in self.problem.item_units_by_order and o in self.problem.item_units_by_order[item]
            )
            
            # Oferta do item nos corredores selecionados
            item_supply = pulp.lpSum(
                self.problem.item_units_by_aisle.get(item, {}).get(a, 0) * y[a]
                for a in range(self.problem.n_aisles)
                if item in self.problem.item_units_by_aisle and a in self.problem.item_units_by_aisle[item]
            )
            
            # Criar variável para medir a violação da cobertura do item
            v_item = pulp.LpVariable(f"violation_item_{item}", lowBound=0)
            variables[f'v_item_{item}'] = v_item
            
            # Definir a violação: max(0, demanda - oferta)
            model += v_item >= item_demand - item_supply, f"ItemCoverage_violation_{item}"
            
            # Adicionar à penalidade total
            penalties += v_item
        
        return penalties