# Content Dependency Graph

Motor de inferencia de grafos de dependencia pedagógica y rutas de aprendizaje a partir de transcripciones de video.

## Arquitectura y Módulos
* `src/domain/`: Modelos Pydantic y contratos de datos inmutables.
* `src/services/`: Extracción semántica, normalización y cálculo de grafos en NetworkX.
* `tests/`: Suite de pruebas unitarias con fixtures sintéticos.
