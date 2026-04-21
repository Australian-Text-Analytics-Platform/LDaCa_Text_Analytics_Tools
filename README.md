# LDaCA Binder

<<<<<<< HEAD
LDaCA is a modular, end-to-end text analytics ecosystem: a Polars-powered Python library for large-scale document processing (`docframe`), a composable workspace graph layer (`docworkspace`), and a FastAPI + React web application for interactive exploration. The platform focuses on lazy, reproducible text pipelines, workspace serialisation, and zero-copy transitions from backend processing to frontend visualisation.

## Installation

### Prerequisites

- Python 3.14
- Node.js 24+ and npm
- [uv](https://docs.astral.sh/uv/) package manager

Install uv if you do not have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

1. Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/Australian-Text-Analytics-Platform/LDaCA-Text-Analytics-Tools.git
cd LDaCA-Text-Analytics-Tools
```

2. If you have already cloned without submodules, initialise them:

```bash
git submodule update --init --recursive
```

3. Install dependencies:

```bash
uv sync --python 3.12
cd ldaca_web_app/frontend && npm install && cd ../..
```

4. Create your environment file:

```bash
cp ldaca_web_app/backend/.env.example ldaca_web_app/backend/.env
```

Edit `.env` to configure API keys and other settings as needed.

## Running the Application

Start the full stack (backend on port 8001, frontend on port 3000):

```bash
bash run.sh
```

Then open http://localhost:3000 in your browser.

### Running Components Separately

**Backend only:**

```bash
cd ldaca_web_app/backend
uv run fastapi dev src/ldaca_web_app_backend/main.py --port 8001
```

**Frontend only:**

```bash
cd ldaca_web_app/frontend
npm start
```

## Debugging

### Log Files

- **Backend logs:** `ldaca_web_app/backend/backend.log`
- **Frontend logs:** `ldaca_web_app/frontend/frontend.log`

To watch logs in real time:

```bash
tail -f ldaca_web_app/backend/backend.log
```

### API Documentation

When the backend is running, interactive API documentation is available at:

- OpenAPI (Swagger): http://localhost:8001/api/docs
- Health check: http://localhost:8001/api/health

## AI Annotator

The AI Annotator is an integrated tool for classifying text data using large language models. It supports multiple LLM providers including OpenAI, Anthropic, Google Gemini, and local models via Ollama.

### Features

- **Zero-shot and few-shot classification:** Define custom classification schemas with class names and descriptions, optionally with example texts for improved accuracy.
- **Multiple providers:** Choose from OpenAI (GPT-4, GPT-5), Anthropic (Claude), Google Gemini, or run locally with Ollama.
- **Cost estimation:** Preview estimated token usage and costs before running classification jobs.
- **Batch processing:** Classify large datasets efficiently with background job processing.
- **Result integration:** Classification results are automatically saved as new nodes in your workspace graph, with columns for predicted class, confidence score, and optional reasoning.

### Configuration

To use cloud providers, add your API keys to the `.env` file:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
```

For local models, ensure Ollama is running at the configured endpoint (default: http://127.0.0.1:11434).
=======
This repository is the Binder wrapper for the LDaCA web application. It opens the `ldaca_web_app` repository directly in Binder without building a Docker image.
>>>>>>> dev

## Repository layout

- `binder/` contains the repo2docker environment and post-build setup.
- `ldaca_web_app/` is the application submodule (used only for local development; Binder installs from PyPI).
- `ldaca_web_app_launch.ipynb` is the Binder notebook entry point.
- `utils.py` provides Binder-specific helpers (JupyterHub proxy URL detection).

## Binder launch

<<<<<<< HEAD
- BinderHub Demo:
  [![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/LDaCA-Text-Analytics-Tools/main?labpath=LDaCa_Analysis.ipynb)
=======
[![Binder](https://mybinder.org/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/ldaca_web_app_binder/main?labpath=ldaca_web_app_launch.ipynb)

## Local development

```bash
uv sync
```
>>>>>>> dev
