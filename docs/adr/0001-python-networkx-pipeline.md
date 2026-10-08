# ADR 0001: Arquitectura de Procesamiento y Modelado de Grafos

* **Estado**: Aceptado
* **Fecha**: 2026-10-08
* **Contexto**: El sistema requiere ingerir transcripciones de YouTube, procesarlas semánticamente con modelos de lenguaje y calcular rutas pedagógicas mediante algoritmos de grafos (ordenación topológica, detección de ciclos y recorrido de ancestros).

## Alternativas Evaluadas

1. **Python + NetworkX + Pydantic (Seleccionada)**:
   * *Pros*: Ecosistema maduro de NLP/ingesta (`youtube-transcript-api`), modelado determinista con Pydantic, algoritmos estándar de grafos en memoria sin latencia de red, cero costo de infraestructura adicional para el MVP.
   * *Contras*: NetworkX trabaja en memoria; no escala a millones de nodos de forma distribuida sin persistencia externa.
2. **Neo4j / Memgraph + Cypher**:
   * *Pros*: Motor de base de datos nativo para grafos grandes y consultas Cypher potentes.
   * *Contras*: Overhead operativo y de despliegue para una etapa inicial de prueba de concepto y validación de hipótesis.
3. **TypeScript / Node.js + Graphlib**:
   * *Pros*: Unificación de lenguaje con el frontend.
   * *Contras*: Menor madurez en librerías de extracción de subtítulos/scraping y manipulación algorítmica de grafos comparado con Python.

## Decisión

Adoptar **Python 3.11+ con NetworkX y Pydantic** para el pipeline de ingesta, normalización y cálculo de grafos. Exportar el grafo en formato JSON estandarizado para su consumo desacoplado por el cliente web.

## Consecuencias

* El núcleo algorítmico es reproducible localmente mediante scripts o CLI independientes.
* El frontend permanece completamente desacoplado del motor de cálculo de grafos.
* Migrar a Neo4j en una fase posterior será una tarea directa de exportación de aristas y nodos ya validados.
