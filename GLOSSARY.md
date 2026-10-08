# GLOSSARY

Canonical domain vocabulary for the **Content Dependency Graph** system (curriculum reverse-engineering from educational content).

---

## Pedagogical & Content Domain

### Channel
* **Definition**: An author/creator content catalog representing the scope of educational material to be analyzed.
* **Context**: Top-level container of all available educational assets.

### Video
* **Definition**: A published video asset belonging to a channel, containing metadata (identifier, title, publication timestamp, duration, URL).
* **Context**: Serves as a media container; not the minimum atomic learning unit.

### Video Segment (Segment)
* **Definition**: An atomic, time-bounded section of a video (`start_time`, `end_time`, deep-link timestamp) where a specific concept is explained, implemented, or required.
* **Context**: The primary granular unit of pedagogical interaction and path recommendation.

### Concept
* **Definition**: An abstract topic, skill, tool, or theoretical notion that can be taught or required within educational discourse.
* **Context**: Standardized normalized label (e.g., `REST API`, `Async/Await`, `Relational Database`).

### Teaches ($C_{out}$)
* **Definition**: The pedagogical relationship indicating that a video segment explains a concept thoroughly, develops it from scratch, or provides clear instructional mastery.
* **Context**: A segment satisfies or provides this concept.

### Requires ($C_{in}$)
* **Definition**: The pedagogical relationship indicating that a video segment assumes familiarity with a concept, refers to it as already understood, or uses it as an unexplained dependency.
* **Context**: Must be satisfied by a preceding segment or identified as external.

### External Prerequisite (Out-of-Channel Prerequisite)
* **Definition**: A concept required ($C_{in}$) by one or more segments in the channel that is never taught ($C_{out}$) anywhere within the channel's history.
* **Context**: Flagged to the learner as assumed prior background knowledge so the dependency graph does not break.

### Content Dependency Graph (CDG)
* **Definition**: A Directed Acyclic Graph (DAG) whose nodes represent segments or concepts, and whose directed edges represent pedagogical precedence ($A \longrightarrow B$ means understanding $A$ is a prerequisite for understanding $B$).
* **Context**: Core data model calculated from channel transcripts.

### Learning Path (Curricular Roadmap)
* **Definition**: An ordered sequence of video segments obtained via topological sorting or ancestor graph traversal that prepares a learner to understand a target topic without unfulfilled internal prerequisites.
* **Context**: Generated dynamically based on the learner's chosen destination video or concept.

### Supersession / Replacement
* **Definition**: The pedagogical replacement of an outdated explanation by a more modern video segment covering the same concept within the same channel.
* **Context**: Solves deduplication and obsolescence by favoring recent explanations and cohesive series contexts.
