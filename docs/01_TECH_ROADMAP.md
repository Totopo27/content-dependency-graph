# 01_TECH_ROADMAP: Hoja de Ruta Técnica y Wayfinding

## Visión General de Arquitectura

El sistema se estructura en dos subsistemas principales desacoplados:
1. **Pipeline de Ingesta y Grafo (Python Core)**: Responsable de extraer transcripciones, estructurar conceptos mediante LLM, normalizar entidades y computar el Grafo Dirigido Acíclico (DAG) con NetworkX.
2. **Visualizador Web (Frontend Client)**: Aplicación web interactiva que consume el artefacto JSON del grafo, permitiendo navegación interactiva mediante React Flow y visualización de rutas de aprendizaje paso a paso.

---

## Contrato de Datos del Grafo (JSON Output Schema)

```json
{
  "channel_id": "string",
  "channel_title": "string",
  "generated_at": "ISO-8601",
  "nodes": [
    {
      "id": "segment-id | concept-id",
      "type": "video_segment | concept",
      "label": "string",
      "metadata": {
        "video_id": "string",
        "video_title": "string",
        "start_time": 0,
        "end_time": 0,
        "published_at": "ISO-8601",
        "external": false
      }
    }
  ],
  "edges": [
    {
      "source": "node-id",
      "target": "node-id",
      "relation": "TEACHES | REQUIRES | PREREQUISITE_OF"
    }
  ]
}
```

---

## Milestones de Desarrollo

### Milestone 0: Scaffolding, Contratos y Entorno de Pruebas (M0)
* Estructuración del repositorio y entornos de desarrollo.
* Modelos de datos Pydantic para `Video`, `Segment`, `Concept`, `GraphOutput`.
* Fixture con dataset controlado de prueba (transcripciones mockeadas de 5-10 videos para pruebas deterministas sin consumir APIs).

### Milestone 1: Ingesta y Extracción Semántica (M1)
* Extractor de transcripciones vía `youtube-transcript-api` con segmentación por tiempo/pausas temáticas.
* Pipeline de extracción de conceptos $C_{in}$ y $C_{out}$ con prompts estructurados (JSON Schema estricto).
* Capa de normalización de entidades (resolución de alias y sinonimia conceptual).

### Milestone 2: Motor de Grafo Curricular y Algoritmos de Ruta (M2)
* Construcción del grafo dirigido con `NetworkX`.
* Regla de dependencia cronológica y detección/ruptura de ciclos espurios.
* Algoritmo de cálculo de ruta pedagógica mínima (Topological Sort + subárbol de ancestros).
* Identificación y marcado de prerrequisitos externos huérfanos.
* Exportador serializado a JSON y GraphML.

### Milestone 3: Visualizador Interactivo en Frontend (M3)
* Proyecto React / Next.js configurado con Tailwind CSS y React Flow.
* Componentes de nodos customizados (`SegmentNode`, `ConceptNode`).
* Panel lateral de ruta de aprendizaje: selección de video objetivo $\rightarrow$ lista ordenada con timestamps clicables.
* Filtros de vista (Vista Grafo Global vs. Vista Ruta Paso a Paso).

---

## Niebla de Guerra (Fog of War / Post-MVP)
* Soporte para canales no técnicos o de debate informal donde los conceptos no siguen jerarquías estrictas.
* Integración con transcripción local continua mediante Whisper para videos sin subtítulos.
* Persistencia en base de datos multi-tenant y generación bajo demanda vía cola de tareas asíncronas (Celery / Redis).
