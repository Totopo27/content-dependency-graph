from src.services.normalizer import ConceptNormalizer
from src.services.extractor import ConceptExtractionService


def test_concept_normalizer_aliases():
    normalizer = ConceptNormalizer()

    assert normalizer.normalize("PostgreSQL database") == "postgresql"
    assert normalizer.normalize("POSTGRES") == "postgresql"
    assert normalizer.normalize("RESTful API") == "rest-api-design"
    assert normalizer.normalize("JSON web token") == "jwt-authentication"


def test_concept_normalizer_deduplication():
    normalizer = ConceptNormalizer()
    raw_list = ["Postgres", "postgresql database", "SQL Query", "SQL"]
    normalized = normalizer.normalize_list(raw_list)

    assert normalized == ["postgresql", "sql-basics"]


def test_concept_extraction_service_processing():
    service = ConceptExtractionService()
    raw_llm_output = {
        "start_time": 120,
        "end_time": 300,
        "transcript_text": "En este segmento conectamos REST con Postgres.",
        "concepts_taught": [{"raw_name": "RESTful API"}, "json api"],
        "concepts_required": ["HTTP Protocol", {"raw_name": "Postgres"}],
    }

    segment = service.process_raw_extraction("seg_test_01", raw_llm_output)

    assert segment.segment_id == "seg_test_01"
    assert segment.duration == 180
    assert segment.concepts_taught == ["rest-api-design", "json-api-endpoints"]
    assert segment.concepts_required == ["http-basics", "postgresql"]
