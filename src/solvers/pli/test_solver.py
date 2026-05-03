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

import pytest
import os
from src.models.problem import WaveOrderPickingProblem
from src.solvers.pli.pli_solver import PLISolver

def test_solver_inverse():
    # Instância básica para testar o solver linearizado
    orders = {0: {101: 2, 102: 1}}
    aisles = {0: {101: 10, 102: 10}}
    problem = WaveOrderPickingProblem(orders=orders, aisles=aisles, n_items=200, wave_size_lb=1, wave_size_ub=50)
    problem._preprocess_sequential()
    
    config = {
        'algorithm': {
            'solver': 'CBC', # Usando CBC como fallback padrão nos testes para evitar dependência de CPLEX no ambiente de CI/CD
            'linearizer': 'inverse',
            'instance_reduction': 'false'
        },
        'constraints': {
            'soft_constraints': 'true'
        }
    }
    
    solver = PLISolver(problem, config=config)
    solution = solver.solve()
    
    # Validações básicas da solução retornada
    assert solution is not None
    assert isinstance(solution.selected_orders, list)
    assert isinstance(solution.visited_aisles, list)

def test_solver_dinkelbach():
    # Instância básica para testar o solver via Dinkelbach
    orders = {0: {101: 2}}
    aisles = {0: {101: 10}}
    problem = WaveOrderPickingProblem(orders=orders, aisles=aisles, n_items=200, wave_size_lb=1, wave_size_ub=50)
    problem._preprocess_sequential()
    
    config = {
        'algorithm': {
            'solver': 'CBC',
            'linearizer': 'dinkelbach',
            'instance_reduction': 'false'
        }
    }
    
    solver = PLISolver(problem, config=config)
    solution = solver.solve()
    
    assert solution is not None
    assert isinstance(solution.selected_orders, list)
