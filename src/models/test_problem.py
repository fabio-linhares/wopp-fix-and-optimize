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


def test_read_valid_instance():
    instance_text = """2 3 2
2 0 10 1 5
1 2 20
2 0 100 1 50
1 2 10
10 50
"""
    test_file = "test_instance.txt"
    with open(test_file, "w") as f:
        f.write(instance_text)
        
    try:
        problem = WaveOrderPickingProblem()
        problem.read_input(test_file)
        
        assert problem.n_orders == 2
        assert problem.n_items == 3
        assert problem.n_aisles == 2
        assert problem.wave_size_lb == 10
        assert problem.wave_size_ub == 50
        assert problem.orders[0] == {0: 10, 1: 5}
        assert problem.orders[1] == {2: 20}
        assert problem.aisles[0] == {0: 100, 1: 50}
        assert problem.aisles[1] == {2: 10}
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def test_problem_fallback_preprocess():
    orders = {0: {10: 2, 11: 3}}
    aisles = {0: {10: 100}, 1: {11: 50}}
    problem = WaveOrderPickingProblem(orders=orders, aisles=aisles, n_items=12, wave_size_lb=2, wave_size_ub=5)
    problem._preprocess_sequential()
    
    assert problem.order_units[0] == 5
    assert problem.item_units_by_aisle[10][0] == 100
    assert problem.item_units_by_aisle[11][1] == 50
    assert problem.item_units_by_order[10][0] == 2
    assert problem.item_units_by_order[11][0] == 3

def test_empty_instance():
    problem = WaveOrderPickingProblem()
    res = problem.read_input("non_existent_file.txt")
    assert res is problem
    assert len(problem.orders) == 0

def test_edge_case_zero_orders():
    problem = WaveOrderPickingProblem(orders={}, aisles={}, n_items=0, wave_size_lb=0, wave_size_ub=0)
    problem._preprocess_sequential()
    assert len(problem.order_units) == 0

def test_wave_bounds_consistency():
    # Testa os limites operacionais de wave
    problem = WaveOrderPickingProblem(orders={}, aisles={}, n_items=0, wave_size_lb=50, wave_size_ub=10)
    assert problem.wave_size_lb == 50
    assert problem.wave_size_ub == 10

def test_all_order_items_uniqueness():
    # Testa a extração de itens únicos
    orders = {
        0: {10: 5, 11: 2},
        1: {11: 1, 12: 4}
    }
    problem = WaveOrderPickingProblem(orders=orders, aisles={}, n_items=20, wave_size_lb=1, wave_size_ub=10)
    problem._preprocess_sequential()
    assert problem.all_order_items == {10, 11, 12}

def test_order_units_sum():
    # Valida o cálculo exato do somatório de itens demandados em um pedido
    orders = {
        0: {101: 5, 102: 10, 103: 15}
    }
    problem = WaveOrderPickingProblem(orders=orders, aisles={}, n_items=200, wave_size_lb=1, wave_size_ub=50)
    problem._preprocess_sequential()
    assert problem.order_units[0] == 30

def test_invalid_line_format():
    # Testa a resposta do parser ao tentar ler arquivo mal formatado
    malformed_text = "not_a_number\n"
    test_file = "malformed_instance.txt"
    with open(test_file, "w") as f:
        f.write(malformed_text)
    try:
        problem = WaveOrderPickingProblem()
        problem.read_input(test_file)
        assert len(problem.orders) == 0
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
