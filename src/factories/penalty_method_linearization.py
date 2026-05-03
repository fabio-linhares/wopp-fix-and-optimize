class PenaltyMethodLinearizer:
    def __init__(self, problem, penalty_weight=1000.0):
        self.problem = problem
        self.penalty_weight = penalty_weight
    
    def linearize(self, model, x, y, q_value=0):
        """
        Lineariza o problema incorporando as restrições como penalidades na função objetivo.
        """
        # Calcular a função objetivo base (como no método de Dinkelbach)
        base_objective = pulp.lpSum(
            self.problem.order_units[o] * x[o] for o in range(self.problem.n_orders)
        ) - q_value * pulp.lpSum(y[a] for a in range(self.problem.n_aisles))
        
        # Adicionar penalidades para violações de restrições
        penalties = self._calculate_constraint_penalties(x, y)
        
        # Função objetivo final: base - penalidades
        objective_expr = base_objective - self.penalty_weight * penalties
        
        return objective_expr, {}
    
    def _calculate_constraint_penalties(self, x, y):
        """
        Calcula os termos de penalidade para as restrições.
        Retorna uma expressão PuLP que representa as violações de restrições.
        """
        penalties = 0
        
        # Penalidade para tamanho mínimo da onda
        if self.problem.min_wave_size > 0:
            # Usamos max(0, min_size - atual_size) como penalidade
            wave_size = pulp.lpSum(
                self.problem.order_units[o] * x[o] for o in range(self.problem.n_orders)
            )
            min_violation = pulp.LpVariable("min_wave_violation", lowBound=0)
            model += min_violation >= self.problem.min_wave_size - wave_size, "min_wave_violation_constr"
            penalties += min_violation
        
        # Penalidade para tamanho máximo da onda
        if self.problem.max_wave_size < float('inf'):
            # Usamos max(0, atual_size - max_size) como penalidade
            wave_size = pulp.lpSum(
                self.problem.order_units[o] * x[o] for o in range(self.problem.n_orders)
            )
            max_violation = pulp.LpVariable("max_wave_violation", lowBound=0)
            model += max_violation >= wave_size - self.problem.max_wave_size, "max_wave_violation_constr"
            penalties += max_violation
        
        # Penalidade para cobertura de itens
        for i in range(self.problem.n_items):
            # Quantidade necessária do item
            item_demand = pulp.lpSum(
                self.problem.order_item_quantities[(o, i)] * x[o] 
                for o in range(self.problem.n_orders) 
                if (o, i) in self.problem.order_item_quantities
            )
            
            # Quantidade disponível nos corredores visitados
            item_supply = pulp.lpSum(
                self.problem.aisle_item_contains[(a, i)] * y[a]
                for a in range(self.problem.n_aisles)
                if (a, i) in self.problem.aisle_item_contains
            )
            
            # Penalidade é max(0, demanda - suprimento)
            item_violation = pulp.LpVariable(f"item_violation_{i}", lowBound=0)
            model += item_violation >= item_demand - item_supply, f"item_violation_constr_{i}"
            penalties += item_violation
        
        return penalties
    
    def solve_iteratively(self, model_builder):
        """
        Executa o algoritmo iterativo de Dinkelbach com penalidades.
        """
        q_current = 0.0
        best_solution = None
        
        for iteration in range(5):  # Definindo um máximo de 5 iterações como padrão
            # Resolver o problema linearizado com q atual
            solution = model_builder(q_current)
            
            if solution is None:
                # Se o solver não encontrou solução, pare
                break
            
            # Calcular o novo valor de q
            new_q = solution.objective_value
            
            # Verificar convergência
            if abs(new_q - q_current) < 1e-6:
                best_solution = solution
                break
            
            # Atualizar q para próxima iteração
            q_current = new_q
            best_solution = solution
        
        return best_solution