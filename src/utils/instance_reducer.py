# -*- coding: utf-8 -*-
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
"""
Operador de redução baseado em dominância aproximada para fixação de variáveis em zero antes da etapa exata.

Implementa uma estratégia matheurística inspirada em Fix-and-Optimize:
1. Representação densa dos corredores por pedido.
2. Matriz de conflito via broadcasting.
3. Score de eficiência S_o / |R_o|.
4. Detecção de dominância vetorizada.
5. Filtragem de pedidos dominados e corredores irrelevantes (zerando variáveis de decisão no modelo final).

Nota metodológica: A redução não é uma prova de dominância global em todos os casos; ela é uma filtragem heurística orientada à tratabilidade computacional e não garante a preservação do ótimo global.

Pode operar em GPU (CuPy) ou CPU (NumPy) de forma transparente.
"""

import numpy as np

import time

# Tentativa de importar e verificar CuPy *funcional*
_CUPY_AVAILABLE = False
cp = None
try:
    import cupy as _cp
    # Verificar se dispositivo existe E se kernels compilam de fato
    if _cp.cuda.runtime.getDeviceCount() > 0:
        _test = _cp.array([1.0, 2.0]) + _cp.array([3.0, 4.0])
        assert float(_cp.sum(_test)) > 0
        cp = _cp
        _CUPY_AVAILABLE = True
except Exception:
    # ImportError, compilação falha (arch incompatível), ou qualquer outro erro
    _CUPY_AVAILABLE = False
    cp = None


class InstanceReducer:
    """
    Reduz a instância do problema WOP eliminando pedidos dominados
    e corredores irrelevantes, usando operações vetorizadas.
    """

    def __init__(self, use_gpu=True):
        """
        Args:
            use_gpu: Se True, tenta usar CuPy/GPU. Fallback para NumPy/CPU.
        """
        self.use_gpu = use_gpu and _CUPY_AVAILABLE
        self.xp = cp if self.use_gpu else np  # Módulo de array (CuPy ou NumPy)
        self.timings = {}

    def reduce(self, orders, aisles, n_items, order_units):
        """
        Executa o pipeline completo de redução de instância.

        Args:
            orders: dict {order_id: {item_id: quantity, ...}, ...}
            aisles: dict {aisle_id: {item_id: quantity, ...}, ...}
            n_items: int, número total de tipos de itens
            order_units: dict {order_id: total_units, ...}

        Returns:
            tuple: (kept_order_ids, kept_aisle_ids, timings_dict)
                - kept_order_ids: lista de IDs dos pedidos não-dominados
                - kept_aisle_ids: lista de IDs dos corredores relevantes
                - timings_dict: tempos de cada etapa
        """
        xp = self.xp
        total_start = time.time()

        order_ids = sorted(orders.keys())
        aisle_ids = sorted(aisles.keys())
        n_orders = len(order_ids)
        n_aisles = len(aisle_ids)

        if n_orders == 0 or n_aisles == 0:
            return order_ids, aisle_ids, {}

        # Para instâncias gigantescas (ex: > 20k pedidos), evitamos as matrizes O(n²) de dominância
        # que causam OOM. Em vez disso, fazemos uma filtragem baseada puramente nos melhores scores.
        if n_orders > 20000:
            print(f"  ⚠ Instância massiva detectada ({n_orders} pedidos) — usando redução top-scoring para evitar OOM")
            t0 = time.time()
            item_to_aisles = {}
            for a_idx, a_id in enumerate(aisle_ids):
                for item_id in aisles[a_id]:
                    if item_id not in item_to_aisles:
                        item_to_aisles[item_id] = []
                    item_to_aisles[item_id].append(a_id)

            order_scores = []
            for o_id in order_ids:
                relevant_aisles = set()
                for item_id in orders[o_id]:
                    if item_id in item_to_aisles:
                        relevant_aisles.update(item_to_aisles[item_id])
                u = order_units.get(o_id, 0)
                n_corr = max(len(relevant_aisles), 1)
                order_scores.append((o_id, u / n_corr))

            order_scores.sort(key=lambda x: x[1], reverse=True)
            kept_order_ids = [o_id for o_id, s in order_scores[:1000]]
            
            kept_aisle_ids = set()
            for o_id in kept_order_ids:
                for item_id in orders[o_id]:
                    if item_id in item_to_aisles:
                        kept_aisle_ids.update(item_to_aisles[item_id])

            self.timings['dense_matrix'] = time.time() - t0
            self.timings['TOTAL'] = time.time() - total_start
            return kept_order_ids, sorted(list(kept_aisle_ids)), self.timings

        # ─── Etapa 1: Mapear corredores necessários por pedido ───
        t0 = time.time()

        # Para cada pedido, quais corredores contêm pelo menos um dos seus itens?
        # Construir em NumPy (preenching escalar é rápido em CPU)
        corridors_per_order_np = np.zeros((n_orders, n_aisles), dtype=np.int8)

        # Construir mapa item -> corredores (para lookup rápido)
        item_to_aisles = {}
        for a_idx, a_id in enumerate(aisle_ids):
            for item_id in aisles[a_id]:
                if item_id not in item_to_aisles:
                    item_to_aisles[item_id] = []
                item_to_aisles[item_id].append(a_idx)

        # Preencher a matriz (CPU)
        for o_idx, o_id in enumerate(order_ids):
            relevant_aisles = set()
            for item_id in orders[o_id]:
                if item_id in item_to_aisles:
                    relevant_aisles.update(item_to_aisles[item_id])
            for a_idx in relevant_aisles:
                corridors_per_order_np[o_idx, a_idx] = 1

        # Transferir para GPU se disponível
        corridors_per_order = xp.asarray(corridors_per_order_np) if self.use_gpu else corridors_per_order_np

        self.timings['dense_matrix'] = time.time() - t0

        # ─── Etapa 2: Matriz de conflito ───
        t0 = time.time()

        # Conflito: dois pedidos conflitam se compartilham ao menos um corredor.
        # Método eficiente: conflict = (C @ C.T > 0) — usa matmul O(n²) em vez de
        # broadcasting O(n²·m) que estourava memória em instâncias grandes.
        #
        # Estimativa de memória para matmul result: n² * 4 bytes (int32)
        mem_matmul_gb = (n_orders * n_orders * 4) / (1024**3)

        if mem_matmul_gb < 8.0:  # Cabe em GPU (8 GB VRAM) ou RAM (32 GB)
            corridors_float = corridors_per_order.astype(xp.float32)
            overlap_count = corridors_float @ corridors_float.T  # (n, n) float32
            conflict_matrix = overlap_count > 0  # (n, n) bool
            del corridors_float, overlap_count
        else:
            # Para instâncias enormes (>45k pedidos), processar linha por linha
            print(f"  ⚠ Instância muito grande ({n_orders} pedidos) — dominância linha por linha")
            conflict_matrix = xp.zeros((n_orders, n_orders), dtype=xp.bool_)
            for i in range(n_orders):
                row_i = corridors_per_order[i:i+1, :]  # (1, n_aisles)
                overlap = xp.sum(corridors_per_order * row_i, axis=1)  # (n,)
                conflict_matrix[i, :] = overlap > 0

        self.timings['conflict_matrix'] = time.time() - t0

        # ─── Etapa 3: Score de eficiência ───
        t0 = time.time()

        # S_o / |R_o| — volume dividido por número de corredores necessários
        units_array = xp.array(
            [order_units.get(o_id, 0) for o_id in order_ids], dtype=xp.float64
        )
        n_corridors_per_order = xp.sum(corridors_per_order, axis=1).astype(xp.float64)
        # Evitar divisão por zero
        n_corridors_per_order = xp.maximum(n_corridors_per_order, 1.0)
        scores = units_array / n_corridors_per_order

        self.timings['scores'] = time.time() - t0

        # ─── Etapa 4: Detecção de dominância ───
        t0 = time.time()

        # Pedido j domina pedido i se:
        #   (score[j] > score[i]) OR (score[j] == score[i] AND j < i)
        # e eles entram em conflito.
        score_gt = scores[xp.newaxis, :] > scores[:, xp.newaxis]  # (n, n)
        score_eq = scores[xp.newaxis, :] == scores[:, xp.newaxis]  # (n, n)
        
        # Array de índices para desempate
        indices = xp.arange(n_orders)
        index_lt = indices[xp.newaxis, :] < indices[:, xp.newaxis]  # j < i
        
        # Matriz de dominância com desempate
        dominates = score_gt | (score_eq & index_lt)

        # Pedido i é dominado se EXISTE algum j que o domina
        # Excluir auto-dominância (diagonal)
        identity_mask = xp.eye(n_orders, dtype=xp.bool_)
        dominance_check = dominates & conflict_matrix & (~identity_mask)

        # is_dominated[i] = True se existe algum j que domina i
        is_dominated = xp.any(dominance_check, axis=1)  # (n,)

        self.timings['dominance'] = time.time() - t0

        # ─── Etapa 5: Filtragem ───
        t0 = time.time()

        # Transferir para CPU se necessário
        if self.use_gpu:
            is_dominated_cpu = is_dominated.get()
        else:
            is_dominated_cpu = is_dominated

        # Pedidos não dominados
        kept_order_ids = [
            order_ids[i] for i in range(n_orders) if not is_dominated_cpu[i]
        ]

        # Corredores relevantes: aqueles que contêm itens dos pedidos sobreviventes
        relevant_items = set()
        for o_id in kept_order_ids:
            relevant_items.update(orders[o_id].keys())

        kept_aisle_ids = []
        for a_id in aisle_ids:
            if relevant_items & set(aisles[a_id].keys()):
                kept_aisle_ids.append(a_id)

        self.timings['filtering'] = time.time() - t0
        self.timings['total'] = time.time() - total_start

        return kept_order_ids, kept_aisle_ids, self.timings

    def print_report(self, n_orders_original, n_aisles_original,
                     n_orders_reduced, n_aisles_reduced):
        """Imprime relatório da redução."""
        backend = "GPU (CuPy)" if self.use_gpu else "CPU (NumPy)"
        print(f"\n{'='*60}")
        print(f"  REDUÇÃO DE INSTÂNCIA — {backend}")
        print(f"{'='*60}")
        print(f"  Pedidos:    {n_orders_original:>6} → {n_orders_reduced:>6} "
              f"({n_orders_reduced/max(1,n_orders_original)*100:.1f}% mantidos)")
        print(f"  Corredores: {n_aisles_original:>6} → {n_aisles_reduced:>6} "
              f"({n_aisles_reduced/max(1,n_aisles_original)*100:.1f}% mantidos)")
        print(f"  Tempos:")
        for phase, t in self.timings.items():
            if phase != 'total':
                print(f"    {phase:.<30} {t:.4f}s")
        print(f"    {'TOTAL':.<30} {self.timings.get('total', 0):.4f}s")
        print(f"{'='*60}\n")
