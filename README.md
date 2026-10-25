# Asistente documental RAG

Prototipo de **generación aumentada por recuperación (RAG)** desarrollado en Python para consultar documentos internos y obtener respuestas respaldadas por fragmentos de esos documentos. La aplicación expone una API con **FastAPI**, almacena embeddings en **ChromaDB local** y utiliza un modelo de lenguaje a través de **Groq** para redactar las respuestas.

Los documentos de **NovaTech son ficticios y se utilizan exclusivamente como corpus de demostración**; no representan políticas de una empresa real.

## Funcionalidades

- Carga de archivos `.md`, `.txt` y `.pdf` **con texto extraíble** desde `documents/`.
- División del texto en fragmentos con solapamiento, conservando el archivo de origen y un identificador por fragmento.
- Generación local de embeddings multilingües y persistencia de vectores en ChromaDB.
- Recuperación por similitud coseno de los fragmentos más próximos a cada pregunta.
- Generación en español basada en la evidencia recuperada, con referencias numeradas a los fragmentos utilizados.
- Respuestas parciales cuando solo una parte de la pregunta está documentada y abstención cuando no existe evidencia suficiente.
- API de tres endpoints y documentación interactiva en Swagger, sin interfaz adicional.

## Arquitectura

El procesamiento se separa en **indexación**, que se ejecuta explícitamente cuando cambian los archivos, y **consulta**, que utiliza el índice previamente construido.

```text
INDEXACIÓN — POST /index

documents/ (.md, .txt, .pdf textual)
    │
    ▼
Carga y extracción de texto (document_loader.py)
    │
    ▼
Fragmentación y metadatos (chunker.py)
    │
    ▼
Embeddings locales (embeddings.py)
    │
    ▼
ChromaDB persistente (vector_store.py)
    │
    └── data/chroma/

CONSULTA — POST /ask

Pregunta
    │
    ▼
Embedding de la pregunta (retriever.py)
    │
    ▼
Búsqueda por similitud en ChromaDB
    │
    ▼
Fragmentos con texto, fuente, ID y distancia
    │
    ▼
Prompt con contexto numerado (llm_client.py)
    │
    ▼
LLM mediante Groq (API externa)
    │
    ▼
Respuesta + referencias y extractos (rag_service.py / main.py)
```

**Componentes y decisiones:**

| Componente | Implementación | Motivo |
|---|---|---|
| API | FastAPI, Pydantic y Uvicorn | Validación de solicitudes y Swagger integrado en `/docs`. |
| Lectura documental | `pathlib` y `pypdf` | Soporte sencillo para Markdown, TXT y PDF textual. |
| Chunking | Código Python propio; 400 caracteres y 60 de solapamiento por defecto | Control explícito del proceso; prioriza límites de oración cuando es posible. |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Representaciones multilingües locales, de 384 dimensiones, normalizadas. |
| Base vectorial | ChromaDB `PersistentClient`, colección `politicas_internas`, distancia coseno | Persistencia de vectores, textos e identificadores sin mantener un mapa externo como se requeriría con FAISS. |
| Generación | SDK `openai` con URL base compatible con Groq | LLM remoto configurable sin alojar un modelo generativo local. |
| Pruebas | `pytest`, `httpx` y `TestClient` | Verificación de componentes y contratos HTTP, con simulaciones para aislar dependencias. |

Se evitó introducir LangChain, LangGraph, Docker, agentes, servicios cloud o una segunda interfaz porque no eran necesarios para el alcance de este prototipo.

## Funcionamiento interno

**1. Carga y fragmentación.** `load_documents()` recorre los archivos compatibles de `documents/` en orden de nombre, sin buscar en subcarpetas. Para Markdown y TXT se lee UTF-8; para PDF se utiliza `pypdf` para extraer el texto disponible en sus páginas. `split_text()` normaliza los espacios en blanco y forma fragmentos de hasta **400 caracteres**, con un solapamiento configurado inicialmente en **60 caracteres**. Cuando es posible, se priorizan límites de oración; en otros casos se utilizan límites de palabra. `chunk_documents()` asigna un `chunk_id` ordinal y conserva `source` y `text`.

**2. Construcción del índice.** `generate_embeddings()` convierte los fragmentos en vectores normalizados utilizando `paraphrase-multilingual-MiniLM-L12-v2`; el modelo se reutiliza en el mismo proceso mediante caché. `index_chunks()` elimina la colección anterior, crea `politicas_internas` con métrica coseno y almacena explícitamente los vectores, textos, identificadores y metadatos de origen. Los datos se conservan en `data/chroma/` mediante `PersistentClient`.

**3. Recuperación.** En cada consulta, `retrieve()` genera el embedding de la pregunta utilizando **el mismo modelo** empleado para los documentos. `search_similar()` obtiene de ChromaDB hasta `top_k` resultados, ordenados por distancia, con su contenido y procedencia. No se aplica un umbral de relevancia calibrado: un fragmento cercano puede seguir siendo insuficiente para responder.

**4. Generación y referencias.** `generate_answer()` incorpora la pregunta y los fragmentos numerados al contexto enviado al LLM. El prompt solicita responder solo con la información suministrada, distinguir las partes documentadas de las no documentadas y citar referencias `[n]`. Tras recibir la respuesta, se comprueba que sus números de referencia pertenezcan a los fragmentos disponibles; en una abstención exacta se permiten `sources: []`. **No se realiza una verificación automática del respaldo semántico de cada afirmación**.

Esta separación permite comprobar por separado la búsqueda de fragmentos y la generación de texto. También facilita identificar si un error procede de la extracción, la fragmentación, la recuperación o la respuesta del modelo.

## Estructura del repositorio

```text
rag-asistente-documental/
├── app/
│   ├── __init__.py
│   ├── main.py              # Endpoints FastAPI
│   ├── schemas.py           # Modelos de solicitud y respuesta
│   ├── document_loader.py   # Lectura de MD, TXT y PDF textual
│   ├── chunker.py           # Fragmentación y metadatos
│   ├── embeddings.py        # Modelo de embeddings local
│   ├── vector_store.py      # Persistencia y consulta a ChromaDB
│   ├── retriever.py         # Recuperación por similitud
│   ├── llm_client.py        # Generación fundamentada y referencias
│   └── rag_service.py       # Orquestación del flujo de consulta
├── documents/
│   ├── politica_gastos_viajes.pdf
│   ├── politica_trabajo_remoto.md
│   └── politica_vacaciones.md
├── tests/                   # Pruebas automatizadas
├── resultados/
│   └── pruebas_funcionales.md
├── data/chroma/             # Generado localmente; no se versiona
├── .env.example             # Plantilla de configuración sin clave
├── .gitignore
├── requirements.txt
└── README.md
```

> `data/chroma/`, `.venv/` y `.env` son recursos locales excluidos de Git. El índice se reconstruye a partir de los documentos versionados; **no** es necesario compartir ni versionar una copia de la base vectorial local.

## Requisitos

- **Windows con Python 3.12**; entorno de desarrollo utilizado: Python **3.12.10**, VS Code y Git Bash.
- Acceso a Internet para instalar dependencias, descargar inicialmente el modelo de embeddings y consultar el LLM.
- Una **clave de API válida del proveedor configurado** (en las pruebas se utilizó Groq).
- Dependencias declaradas en [`requirements.txt`](requirements.txt).

Se comprobó el funcionamiento en un entorno local de desarrollo. **Todavía no se ha verificado una instalación completa desde un clon limpio**, y `requirements.txt` no fija versiones exactas. Los comandos siguientes describen el procedimiento de instalación previsto; no representan una garantía de reproducibilidad binaria en cualquier equipo.

## Instalación y configuración (Git Bash en Windows)

1. Se clona el repositorio desde la URL facilitada para la prueba y se abre Git Bash en la carpeta raíz `rag-asistente-documental/`. Si el repositorio ya está descargado, se utiliza esa carpeta directamente.

2. Se crea y activa el entorno virtual:

   ```bash
   py -3.12 -m venv .venv
   source .venv/Scripts/activate
   python --version
   ```

3. Se instalan las dependencias:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Se crea el archivo local de configuración:

   ```bash
   cp .env.example .env
   ```

   Se edita `.env` **únicamente en el equipo local**, asignando una clave real a `LLM_API_KEY`. La plantilla contiene estas variables:

   ```dotenv
   LLM_API_KEY=
   LLM_BASE_URL=https://api.groq.com/openai/v1
   LLM_MODEL=openai/gpt-oss-20b
   ```

   **La clave real no debe incluirse en Git, capturas, videos, mensajes ni archivos compartidos.** El proveedor y el modelo se configuran desde este archivo; el modelo de embeddings y la ubicación de ChromaDB están definidos actualmente en el código Python.

5. Se inicia la aplicación **desde la raíz del repositorio**:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

   Se accede a Swagger desde **http://127.0.0.1:8000/docs**. `--reload` se utiliza en desarrollo local. La primera indexación puede requerir la descarga del modelo de Sentence Transformers.

## Cargar e indexar documentos

La API **no recibe archivos mediante un formulario ni mediante un endpoint de subida**. Para agregar o cambiar documentos:

1. Se colocan los archivos compatibles (`.md`, `.txt` o `.pdf` textual) directamente en `documents/`. Los Markdown y TXT deben poder leerse como UTF-8; los PDF escaneados sin capa de texto no están soportados.
2. Desde Swagger, se ejecuta **`POST /index`** sin cuerpo de solicitud.
3. Al finalizar, el endpoint habrá leído los archivos compatibles, generado sus fragmentos y embeddings y **reemplazado** la colección de ChromaDB.
4. Durante la reconstrucción no deben ejecutarse consultas ni otra indexación de forma simultánea.

Con el corpus NovaTech definitivo y el chunker actualizado, el resultado real observado fue:

```json
{
  "documents": 3,
  "chunks": 19
}
```

La cantidad de fragmentos puede cambiar si se modifican los documentos o el algoritmo. La carpeta se procesa de forma **no recursiva** y los formatos no compatibles se omiten.

## Consultar el asistente

Después de indexar, se abre **`POST /ask`** desde Swagger y se envía un JSON como este:

```json
{
  "question": "¿En qué plazo deben presentarse los comprobantes de gastos de viaje y quién aprueba el reembolso?",
  "top_k": 3
}
```

- `question`: texto obligatorio entre **1 y 1000 caracteres**; no admite solo espacios.
- `top_k`: cantidad de fragmentos solicitados, **entero positivo**. El valor predeterminado del código es **4**; en las tres pruebas funcionales definitivas se indicó **3** explícitamente. No se ha demostrado que 3 sea óptimo para todas las preguntas.

La respuesta contiene `question`, `answer` y `sources`. Cada fuente citada informa `reference`, `source`, `chunk_id`, `excerpt` y `distance`.

Por ejemplo, esta fue la **respuesta real de abstención** obtenida en la evaluación:

```json
{
  "question": "¿Cuál es el salario promedio de los empleados de NovaTech?",
  "answer": "No encuentro información suficiente en los documentos para responder.",
  "sources": []
}
```

Una referencia `[1]` identifica el primer fragmento numerado que recibió el modelo en esa consulta; no significa necesariamente el primer fragmento del documento. La **distancia coseno** indica proximidad en el espacio vectorial: menor distancia implica mayor cercanía, **no** una probabilidad de certeza ni prueba suficiente de que el fragmento respalde cada afirmación.

### Endpoints y errores principales

| Método y ruta | Propósito | Respuesta o condición |
|---|---|---|
| `GET /health` | Comprobar que responde la API | `200` → `{"status":"ok"}`. No comprueba la disponibilidad de Groq ni el estado del índice. |
| `POST /index` | Leer `documents/` y reconstruir ChromaDB | `200` con `documents` y `chunks`; `404` si falta la carpeta; `400` cuando no hay documentos válidos o ocurre un `ValueError` de carga controlado. |
| `POST /ask` | Ejecutar recuperación y generación | `200` con pregunta, respuesta y fuentes; `422` por solicitud inválida; `409` si el índice está vacío; `503` ante errores del proveedor cubiertos por `openai.APIError`. |
| `GET /docs` | Abrir Swagger UI | Documentación y ejecución interactiva de la API. |

No existe un manejo uniforme para todos los fallos posibles de PDF, almacenamiento, embeddings o configuración; pueden presentarse errores no controlados. La API es local y **no incorpora autenticación**, por lo que no debe exponerse públicamente tal como está.

## Pruebas y resultados

### Pruebas automatizadas

Desde la raíz del repositorio, con el entorno virtual activado, se ejecuta:

```bash
python -m pytest -q
```

La última ejecución comunicada durante P6 tuvo **28 pruebas aprobadas**. Estas pruebas comprueban lógica de carga, fragmentación, almacenamiento, recuperación, orquestación y contratos HTTP. Algunas utilizan dobles de prueba o simulaciones; **no equivalen a 28 llamadas reales a Groq** ni a una medición de exactitud del modelo.

### Evaluación funcional con el LLM real

Se realizaron las tres consultas obligatorias en Swagger con **`top_k=3`** y el corpus de 3 documentos y 19 fragmentos:

| Escenario | Pregunta resumida | Evaluación manual |
|---|---|---|
| Respondible | Plazo y responsable de aprobación del reembolso | **Correcta**: cinco días hábiles posteriores al viaje y aprobación del responsable administrativo, con fragmentos citados del PDF. |
| Parcial | Trabajar tres meses desde otro país y medidas de seguridad | **Correcta con observaciones**: reconoce que la autorización internacional prolongada no está definida y responde varias medidas de seguridad. Omite otras medidas y utiliza una expresión ligeramente más restrictiva sobre la VPN. |
| Fuera del corpus | Salario promedio de NovaTech | **Correcta**: se abstiene de dar cifras y devuelve `sources: []`. |

Las **preguntas literales, respuestas JSON completas, identificadores de fragmento, distancias, evaluación manual e incidencias de la implementación** están en [`resultados/pruebas_funcionales.md`](resultados/pruebas_funcionales.md). Son resultados de tres casos concretos, no un estudio estadístico ni una garantía de ausencia de alucinaciones.

## Limitaciones conocidas

- **Cobertura documental:** solo PDF con texto seleccionable; no OCR, extracción de tablas avanzada, subcarpetas recursivas ni citas por página.
- **Recuperación:** se usa similitud vectorial sin búsqueda híbrida, reranking ni umbral de distancia calibrado. Chroma devuelve vecinos cercanos aunque su contenido no permita contestar la pregunta.
- **Generación y citas:** el prompt solicita basarse exclusivamente en el contexto y abstenerse cuando corresponda. El programa comprueba la validez numérica de las citas, **no** que todas las afirmaciones estén semánticamente justificadas. La redacción puede variar entre ejecuciones incluso con temperatura 0.
- **Chunking:** heurístico por tamaño, solapamiento y límites de oración; no garantiza preservar íntegramente toda unidad semántica o todos los detalles relevantes.
- **Reindexación:** borra y recrea la colección actual; no es atómica y una falla durante el proceso puede dejar el índice incompleto. Por ello, no se recomienda reindexar mientras se responde a preguntas.
- **Operación y seguridad:** prototipo local sin autenticación, permisos por usuario, interfaz de subida ni despliegue productivo. Los fragmentos recuperados se envían al proveedor externo del LLM.
- **Dependencias y errores:** `requirements.txt` no fija versiones; no está verificada una instalación completa desde un clon nuevo y el manejo de excepciones cubre solo casos seleccionados.

## Mejoras futuras

En una evolución posterior se podría incorporar un conjunto más amplio de preguntas para medir recuperación y calidad de citas, calibrar criterios de abstención, añadir pruebas de regresión para PDF y chunking, fijar versiones compatibles de dependencias y hacer la reindexación más segura. Para documentos más heterogéneos, también tendría sentido evaluar OCR, búsqueda híbrida y fragmentación por estructura. Una eventual publicación en la nube exigiría autenticación, protección de datos y almacenamiento persistente adecuado; ninguna de estas capacidades se presenta como implementada.

## Uso responsable de herramientas de IA

Durante el desarrollo se utilizó **ChatGPT como herramienta de apoyo**, con revisión del código y comprobación de los resultados en el entorno local. La asistencia de IA se documenta para distinguir las propuestas recibidas de las decisiones y verificaciones realizadas durante la implementación.

- **Para qué se utilizó:** se empleó para analizar el enunciado, contrastar alternativas de arquitectura, elaborar propuestas de módulos y pruebas, preparar documentos ficticios y documentación, y apoyar el diagnóstico de incidencias relacionadas con la recuperación, el chunking y las respuestas parciales.
- **Qué se revisó manualmente:** se configuró el entorno de Python y Git Bash, se examinaron e integraron los módulos, se instalaron dependencias, se ejecutaron las pruebas con `pytest`, se verificó la persistencia de ChromaDB, se reconstruyó el índice, se probaron consultas reales desde Swagger y se revisaron los fragmentos citados. También se registraron las modificaciones mediante Git y se publicaron los cambios en el repositorio.
- **Qué se aprendió:** se comprobó que una distancia vectorial baja no garantiza evidencia suficiente; se identificó cómo un corte incorrecto puede alterar el sentido de una negación; se distinguió la abstención total de una respuesta parcialmente documentada; se reconoció que validar referencias numéricas no equivale a comprobar su respaldo semántico; y se diferenció la utilidad de las pruebas simuladas frente a las validaciones con el proveedor LLM real.

Las respuestas y sus evaluaciones se registraron a partir de ejecuciones reales. **No se sustituyeron las salidas observadas por ejemplos simulados**. Se mantuvo un alcance técnico deliberadamente acotado para facilitar la comprensión, la verificación y la explicación del RAG.

## Material de entrega

- **Código y corpus:** este repositorio.
- **Evaluación funcional:** [`resultados/pruebas_funcionales.md`](resultados/pruebas_funcionales.md).