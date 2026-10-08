# 00_DISCOVERY: Inferencia de Rutas de Aprendizaje en Canales de Video

## 1. Problema de Negocio y Visión

Las plataformas de streaming educativo organizan el contenido en orden cronológico inverso o por engagement algorítmico. Esto produce:
* Pérdida de secuencia pedagógica lógica.
* Videos avanzados con prerrequisitos implícitos que no están explicitados ni enlazados.
* Fricción y deserción en estudiantes que intentan aprender habilidades complejas en canales educativos existentes.

**Tesis de Valor**:  
Construir un motor de ingeniería inversa curricular que analice el catálogo de un canal educativo, extraiga conceptos enseñados y asumidos a nivel de segmento temporal, y genere un **Grafo Dirigido Acíclico (DAG)** con rutas óptimas de aprendizaje personalizadas.

---

## 2. Actores y Roles

* **Estudiante / Aprendiz**:
  * Desea llegar a dominar un video o concepto destino ($V_{target}$ o $C_{target}$).
  * Requiere saber exactamente qué ver antes (y qué minuto exacto) sin perder tiempo en explicaciones redundantes o desactualizadas.
* **Creador Educativo / Docente** *(Consumidor secundario)*:
  * Desea auditar la coherencia curricular de su canal, detectar conceptos huérfanos y descubrir vacíos formativos en su catálogo.
* **Operador del Sistema**:
  * Ingiere canales, ejecuta el pipeline de extracción y genera/publica el grafo curricular.

---

## 3. Reglas de Dominio Fundamentales

1. **Granularidad Atómica**:
   * La unidad de recomendación pedagógica es el **Segmento de Video** (`Video Segment` con `start_time` y `end_time`), no el video completo.
2. **Deduplicación y Obsolescencia**:
   * Si un concepto $C_k$ es enseñado en múltiples segmentos a lo largo del tiempo, la selección prioriza:
     1. **Recencia temporal**: versiones más modernas reemplazan explicaciones obsoletas para tecnologías mutables.
     2. **Cohesión de serie/contexto**: preferencia por segmentos pertenecientes a la misma serie o lista de reproducción activa.
3. **Resiliencia ante Prerrequisitos Externos**:
   * Todo concepto requerido ($C_{in}$) que no cuente con un segmento proveedor ($C_{out}$) en el canal se clasifica como `Prerrequisito Externo`.
   * El sistema notifica al estudiante sobre esta base previa sin romper la continuidad del grafo ni el ordenamiento topológico.
4. **Aciclicidad Pedagógica**:
   * Las dependencias deben resolver un Grafo Dirigido Acíclico (DAG). Si el discurso informal genera bucles circunstanciales ($A$ requiere $B$ y $B$ menciona $A$), el grafo resuelve la precedencia usando orden cronológico y jerarquía conceptual.

---

## 4. Alcance del Sistema

### In Scope (MVP)
* Ingesta de catálogos y transcripciones de prueba (canales tecnológicos de 30-50 videos con subtítulos preexistentes en español o inglés).
* Extracción semántica estructurada de conceptos enseñados ($C_{out}$) y requeridos ($C_{in}$) con timestamps.
* Normalización de entidades conceptuales y resolución de sinonimia ("Postgres" vs "PostgreSQL").
* Modelado del DAG de dependencias y cálculo de caminos de aprendizaje (Topological Sort / Ancestor Traversal).
* Exportación estructurada (JSON / GraphML) y visualizador interactivo local del grafo y de la ruta paso a paso.

### Out of Scope (Post-MVP)
* Transcripción masiva de audio crudo con modelos Whisper en GPU pesada.
* Extensión de navegador web para inyección en tiempo real en youtube.com.
* Soporte multi-plataforma (Twitch, TikTok, podcasts de audio).
* Cuentas de usuario, pasarelas de pago y autenticación multi-tenant.

---

## 5. Historias de Usuario Críticas

### US-01: Extracción de Prerrequisitos por Segmento
* **Como** Estudiante,
* **Quiero** seleccionar un video específico que deseo aprender,
* **Para** recibir la lista exacta de segmentos previos del canal que debo ver antes para no perderme en la explicación.
* **Criterios de Aceptación**:
  * *Dado* un video objetivo $V$,
  * *Cuando* el sistema calcula sus prerrequisitos,
  * *Entonces* devuelve una lista ordenada de segmentos con título, timestamp de inicio/fin y el concepto específico que cubre.

### US-02: Identificación de Conceptos Externos
* **Como** Estudiante,
* **Quiero** ver con claridad qué conocimientos se asumen que el canal nunca explicó,
* **Para** saber si necesito repasar fundamentos externos antes de comenzar la ruta.
* **Criterios de Aceptación**:
  * *Dado* un conjunto de conceptos requeridos en un video,
  * *Cuando* ninguno de ellos tiene arista $C_{out}$ en el canal,
  * *Entonces* se listan bajo la categoría "Prerrequisitos Externos Sugeridos".

### US-03: Visualización Interactiva del Grafo del Canal
* **Como** Estudiante o Docente,
* **Quiero** explorar un mapa visual interactivo de los conceptos y videos del canal,
* **Para** entender cómo se conectan los temas entre sí y qué áreas del canal son troncales.
* **Criterios de Aceptación**:
  * *Dado* el análisis completo de un canal,
  * *Cuando* abro el visualizador,
  * *Entonces* veo los nodos (conceptos/segmentos), sus conexiones direccionales y puedo filtrar la ruta hacia cualquier nodo destino.
