# CEMICODE — entorno aislado (Docker recomendado produccion)
FROM node:20-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl python3 build-essential ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && npm install -g bun

# Solo capa CEMICODE (upstream se monta como volumen o se copia en build pulido)
COPY opencode.json ./
COPY .opencode ./.opencode/
COPY scripts ./scripts/
COPY cemicode-branding ./cemicode-branding/
COPY README_CEMICODE.md AGENTS.md ./

RUN bun --version && python3 --version && node --version

EXPOSE 3000
CMD ["bun", "--cwd", "opencode-upstream", "dev"]
