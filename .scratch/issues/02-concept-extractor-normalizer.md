# Issue 02: Semantic Concept Extractor & Normalizer

## Status: Ready
**Milestone**: M1  
**Blocked by**: Issue 01 (Domain Schemas)  

### Description
Implement the structured concept extraction service that receives video segment transcripts and outputs structured lists of taught ($C_{out}$) and required ($C_{in}$) concepts. Implement the entity normalization layer to harmonize variants into canonical concepts.

### Deliverables
1. `src/services/extractor.py`:
   - Prompt engineering and JSON Schema enforcement with LLM integration.
   - Fallback and validator for malformed responses.
2. `src/services/normalizer.py`:
   - Mapping catalog of aliases (e.g. `PostgreSQL` -> `postgres`, `REST` -> `rest-api`).
   - Deduplication function for extracted concepts.
3. Unit tests with fixture data verifying that concepts are cleanly extracted and normalized without hallucinations.
