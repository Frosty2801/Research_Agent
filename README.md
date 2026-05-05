# Research Agent

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Status](https://img.shields.io/badge/status-active%20development-yellow)

Research Agent is a Python research assistant that plans a topic, searches and reads web sources, extracts findings with an LLM, stores memory in ChromaDB, and writes structured reports in Markdown and JSON.

> [!NOTE]
> The project is in active development. The current implementation supports a working CLI, mock or Tavily search, Ollama-based generation, ChromaDB memory, and local report output.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)

## Features

- Topic planning through a dedicated `Planner`.
- Search abstraction with mock search by default and Tavily support.
- Web page reading with HTML cleanup and network fallbacks.
- LLM-assisted claim extraction, title generation, and summary synthesis through Ollama.
- ChromaDB-backed research memory for previous summaries.
- Report generation in Markdown and JSON.
- CLI entry point through `research-agent`.
- Layered architecture with explicit ports for external dependencies.

## Architecture

The project follows a layered design:

| Layer | Responsibility |
| --- | --- |
| `application/` | Wires use cases and dependencies. |
| `core/` | Domain state, schemas, planning, research orchestration, reporting, and ports. |
| `llm/` | LLM adapters and research prompts. |
| `memory/` | ChromaDB persistence behind a memory interface. |
| `reports/` | Markdown and JSON report output. |
| `tools/` | External tools such as search, page reading, and citation extraction. |
| `config/` | Environment-based settings. |

Core code depends on protocols instead of concrete infrastructure. This keeps the workflow testable and makes providers easier to replace.

## Installation

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install -e ".[dev]"
```

This installs the project in editable mode, development dependencies, and the `research-agent` CLI script.

## Configuration

Create a local environment file:

```bash
cp .env.example .env
```

Supported variables:

```env
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
LLM_PROVIDER=ollama
LLM_TEMPERATURE=0.2

DEFAULT_SEARCH_PROVIDER=mock
TAVILY_API_KEY=your_tavily_api_key_here

MEMORY_DIR=src/data/memory
CHROMA_COLLECTION_NAME=research_memory
REPORTS_DIR=src/data/outputs
```

### Providers

| Variable | Description |
| --- | --- |
| `LLM_PROVIDER` | Currently supports `ollama`. |
| `OLLAMA_API_URL` | Local Ollama server URL. |
| `OLLAMA_MODEL` | Ollama model used for generation. |
| `DEFAULT_SEARCH_PROVIDER` | Use `mock` for local testing or `tavily` for real web search. |
| `TAVILY_API_KEY` | Required only when `DEFAULT_SEARCH_PROVIDER=tavily`. |
| `MEMORY_DIR` | ChromaDB persistence directory. |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection name. |
| `REPORTS_DIR` | Directory where Markdown and JSON reports are written. |

## Usage

### 1. Start Ollama

In another terminal:

```bash
ollama serve
```

Pull the configured model if needed:

```bash
ollama pull llama3.1
```

### 2. Run the CLI

Use mock search first:

```bash
.venv/bin/research-agent "impacto de la inteligencia artificial en la educacion"
```

Or run the module directly:

```bash
.venv/bin/python -m src.cli "impacto de la inteligencia artificial en la educacion"
```

The CLI prints the report title and output paths:

```text
Report title: ...
Markdown: src/data/outputs/...
JSON: src/data/outputs/...
```

### 3. Enable Tavily Search

Set the provider and API key in `.env`:

```env
DEFAULT_SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_real_key
```

Then run the same CLI command.

### Python API

```python
from src.application.factory import build_research_workflow
from src.config.settings import get_settings
from src.reports.writer import ResearchReportWriter

settings = get_settings()
workflow = build_research_workflow(settings)

report = workflow.run("impacto de la IA en educacion")
paths = ResearchReportWriter(settings.reports_dir).save(report)

print(report.title)
print(paths.markdown)
print(paths.json)
```

## Testing

Run the test suite:

```bash
.venv/bin/python -m pytest -q
```

Run a syntax check:

```bash
.venv/bin/python -m compileall src tests
```

Current tests cover:

- planner state creation
- search and page reading flow
- citation deduplication
- ChromaDB memory behavior with a fake collection
- LLM assistant behavior with a fake text generator
- report writing
- CLI execution path

## Project Structure

```text
src/
  application/
    factory.py
    research_workflow.py
  config/
    settings.py
  core/
    planner.py
    ports.py
    reporter.py
    researcher.py
    schemas.py
    state.py
    summarizer.py
  llm/
    ollama_client.py
    prompts.py
    research_assistant.py
  memory/
    chroma_store.py
    store.py
  reports/
    writer.py
  tools/
    citations.py
    web_search.py
    webpage_reader.py
tests/
  test_core_flow.py
```

## Generated Data

Runtime artifacts are written under:

```text
src/data/memory/
src/data/outputs/
```

`src/data/memory/` stores ChromaDB state. `src/data/outputs/` stores generated Markdown and JSON reports.

## Roadmap

- Validate Tavily search with real credentials and production-like errors.
- Improve article extraction quality for noisy web pages.
- Tune LLM prompts with real research runs.
- Store richer memory in ChromaDB, including findings and source evidence.
- Add semantic retrieval of related past research.
- Improve citation formatting with inline references.
- Add integration tests for real Ollama, Tavily, and ChromaDB.

## License

No license has been declared yet.
