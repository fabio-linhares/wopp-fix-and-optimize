import os
import time
from src.config_manager import load_config
from src.models.problem import WaveOrderPickingProblem
from src.solvers.pli.pli_solver import PLISolver

config = load_config()
config['algorithm']['instance_reduction'] = 'false'
config['algorithm']['solver'] = 'CBC'
config['algorithm']['max_runtime'] = '60'
config['constraints']['soft_constraints'] = 'false'

instance_path = os.path.join("datasets", "b", "instance_0008.txt")
problem = WaveOrderPickingProblem(config=config)
problem.read_input(instance_path)

print(f"Resolvendo B08 completo ({problem.n_orders} pedidos) com CBC por 60s...")
solver = PLISolver(problem, config)
solution = solver.solve(time.time())

if solution and solution.selected_orders:
    print(f"Pedidos selecionados: {len(solution.selected_orders)}")
    print(f"Corredores: {len(solution.visited_aisles)}")
    print(f"Unidades totais: {solution.total_units}")
    print(f"Ratio: {solution.total_units / max(1, len(solution.visited_aisles))}")
else:
    print("Infeasible")
