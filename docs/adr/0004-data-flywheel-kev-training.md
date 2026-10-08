# ADR 0004: Estrategia de "Data Flywheel" para Entrenamiento Gradual de Kev (Sistema 1)

* **Estado**: Aceptado
* **Fecha**: 2026-10-08
* **Contexto**: El etiquetado rápido y tipado con Kev (Sistema 1) es el objetivo de alta eficiencia a largo plazo. Sin embargo, generar datasets sintéticos masivos por adelantado es costoso y artificial. Se requiere una estrategia evolutiva donde el sistema funcione hoy sin Kev pero capture datos reales orgánicos durante su uso para entrenarlo más adelante con pinzas y alta calidad.

## Decisión de Arquitectura: The Data Flywheel (Volante de Inercia de Datos)

Adoptar un pipeline en dos etapas:

1. **Etapa Operativa Activa (Bootstrapping)**:
   * El sistema utiliza marcadores heurísticos discursivos (conectores pedagógicos) combinados con inferencia local (modelos open-source pre-entrenados o LLMs locales).
   * Genera el grafo curricular y permite al usuario navegar las rutas de aprendizaje.

2. **Etapa Colectora Silenciosa (Dataset Collector)**:
   * Cada vez que un canal real es procesado y sus dependencias son validadas (sin ciclos y con enlaces lógicos verificados), el sistema exporta automáticamente una tupla tipada:
     ```json
     {
       "transcript_chunk": "...",
       "concept": "...",
       "label": "TEACHES | REQUIRES | NONE",
       "confidence": 0.95,
       "channel_domain": "farming | law | programming | gaming"
     }
     ```
   * Estos registros se acumulan en un almacén local de entrenamiento (`data/training_pool/`).

3. **Etapa de Entrenamiento de Kev (Destino Final)**:
   * Cuando el repositorio acumula miles de muestras orgánicas de múltiples canales y temas reales validados en producción, se ejecuta el fine-tuning de Kev.
   * Kev reemplaza progresivamente a los clasificadores más lentos, operando en sub-100ms con costo cero.

## Consecuencias

* **Cero bloqueo inicial**: El proyecto avanza de inmediato sin esperar la construcción de un dataset titánico.
* **Calidad de datos superior**: Los datos de entrenamiento provienen de discursos reales de creadores en YouTube y de grafos que ya demostraron ser coherentes en la práctica.
* **Multi-dominio natural**: El dataset crece de forma diversa a medida que los usuarios prueban canales de granjas, leyes, diseño, código o juegos.
