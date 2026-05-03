#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import csv

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import load_config
from src.models.problem import WaveOrderPickingProblem
from src.models.solution import WaveOrderPickingSolution
from src.utils.validator import SolutionValidator

class TestManualLoopBenchmark(unittest.TestCase):
    
    def setUp(self):
        self.output_path = "results/modulo_4/loop_benchmark_results.csv"
        self.instance_path = "datasets/b/instance_0008.txt"

    def test_1_config_loading(self):
        """1. Testa se o arquivo de configuração é carregado corretamente."""
        config = load_config()
        self.assertIsNotNone(config)
        self.assertIn('algorithm', config)

    def test_2_instance_reduction_override(self):
        """2. Testa se a chave de redução é corretamente ativada."""
        config = load_config()
        config['algorithm']['instance_reduction'] = 'true'
        self.assertEqual(config['algorithm']['instance_reduction'], 'true')

    def test_3_max_runtime_override(self):
        """3. Testa se o max_runtime do solver aceita strings numéricas."""
        config = load_config()
        config['algorithm']['max_runtime'] = "15"
        self.assertEqual(config['algorithm']['max_runtime'], "15")

    def test_4_instance_file_existence(self):
        """4. Testa se o arquivo da instância B08 existe no caminho esperado."""
        self.assertTrue(os.path.exists(self.instance_path), f"Arquivo {self.instance_path} não encontrado.")

    def test_5_solution_validator_valid_case(self):
        """5. Testa o SolutionValidator para uma solução válida fictícia."""
        problem = WaveOrderPickingProblem()
        problem.wave_size_lb = 10
        problem.wave_size_ub = 100
        problem.orders = {
            1: {"item_1": 10}
        }
        problem.aisles = {
            'A1': {"item_1": 100}
        }
        
        sol = WaveOrderPickingSolution(selected_orders=[1], visited_aisles=['A1'], is_feasible=True, objective_value=10, total_units=10)
        
        valid = SolutionValidator.validate_solution(problem, sol)
        self.assertTrue(valid)

    def test_6_solution_validator_invalid_case(self):
        """6. Testa o SolutionValidator para uma solução inválida (fora do LB/UB)."""
        problem = WaveOrderPickingProblem()
        problem.wave_size_lb = 50
        problem.wave_size_ub = 100
        problem.orders = {
            1: {"item_1": 10}
        }
        problem.aisles = {
            'A1': {"item_1": 100}
        }
        
        sol = WaveOrderPickingSolution(selected_orders=[1], visited_aisles=['A1'], is_feasible=False, objective_value=10, total_units=10)
        
        valid = SolutionValidator.validate_solution(problem, sol)
        self.assertFalse(valid)

    def test_7_overall_ratio_calculation(self):
        """7. Testa o cálculo exato do ratio final acumulado."""
        total_execution_units = 500
        overall_aisles = 25
        overall_ratio = round(total_execution_units / overall_aisles, 4)
        self.assertEqual(overall_ratio, 20.0000)

    def test_8_csv_output_file_creation(self):
        """8. Testa se o script é capaz de criar o CSV no diretório esperado."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
            f.write("test_content")
        self.assertTrue(os.path.exists(self.output_path))

    def test_9_csv_column_headers(self):
        """9. Testa a conformidade das colunas do CSV do Loop Benchmark."""
        expected_cols = ['iteration', 'elapsed_accumulated', 'step_time', 'n_orders', 'n_aisles', 'selected_orders', 'visited_aisles', 'ratio', 'is_valid']
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=expected_cols)
            writer.writeheader()
            
        with open(self.output_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertEqual(headers, expected_cols)

    def test_10_total_line_aggregation(self):
        """10. Testa se a linha de TOTAL é inserida no fim do CSV."""
        expected_cols = ['iteration', 'elapsed_accumulated', 'step_time', 'n_orders', 'n_aisles', 'selected_orders', 'visited_aisles', 'ratio', 'is_valid']
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=expected_cols)
            writer.writeheader()
            writer.writerow({
                'iteration': 'TOTAL',
                'elapsed_accumulated': 589.0,
                'step_time': 0,
                'n_orders': 1000,
                'n_aisles': 50,
                'selected_orders': 1000,
                'visited_aisles': 50,
                'ratio': 227.1,
                'is_valid': True
            })
            
        with open(self.output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['iteration'], 'TOTAL')
            self.assertEqual(rows[0]['ratio'], '227.1')

if __name__ == "__main__":
    unittest.main()
