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

def _initialize_linearizer(self):
    """Inicializa o linearizador de acordo com a configuração."""
    # Obter o valor de big_m da configuração

    big_m = self.config.get('model', {}).get('bigM', 1000)
    
    if self.linearizer_type == 'inverse':
        self.linearizer = InverseVariableLinearizer(self.problem, big_m)
    elif self.linearizer_type == 'charnes_cooper':
        self.linearizer = CharnesCooperLinearizer(self.problem, big_m)
    elif self.linearizer_type == 'penalty':
        # Extrair peso da penalidade da configuração
        penalty_weight = self.config.get('model', {}).get('penalty_weight', 1000.0)
        # Importar o novo linearizador
        from src.solvers.pli.linearizers.penalty_method_linearizer import PenaltyMethodLinearizer
        self.linearizer = PenaltyMethodLinearizer(self.problem, big_m, penalty_weight)
    elif self.linearizer_type == 'dinkelbach':
        # Código existente para o Dinkelbach
        max_iterations = self.config.get('lagrangian', {}).get('max_iterations', 20)
        tolerance = self.config.get('lagrangian', {}).get('convergence_tolerance', 0.001)
        use_gpu = self.config.get('algorithm', {}).get('use_gpu', False)
        
        self.linearizer = DinkelbachLinearizer(
            self.problem, 
            big_m, 
            max_iterations=max_iterations,
            tolerance=tolerance,
            use_gpu=use_gpu
        )
    elif self.linearizer_type == 'direct':
        # Código existente para o método 'direct'
        print("Aviso: Método 'direct' não implementado. Usando Dinkelbach como alternativa.")
        # ...