# ADR 0002: Desacoplamiento entre Extracción Semántica y Normalización de Entidades

* **Estado**: Aceptado
* **Fecha**: 2026-10-08
* **Contexto**: Un creador puede referirse al mismo concepto con variaciones ortográficas, sinónimos o niveles de abstracción variables ("Postgres", "PostgreSQL", "Base de datos relacional"). Unificar todo en un solo prompt de LLM suele provocar alucinaciones de sinonimia o proliferación de nodos desconectados.

## Alternativas Evaluadas

1. **Extracción y Normalización en 2 Fases (Seleccionada)**:
   * *Fase A*: El LLM extrae los conceptos $C_{in}$ y $C_{out}$ crudos por segmento con sus timestamps exactos y descripciones contextuales.
   * *Fase B*: Paso determinista + clustering semántico (taxonomía canónica y embeddings vectoriales) que unifica variantes en un único `ConceptID` canónico antes de enlazar las aristas del grafo.
   * *Pros*: Alta trazabilidad, reduce errores de grafo desconectado, permite corrección manual de taxonomías sin reprocesar videos.
   * *Contras*: Requiere un paso intermedio de procesamiento por lote.
2. **Normalización en Prompt Único**:
   * *Pros*: Menor número de llamadas y menor tiempo de pipeline inicial.
   * *Contras*: Fragilidad de consistencia a través de decenas de videos procesados en llamadas independientes.

## Decisión

Implementar un flujo de **dos fases desacopladas**. La extracción produce un catálogo intermedio de conceptos crudos con timestamps; una capa de resolución de entidades unifica los identificadores antes de inyectarlos en `NetworkX`.

## Consecuencias

* Consistencia matemática y pedagógica en el grafo resultante.
* Facilidad para auditar y depurar cómo se mapeó cada término sin re-ejecutar la transcripción completa.
