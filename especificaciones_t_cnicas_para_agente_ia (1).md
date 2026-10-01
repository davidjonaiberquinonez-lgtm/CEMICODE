# Especificación de Proyecto: Personalización de OpenCode, Enrutamiento local DGX y Enjambre Multi-Agente con OpenCode Zen

**Objetivo:** Adaptar el repositorio open-source de **OpenCode** (`anomalyco/opencode`), personalizar su interfaz visual, conectar sus inferencias a un servidor de cálculo en NVIDIA DGX (vLLM / Ollama) y configurar un sistema orquestado de múltiples agentes especializados delegando tareas entre modelos locales y modelos curados de **OpenCode Zen**.

---

## 0. Entorno de Desarrollo Aislado (Entorno Aparte)

Para evitar contaminación de librerías globales o conflictos con las versiones de Node.js, Python o Bun del sistema principal, **todo el proyecto debe ejecutarse dentro de un entorno aislado**.

### Opción A: Entorno Aislado con Node / Bun / Conda
Si se trabaja directamente en la máquina hospedadora, utilizar gestores de versión aislados:

```bash
# 1. Crear y activar entorno aislado con Conda/Mamba (Opcional)
conda create -n opencode-env python=3.11 nodejs=20 -y
conda activate opencode-env

# 2. Utilizar Node Version Manager (nvm) para aislar la versión de Node.js
nvm install 20
nvm use 20

# 3. Utilizar Bun de forma aislada para resolver el monorepo
npm install -g bun
```

### Opción B: Entorno Contenerizado con Docker (Recomendado para Producción)
Crear un contenedor donde resida el entorno de ejecución del enjambre de agentes:

```dockerfile
# Dockerfile de Entorno Aislado
FROM node:20-slim

WORKDIR /app

# Instalar herramientas del sistema
RUN apt-get update && apt-get install -y git curl python3 build-essential && rm -rf /var/lib/apt/lists/*
RUN npm install -g bun

# Copiar proyecto y dependencias
COPY . .
RUN bun install

EXPOSE 3000
CMD ["bun", "dev"]
```

---

## 1. Repositorio de Base y Repositorio de Trabajo

* **Repositorio Oficial:** `https://github.com/anomalyco/opencode` (Licencia MIT)

* **Comando para clonar:**

  ```bash
  git clone https://github.com/anomalyco/opencode.git
  cd opencode
  bun install # O pnpm install según el gestor del monorepo
  ```

---

## 2. Personalización de UI y Frontend

1. **Rebranding & Estilo Visual:**
   * Ubicación de componentes UI: `packages/app/` o `packages/ui/` (según monorepo).
   * Modificar temas de Tailwind CSS, paletas de colores corporativas y logotipos.
   * Modificar componentes de cliente interactivo (consola TUI / Desktop App con Tauri o Electron).

2. **Recompilación:**
   * Probar cambios locales: `bun dev` o `pnpm dev`.
   * Generar el ejecutable compilado: `bun run build`.

---

## 3. Integración con Servidor NVIDIA DGX (Modelos Locales)

Para conectar el motor de OpenCode a tu instancia de NVIDIA DGX que ejecuta servicios de LLM locales (vLLM, Ollama, LM Studio):

### Archivo de Configuración de OpenCode (`~/.config/opencode/config.json` u `opencode.json` en raíz del proyecto):

```json
{
  "providers": {
    "dgx-vllm": {
      "type": "openai-compatible",
      "baseUrl": "http://<IP-DE-TU-DGX>:8000/v1",
      "apiKey": "dgx-local-key",
      "models": [
        "qwen-2.5-coder-32b-instruct",
        "deepseek-r1-distill-qwen-32b"
      ]
    },
    "opencode-zen": {
      "type": "opencode",
      "apiKey": "ENV_OPENCODE_ZEN_API_KEY"
    }
  }
}
```

---

## 4. Arquitectura del Enjambre Multi-Agente (Pool de Comunicación Inter-Agente)

Configuraremos un patrón de orquestación donde un **Agente Director/Orquestador** recibe el requerimiento, desglosa el plan de trabajo y delega el análisis, generación de código y revisión a roles secundarios con modelos diferenciados.

### 4.1 Definición de Agentes en `.opencode/agents.json` (o `AGENTS.md`)

```json
{
  "agents": {
    "orchestrator": {
      "name": "Orquestador de Proyecto",
      "role": "router_planner",
      "provider": "opencode-zen",
      "model": "zen/claude-3-7-sonnet",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      },
      "systemPrompt": "Eres el Agente Orquestador. Analizas la petición del usuario, divides la tarea en subtareas y delegas código al agente Coder y pruebas al agente Tester. No modificas archivos directamente."
    },
    "coder_dgx": {
      "name": "Especialista en Código (DGX)",
      "role": "code_executor",
      "provider": "dgx-vllm",
      "model": "qwen-2.5-coder-32b-instruct",
      "permission": {
        "edit": "allow",
        "bash": "allow"
      },
      "systemPrompt": "Eres un Agente Programador Senior ejecutado localmente en la NVIDIA DGX. Recibes especificaciones exactas del Orquestador e implementas o editas el código necesario."
    },
    "reasoning_dgx": {
      "name": "Razonamiento Complejo (DGX)",
      "role": "architect",
      "provider": "dgx-vllm",
      "model": "deepseek-r1-distill-qwen-32b",
      "permission": {
        "edit": "deny"
      },
      "systemPrompt": "Eres el Agente Arquitecto en la DGX. Tu trabajo es diseñar la lógica de datos, algoritmos complejos y resolver bugs difíciles entregando análisis al Coder."
    },
    "reviewer_zen": {
      "name": "Revisor de Calidad & QA (Zen)",
      "role": "tester",
      "provider": "opencode-zen",
      "model": "zen/deepseek-r1",
      "permission": {
        "edit": "deny",
        "bash": "allow"
      },
      "systemPrompt": "Eres el Agente Revisor. Tu trabajo es ejecutar pruebas unitarias y auditar el código generado por los agentes locales para asegurar máxima calidad."
    }
  }
}
```

---

## 5. Instrucción para el Agente IA de Desarrollo

> **Prompt para tu Agente:**
> *"Hola Agente. Tu objetivo es primero preparar un entorno aislado de desarrollo (usando NVM/Bun o Docker) y clonar `https://github.com/anomalyco/opencode`. Revisa la estructura monorepo del proyecto e implementa un módulo multi-agente siguiendo la arquitectura del archivo `opencode_multiagent_dgx_spec.md`. Permite que la UI consuma los endpoints de la DGX (`http://<IP-DE-TU-DGX>:8000/v1`) y modele la delegación de prompts entre los agentes orquestadores, programadores y revisores. Mantén todo el código bajo la licencia MIT del repositorio original."*