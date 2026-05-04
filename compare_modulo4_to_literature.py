#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def main():
    print("══════════════════════════════════════════════════════════════════════")
    print("  EXECUTANDO EXPERIMENTOS DO MÓDULO 4")
    print("══════════════════════════════════════════════════════════════════════")
    
    # 1. Apaga resultados antigos/incorretos
    csv_path = "results/modulo_4/experiments.csv"
    if os.path.exists(csv_path):
        os.remove(csv_path)
        print(f"🗑️ Arquivo {csv_path} limpo com sucesso.")

    # 2. Executa experimentos reais
    cmd = [
        sys.executable, "run_experiments.py",
        "--instance", "datasets/a/instance_0001.txt",
        "--config", "C1", "C2",
        "--output", csv_path
    ]
    
    print(f"🚀 Rodando: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print("\n✅ Experimentos executados e salvos com sucesso!")

if __name__ == "__main__":
    main()
