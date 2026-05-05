# Research Agent

Agente de investigacion en Python para construir un flujo simple de busqueda, lectura de fuentes y generacion de reportes estructurados.

> Estado actual: el proyecto tiene una arquitectura base, herramientas iniciales, memoria local en JSON y una capa LLM para Ollama. Todavia no es un agente de investigacion funcional de punta a punta con CLI, busqueda web real validada o reportes persistentes.

## Que hace hoy

El flujo principal esta dividido en componentes pequenos:

- `Planner`: crea un plan inicial de investigacion para un tema.
- `Researcher`: ejecuta una busqueda, lee cada resultado y crea hallazgos.
- `SummaryBuilder`: genera titulo y sintesis deterministica como fallback si falla el LLM.
- `Reporter`: convierte el estado del agente en un `ResearchReport`.
- `ResearchWorkflow`: orquesta el caso de uso completo, carga memoria previa y guarda la nueva sintesis.
- `core/ports.py`: define contratos para busqueda, lectura de paginas y citas.
- `LLMResearchAssistant`: usa un LLM para extraer claims, generar titulo y sintetizar resumenes.
- `OllamaTextGenerator`: adaptador de Ollama via LangChain.
- `JsonResearchMemory`: implementa la memoria local en JSON detras de una interfaz de memoria.
- `WebSearchTool`: soporta proveedor `mock` y una ruta inicial para `tavily`.
- `WebPageReaderTool`: descarga paginas y extrae texto basico de HTML, con fallback si falla la red.
- `CitationExtractor`: deduplica fuentes desde el reporte y sus hallazgos.

Los modelos de datos principales estan en `src/core/schemas.py` y el estado compartido del agente esta en `src/core/state.py`.

## Estructura

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
    researcher.py
    reporter.py
    schemas.py
    state.py
    summarizer.py
  llm/
    ollama_client.py
    prompts.py
    research_assistant.py
  memory/
    store.py
    json_store.py
  tools/
    web_search.py
    webpage_reader.py
    citations.py
tests/
  test_core_flow.py
```

## Instalacion

Requiere Python 3.11 o superior.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Tambien puedes instalar desde `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Configuracion

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Variables previstas actualmente:

```env
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
LLM_PROVIDER=ollama
LLM_TEMPERATURE=0.2
DEFAULT_SEARCH_PROVIDER=mock
TAVILY_API_KEY=your_tavily_api_key_here
MEMORY_DIR=src/data/memory
REPORTS_DIR=src/data/outputs
```

Nota: la configuracion actual apunta a Ollama como proveedor de modelo local y usa resultados de busqueda simulados por defecto.
`TAVILY_API_KEY` solo es necesaria si cambias `DEFAULT_SEARCH_PROVIDER` a `tavily`.

## Ejemplo de uso

Actualmente no existe CLI ni punto de entrada ejecutable. Puedes probar el flujo con memoria desde Python:

```python
from src.application.factory import build_research_workflow

topic = "impacto de la IA en educacion"

workflow = build_research_workflow()
report = workflow.run(topic)

print(report.title)
print(report.summary)
print(report.findings)
```

## Pruebas

```bash
pytest -q
```

En este repo hay un `.venv` local; la suite se puede ejecutar con:

```bash
.venv/bin/python -m pytest -q
```

Como comprobacion sintactica basica:

```bash
python3 -m compileall src tests
```

## Que falta para que quede funcional

1. Agregar un punto de entrada real.
   - Falta una CLI, script o API que reciba un tema y ejecute `ResearchWorkflow`.
   - Ejemplos: `python -m src "tema"` o un comando tipo `research-agent "tema"`.

2. Implementar busqueda web real.
   - `WebSearchTool` ya tiene proveedor `mock` y una ruta inicial para Tavily.
   - Falta validar la integracion con credenciales reales y decidir si se usaran otros proveedores como DuckDuckGo, Bing o Google Custom Search.
   - Tambien falta manejar errores, limites de resultados, timeouts y credenciales.

3. Mejorar lectura de paginas.
   - `WebPageReaderTool` ya descarga contenido y limpia HTML basico con libreria estandar.
   - Falta extraccion mas robusta de articulo principal, titulo, fecha, autor y URL final.
   - Se podria usar `trafilatura`, `readability-lxml` o loaders de LangChain si se necesita mejor calidad.

4. Validar LLM en ejecucion real.
   - La capa LLM ya existe con `LLMResearchAssistant` y `OllamaTextGenerator`.
   - Falta probar Ollama levantado localmente, ajustar prompts con datos reales y decidir si se agregaran proveedores como OpenAI.

5. Definir el grafo del agente.
   - El `pyproject.toml` dice que el proyecto usa LangGraph, pero no hay grafo implementado.
   - Falta modelar nodos, transiciones, reintentos y estado persistente si se quiere un agente real.

6. Decidir proveedores reales y limpiar dependencias finales.
   - Hoy las dependencias soportan varias rutas posibles: Ollama, OpenAI, Hugging Face, Tavily y LangChain.
   - Cuando se elijan los providers definitivos, conviene eliminar paquetes no usados.

7. Generar reportes persistentes.
   - `reports_dir` existe en configuracion, pero no se usa.
   - Falta guardar Markdown/JSON/PDF con nombre estable, fecha y fuentes.

8. Mejorar citas.
   - `CitationExtractor` ya deduplica fuentes reales del reporte y de los hallazgos.
   - Falta generar referencias en formato Markdown/APA y asociar citas inline a cada claim.

9. Evolucionar la memoria.
   - La memoria local ya esta integrada en `ResearchWorkflow`.
   - Falta versionar entradas, guardar historial por ejecucion y resumir conversaciones largas con el LLM.

10. Endurecer tests.
    - Las pruebas actuales validan el flujo base, busqueda mock, lectura HTML, errores de red, deduplicacion de fuentes y memoria JSON.
    - Faltan tests de integracion para providers reales y generacion LLM.

## Prioridad recomendada

Para llevarlo a una primera version util:

1. Crear una CLI simple.
2. Guardar el reporte final en Markdown y JSON.
3. Validar busqueda real con Tavily u otro proveedor.
4. Mejorar el lector de paginas para extraer contenido principal.
5. Probar y ajustar prompts LLM con investigaciones reales.
6. Evolucionar memoria de resumen por tema a historial versionado.
