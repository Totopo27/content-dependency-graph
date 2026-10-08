# ADR 0003: Arquitectura Híbrida (Go Core Engine + Python Ingestion Worker)

* **Estado**: Aceptado
* **Fecha**: 2026-10-08
* **Contexto**: El sistema requiere ingesta de transcripciones de YouTube (ecosistema donde Python cuenta con librerías maduras como `youtube-transcript-api`), pero se beneficia enormemente de la concurrencia, tipado estricto, bajo consumo de memoria y facilidad de distribución que ofrece Go para el motor de dominio, cálculo de grafos y servidor API.

## Alternativas Evaluadas

1. **Python Monolítico**:
   * *Pros*: Desarrollo rápido y un solo runtime.
   * *Contras*: Mayor consumo de memoria, GIL complica el paralelismo nativo en servidores de alta concurrencia, distribución pesada.
2. **Go 100% Puro**:
   * *Pros*: Un único binario estático compilado.
   * *Contras*: La ingesta de subtítulos autogenerados en Go requiere reinventar clientes de YouTube, manejo de rotación de tokens o depender de APIs con cuotas muy restrictivas.
3. **Arquitectura Híbrida Hexagonal (Seleccionada)**:
   * **Go Engine (Core)**: Dominio estricto (`models`), algoritmos de DAG y ordenamiento topológico, motor de resolución de rutas, y servidor HTTP/JSON.
   * **Python Worker (Ingestión Específica)**: Script/sidecar quirúrgico y desacoplado enfocado exclusivamente en extraer transcripciones y serializar el catálogo a JSON estándar para consumo de Go.

## Decisión

Adoptar la **Arquitectura Híbrida**. El motor principal, el cálculo algorítmico y la API se desarrollarán en **Go**, mientras que la ingesta de YouTube se mantiene en un worker puntual en **Python**.

## Consecuencias

* Aprovechamiento de lo mejor de ambos ecosistemas sin forzar herramientas en áreas donde son débiles.
* El motor en Go es independiente de YouTube: puede procesar transcripciones de podcasts, cursos locales o cualquier otra fuente sin acoplamiento a Python.
* Facilidad de testing estricto con `go test` y compilación a binarios nativos rápidos.
