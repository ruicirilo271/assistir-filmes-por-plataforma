FROM python:3.10-slim

# Instalar dependências do sistema necessárias para o Playwright + Chromium
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libxshmfence1 \
    libxcb1 \
    libxfixes0 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libdbus-1-3 \
    libglib2.0-0 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar ficheiros
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar browsers do Playwright
RUN python -m playwright install chromium

# Expõe a porta 8080 para o Fly.io
EXPOSE 8080

# Variáveis de ambiente para Flask rodar na porta 8080 e aceitar conexões externas
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Comando para iniciar a app Flask
CMD ["flask", "run"]
