import pytest
import os
from src.models.problem import WaveOrderPickingProblem

def test_read_valid_instance():
    # Criar uma instância de teste em um arquivo temporário
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
        
        # Testar parsing correto dos limites e dimensões
        assert problem.n_orders == 2
        assert problem.n_items == 3
        assert problem.n_aisles == 2
        assert problem.wave_size_lb == 10
        assert problem.wave_size_ub == 50
        
        # Testar dados dos pedidos
        assert problem.orders[0] == {0: 10, 1: 5}
        assert problem.orders[1] == {2: 20}
        
        # Testar dados dos corredores
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
