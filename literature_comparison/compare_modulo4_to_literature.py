#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def main():
    print("══════════════════════════════════════════════════════════════════════")
    print("  EXECUTANDO EXPERIMENTOS DO MÓDULO 4 CONTRA A LITERATURA")
    print("══════════════════════════════════════════════════════════════════════")
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    run_experiments_script = os.path.join(root_dir, "run_experiments.py")
    
    # 1. Apaga resultados antigos/incorretos
    csv_path = os.path.join(root_dir, "results/modulo_4/experiments.csv")
    if os.path.exists(csv_path):
        os.remove(csv_path)
        print(f"🗑️ Arquivo {csv_path} limpo com sucesso.")

    # 2. Executa experimentos reais
    cmd = [
        sys.executable, run_experiments_script,
        "--instance", os.path.join(root_dir, "datasets/a/instance_0001.txt"),
        "--config", "C1", "C2",
        "--output", csv_path
    ]
    
    print(f"🚀 Rodando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=root_dir)
    
    print("\n✅ Experimentos executados e salvos com sucesso!")

if __name__ == "__main__":
    main()
