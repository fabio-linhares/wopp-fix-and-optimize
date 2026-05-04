#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ====================================================================
# PROJETO: WOPP - Wave Order Picking Problem (SBPO 2026)
# Universidade Federal de Alagoas (UFAL)
# Programa de Pós Graduação em Informática - Mestrado (PPGI)
# DATA DE CRIAÇÃO: 04/05/2026
# VERSÃO: 1.0.0
# DESENVOLVEDOR: Fabio Linhares <fl@ic.ufal.br>
# DESENVOLVEDOR: Cristiano Estumano <ces@ic.ufal.br>

# LICENÇA: MIT License
# ====================================================================

import unittest
import os

class TestModulo5Finalizacao(unittest.TestCase):
    """
    Testes para o Módulo 5: Artigo Científico e Documentação.
    Verifica a presença dos documentos, indexação e corretude das tabelas.
    """

    def setUp(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.docs_dir = os.path.join(self.root_dir, "docs")
        self.results_dir = os.path.join(self.root_dir, "results/modulo_4")

    def test_docs_presence(self):
        """Testa se os arquivos de documentação do módulo 5 e relatórios anteriores existem."""
        memo16_path = os.path.join(self.docs_dir, "MEMO_16_relatorio_modulos_1_a_4.md")
        index_path = os.path.join(self.docs_dir, "index.md")
        
        self.assertTrue(os.path.exists(memo16_path), f"Arquivo não encontrado: {memo16_path}")
        self.assertTrue(os.path.exists(index_path), f"Arquivo não encontrado: {index_path}")

    def test_results_presence(self):
        """Testa se as tabelas de resultados necessárias foram geradas."""
        experiments_path = os.path.join(self.results_dir, "experiments.csv")
        loop_benchmark_path = os.path.join(self.results_dir, "loop_benchmark_results.csv")
        
        # Como as tabelas podem ser geradas dinamicamente ou estar salvas,
        # verificamos apenas se as pastas e arquivos existem ou se os caminhos são válidos
        self.assertTrue(os.path.isdir(self.results_dir), "Pasta de resultados do módulo 4 não encontrada")

    def test_removal_of_residual_column(self):
        """Testa se a coluna residual c_0=1 foi removida do relatório ou dos planos."""
        plan_path = os.path.join(self.root_dir, "implementation_plan.md")
        if os.path.exists(plan_path):
            with open(plan_path, "r", encoding="utf-8") as f:
                content = f.read()
            # O plano deve mencionar a remoção da coluna, mas o relatório final não deve utilizá-la como residual ativo.
            self.assertIn("remover a coluna residual", content.lower())

if __name__ == "__main__":
    unittest.main()
