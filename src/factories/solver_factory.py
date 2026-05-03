import logging
import os
import sys

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.solvers.pli.pli_solver import PLISolver
from src.solvers.heuristic.greedy_solver import GreedySolver

class SolverFactory:
    """Fábrica para criar instâncias de solvers apropriados."""
    
    @staticmethod
    def create_solver(problem, method_or_config=None, config=None):
        """
        Cria um solver apropriado para o problema.
        """
        if isinstance(method_or_config, str):
            method = method_or_config
            config = config or {}
        else:
            config = method_or_config or {}
            strategy = config.get('algorithm', {}).get('strategy', 'pli')
            solver_type = config.get('algorithm', {}).get('solver', 'CPLEX')
            
            if strategy == 'heuristic':
                method = 'greedy'
            else:
                method = 'pli'
        
        solver_to_method = {
            'CPLEX': 'pli',
            'CPLEX_GPU': 'pli',
            'CBC': 'pli',
            'GLPK': 'pli',
        }
        
        if method in solver_to_method:
            actual_method = solver_to_method[method]
            logger.info(f"Usando método {actual_method} com solver {method}")
            method = actual_method
        
        if method == 'pli':
            logger.info(f"Criando solver PLI...")
            greedy = GreedySolver(problem, config)
            initial_solution = greedy.solve()
            
            pli_solver = PLISolver(problem, config)
            if initial_solution and initial_solution.is_feasible:
                pli_solver.initial_solution = initial_solution
                
            return pli_solver
            
        elif method == 'greedy':
            logger.info("Criando solver Heurístico Guloso...")
            return GreedySolver(problem, config)
            
        else:
            logger.error(f"ERRO: Método desconhecido: {method}, usando PLI como fallback")
            return PLISolver(problem, config)
    
    @staticmethod
    def compute_objective_function(solution):
        """Calcula o valor da função objetivo."""
        if not solution.visited_aisles:
            return 0.0
        if len(solution.visited_aisles) == 0:
            return 0.0
        try:
            result = solution.total_units / len(solution.visited_aisles)
        except (ArithmeticError, ValueError) as e:
            logger.error(f"Erro matemático: {str(e)}")
            result = 0
        return result