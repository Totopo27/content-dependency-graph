# Issue 01: Core Domain Schemas and Fixtures (Pydantic Models)

## Status: Ready
**Milestone**: M0  
**Blocked by**: None  

### Description
Implement the core domain schemas and data contracts using Pydantic. Ensure strict typing for videos, segments, concepts, and graph outputs. Create a synthetic test fixture mimicking transcript data for deterministic unit testing.

### Deliverables
1. `src/domain/models.py`:
   - `VideoMetadata`: id, title, published_at, duration.
   - `VideoSegment`: segment_id, video_id, start_time, end_time, transcript_text.
   - `ConceptExtraction`: concept_id, name, relation_type (`TEACHES` | `REQUIRES`), segment_id.
   - `CurriculumGraph`: nodes, edges, external_prerequisites.
2. `tests/fixtures/sample_channel_data.json`:
   - Curated mock dataset of 5 interconnected videos on basic and advanced backend concepts.
3. Unit test verifying schema serialization and deserialization.
