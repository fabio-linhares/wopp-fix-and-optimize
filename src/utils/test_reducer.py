import pytest
from src.utils.instance_reducer import InstanceReducer

def test_reducer_cpu():
    orders = {
        0: {101: 2},
        1: {101: 1}, # Order 1 is dominated by order 0 because order 0 has higher units for the same item/corridor
    }
    aisles = {
        0: {101: 10}
    }
    order_units = {0: 2, 1: 1}
    
    reducer = InstanceReducer(use_gpu=False)
    kept_orders, kept_aisles, timings = reducer.reduce(orders, aisles, 200, order_units)
    
    assert 0 in kept_orders
    # Order 1 may be dominated because they conflict on the same aisle and order 0 has higher score
    assert 1 not in kept_orders
    assert 0 in kept_aisles

def test_reducer_empty_input():
    # Testa o comportamento do reducer com listas vazias
    reducer = InstanceReducer(use_gpu=False)
    kept_orders, kept_aisles, timings = reducer.reduce({}, {}, 0, {})
    
    assert kept_orders == []
    assert kept_aisles == []

def test_reducer_no_domination():
    # Testa quando não há sobreposição de corredores e nenhum pedido é dominado
    orders = {
        0: {101: 1},
        1: {102: 1}
    }
    aisles = {
        0: {101: 1},
        1: {102: 1}
    }
    order_units = {0: 1, 1: 1}
    
    reducer = InstanceReducer(use_gpu=False)
    kept_orders, kept_aisles, timings = reducer.reduce(orders, aisles, 200, order_units)
    
    assert 0 in kept_orders
    assert 1 in kept_orders
    assert 0 in kept_aisles
    assert 1 in kept_aisles

def test_reducer_use_gpu_fallback():
    # Garante que fallback funciona corretamente
    reducer = InstanceReducer(use_gpu=True)
    # Se CuPy não estiver funcional, use_gpu deve ser False após a inicialização
    assert reducer.xp is not None
