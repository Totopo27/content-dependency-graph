# Documento de Diseño de Proyecto: Inferencia de Rutas de Aprendizaje en Canales de Contenido (Content Dependency Graph)

---

## 1. Resumen Ejecutivo (Executive Summary)

### El Problema
Las plataformas de video como YouTube organizan el contenido en orden **cronológico inverso**, diseñado para retener audiencias regulares, pero ineficiente para el aprendizaje estructurado. Cuando un usuario descubre a un creador educativo (por ejemplo, en programación, ciencia de datos o ingeniería de software), se enfrenta a barreras críticas:
* Carencia de un hilo conductor o secuencia lógica de aprendizaje.
* Pérdida de contexto pedagógico: videos avanzados asumen conocimientos o proyectos resueltos meses o años atrás sin enlaces explícitos.
* Listas de reproducción estáticas o desactualizadas curadas a mano por el creador.

### La Solución Propuesta
Un sistema automatizado de ingeniería inversa curricular que ingiere el catálogo completo de un canal, analiza sus transcripciones mediante Procesamiento de Lenguaje Natural (PLN) y Modelos de Lenguaje (LLMs), e infiere un **Grafo Dirigido Acíclico (DAG)** de prerrequisitos conceptuales. A partir de este grafo, el sistema genera:
1. **Roadmaps de aprendizaje personalizados** basados en el objetivo del espectador.
2. **Listas de prerrequisitos contextuales** para cualquier video dado (con timestamps).
3. **Mapas visuales e interactivos** de relaciones conceptuales del canal.

---

## 2. Estado del Arte y Ventana de Oportunidad

| Solución Existente | Ejemplos | Enfoque Actual | Brecha / Oportunidad |
| :--- | :--- | :--- | :--- |
| **Búsqueda Semántica / RAG en Video** | You-TLDR, ChatTube, SearchYoutube | Búsqueda puntual y resúmenes de videos específicos vía embeddings. | No calculan precedencia ni dependencias pedagógicas; carecen de noción de "orden curricular". |
| **Grafos de Literatura Académica** | Connected Papers, Litmaps, ResearchRabbit | Mapeo de artículos científicos y autores. | Dependen de citas bibliográficas formales. En video no existen citas normalizadas. |
| **Hojas de Ruta Curadas** | roadmap.sh | Guías estandarizadas curadas por humanos. | Requieren esfuerzo manual continuo; no se adaptan al archivo histórico de un canal específico. |

**Tesis de Valor:** No existe una herramienta popular que resuelva la **inferencia algorítmica de prerrequisitos** en discurso informal/didáctico audiovisual.

---

## 3. Arquitectura del Sistema

El flujo de procesamiento se divide en cuatro capas secuenciales:

```
[ Ingesta de Datos ]
        │
        ▼
[ Extracción Semántica (LLM) ]
        │
        ▼
[ Modelado del Grafo (DAG) ]
        │
        ▼
[ Capa de Consulta y Visualización ]
```

### 3.1. Capa de Ingesta y Transcripción
* **Metadatos:** Extracción de lista completa de videos (título, descripción, fecha de publicación, vistas, tags) vía YouTube Data API v3 o `yt-dlp`.
* **Transcripciones:**
  * Prioridad 1: Subtítulos oficiales o autogenerados mediante `youtube-transcript-api`.
  * Prioridad 2: En videos sin subtítulos disponibles, transcripción por audio vía modelos Whisper (ej. `whisper-large-v3` o APIs cloud de bajo costo).

### 3.2. Capa de Análisis Conceptual y Extracción de Relaciones
Para optimizar costos de cómputo, el análisis se realiza en dos etapas:

1. **Segmentación y Embeddings:**
   * Agrupación semántica previa de los videos mediante embeddings vectoriales (ej. `text-embedding-3-small` o modelos locales BGE) para identificar clusters temáticos (ej. "Frontend", "Bases de datos", "DevOps").
2. **Extracción Estructurada por Video:**
   * Mediante prompts estructurados (JSON Schema / Tool Calling), el LLM analiza transcripciones (por segmentos con timestamp) y extrae:
     * **Conceptos Enseña ($C_{out}$):** Conceptos que el autor explica a fondo o implementa desde cero.
     * **Conceptos Asume / Requiere ($C_{in}$):** Conceptos que el autor da por entendidos, menciona como base ("como vimos anteriormente...") o utiliza como herramientas preexistentes.

### 3.3. Capa de Grafo y Modelado de Dependencias
* **Estructura de Datos:** Base de datos orientada a grafos (ej. **Neo4j** o librerías en memoria como **NetworkX** para prototipos locales).
* **Nodos:** 
  * `Video` (atributos: id, título, fecha, duración, url).
  * `Concepto` (atributos: nombre normalizado, categoría).
* **Aristas:**
  * `(:Video)-[:ENSEÑA]->(:Concepto)`
  * `(:Video)-[:REQUIERE]->(:Concepto)`
* **Regla de Dependencia:**
  $$\text{Si } V_b \text{ REQUIERE } C_k \land V_a \text{ ENSEÑA } C_k \land \text{Fecha}(V_a) \le \text{Fecha}(V_b) \implies V_a \longrightarrow V_b$$
* **Algoritmos de Ruta:**
  * **Topological Sort:** Para ordenar los videos en una secuencia de estudio válida sin vacíos de conocimiento.
  * **Shortest Path / Ancestor Traversal:** Al seleccionar un video objetivo $V_{target}$, calcular el subárbol mínimo de videos que deben verse previamente.

### 3.4. Capa de Presentación / Visualización
* **Vista en Grafo:** Renderizado interactivo tipo red (utilizando React Flow, Cytoscape.js o Vis.js).
* **Vista Roadmap Lineal:** Estilo checklist o ruta paso a paso dividida por niveles (Básico $\rightarrow$ Intermedio $\rightarrow$ Avanzado).
* **Sidebar Contextual:** Extensión web que, al ver un video en YouTube, muestra: *"Para entender este video al 100%, te recomendamos ver antes estos 2 videos del mismo creador"*.

---

## 4. Retos Técnicos y Mitigaciones

1. **Resolución de Entidades y Normalización:**
   * *Problema:* Un creador puede referirse a la misma tecnología como "Postgres", "PostgreSQL" o "base de datos relacional".
   * *Mitigación:* Capa de normalización de entidades conceptuales basada en taxonomías predefinidas o desambiguación mediante LLM.
2. **Costo de Inferencia en Canales Grandes:**
   * *Problema:* Un canal con 500 videos puede superar los 15 millones de tokens.
   * *Mitigación:* Filtrado en dos pasos: primero analizar títulos, descripciones y resúmenes para descartar pares inconexos, y solo procesar transcripciones completas en segmentos relevantes.
3. **Manejo de Contenido Obsoleto:**
   * *Problema:* Un video de 2018 sobre React enseñando componentes de clase puede haber sido reemplazado por un video de 2022 sobre Hooks.
   * *Mitigación:* Atributo temporal y relación de tipo `(:Video_nuevo)-[:REEMPLAZA]->(:Video_viejo)`, priorizando siempre las versiones más recientes en el cálculo de la ruta.

---

## 5. Hoja de Ruta de Desarrollo Sugerida (Roadmap MVP)

- [ ] **Fase 1: Prueba de Concepto (Script local)**
  - Seleccionar un canal de prueba de tecnología con 30-50 videos temáticamente vinculados.
  - Extraer transcripciones con `youtube-transcript-api`.
  - Diseñar el prompt de extracción JSON para `$C_{in}$` y `$C_{out}$`.
- [ ] **Fase 2: Generación del Grafo**
  - Implementar script en Python con `NetworkX` para cruzar prerrequisitos y dependencias.
  - Exportar el resultado en formato JSON / GraphML.
- [ ] **Fase 3: Visualizador Web Básico**
  - Aplicación ligera en Next.js / React Flow para visualizar los nodos y permitir seleccionar un video objetivo con su ruta de estudio.
- [ ] **Fase 4: Generalización y Producto**
  - Automatizar el pipeline para procesar cualquier URL de canal de YouTube.
  - Implementación de cacheado y persistencia en base de datos.