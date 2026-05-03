FROM nvidia/cuda:12.2.2-devel-ubuntu22.04

# Evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python 3.11, JRE, compiladores e bibliotecas auxiliares
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    default-jre \
    libcrypt1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configurar o ambiente virtual Python
ENV VIRTUAL_ENV=/opt/venv
RUN python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copiar os requisitos
WORKDIR /app
COPY requirements.txt .

# Atualizar pip e instalar dependências do projeto
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos de instalação do CPLEX
WORKDIR /tmp/cplex_install
COPY cos_installer_preview-22.1.2.R4-M0N96ML-linux-x86-64.bin .
COPY response.properties .

# Ajustar o arquivo response.properties para instalar em /opt/ibm/ILOG/CPLEX_Studio2212
RUN sed -i 's|USER_INSTALL_DIR=.*|USER_INSTALL_DIR=/opt/ibm/ILOG/CPLEX_Studio2212|' response.properties

# Dar permissão e rodar o instalador da IBM em modo silencioso
RUN chmod +x cos_installer_preview-22.1.2.R4-M0N96ML-linux-x86-64.bin \
    && ./cos_installer_preview-22.1.2.R4-M0N96ML-linux-x86-64.bin -f response.properties \
    && rm -rf /tmp/cplex_install

# Configurar variáveis de ambiente do CPLEX
ENV CPLEX_STUDIO_DIR="/opt/ibm/ILOG/CPLEX_Studio2212"
ENV PATH="$CPLEX_STUDIO_DIR/cplex/bin/x86-64_linux:$PATH"
ENV LD_LIBRARY_PATH="$CPLEX_STUDIO_DIR/cplex/bin/x86-64_linux:$CPLEX_STUDIO_DIR/cplex/lib/x86-64_linux/static_pic:$LD_LIBRARY_PATH"

WORKDIR /app
CMD ["bash"]
