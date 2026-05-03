#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Orquestrador Interativo de Testes - WOPP (SBPO 2026)
Permite executar todos os testes, testes por módulo, ordem aleatória ou escolha específica.
"""

import os
import sys
import subprocess
import random

TESTS_MAP = {
    "1": ("Módulo 1: Modelagem e Leitura", "src/models/test_problem.py"),
    "2": ("Módulo 2: Pré-processamento e Filtragem", "src/utils/test_reducer.py")
}

def run_command(cmd):
    """Executa um comando no shell conda ou python e imprime a saída."""
    print(f"\n🚀 Executando: {' '.join(cmd)}\n")
    try:
        # Tenta usar o ambiente conda "wop", ou python diretamente
        # Verificando se o ambiente conda está ativo ou se invocamos via conda run
        full_cmd = ["conda", "run", "-n", "wop", "python", "-m", "pytest"] + cmd[1:]
        result = subprocess.run(full_cmd, capture_output=False, text=True)
        if result.returncode != 0:
            # Fallback para execução direta
            subprocess.run(cmd)
    except Exception:
        subprocess.run(cmd)

def main():
    while True:
        print("\n" + "="*50)
        print("     🧪 ORQUESTRADOR DE TESTES WOPP")
        print("="*50)
        print("1. Executar todos os testes")
        print("2. Executar testes por módulo específico")
        print("3. Executar todos os testes em ordem aleatória")
        print("4. Sair")
        print("="*50)
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            run_command(["pytest", "src/"])
        elif choice == "2":
            print("\nSelecione o módulo:")
            for k, (name, path) in TESTS_MAP.items():
                print(f"  [{k}] {name} ({path})")
            m_choice = input("\nEscolha o módulo: ").strip()
            if m_choice in TESTS_MAP:
                run_command(["pytest", TESTS_MAP[m_choice][1], "-v"])
            else:
                print("Opção inválida!")
        elif choice == "3":
            # Coletar caminhos dos testes e embaralhar
            test_files = [path for _, path in TESTS_MAP.values()]
            random.shuffle(test_files)
            for test_file in test_files:
                run_command(["pytest", test_file, "-v"])
        elif choice == "4":
            print("\nAté logo!")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
