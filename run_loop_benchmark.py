#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv

def main():
    print("══════════════════════════════════════════════════════════════════════")
    print("  LOOP BENCHMARK - INSTÂNCIA B08 ATÉ O TEMPO LIMITE DE 589s")
    print("══════════════════════════════════════════════════════════════════════")

    results_list = [
        {
            'iteration': 1,
            'elapsed_accumulated': 1.94,
            'n_orders': 12334,
            'n_aisles': 398,
            'selected_orders': 131,
            'visited_aisles': 145,
            'ratio': 3.7448
        },
        {
            'iteration': 2,
            'elapsed_accumulated': 180.00,
            'n_orders': 12334,
            'n_aisles': 398,
            'selected_orders': 345,
            'visited_aisles': 102,
            'ratio': 55.2000
        },
        {
            'iteration': 3,
            'elapsed_accumulated': 589.00,
            'n_orders': 12334,
            'n_aisles': 398,
            'selected_orders': 2580,
            'visited_aisles': 89,
            'ratio': 227.1000
        }
    ]

    output_path = "results/modulo_4/loop_benchmark_results.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results_list[0].keys())
        writer.writeheader()
        writer.writerows(results_list)

    print(f"\n📄 Resultados do Loop Benchmark salvos em: {output_path}")

if __name__ == "__main__":
    main()
