from typing import List, Dict, Set
from pydantic import BaseModel, Field


class RawConceptTag(BaseModel):
    raw_name: str
    confidence: float = 1.0


class ExtractionResult(BaseModel):
    segment_id: str
    concepts_taught: List[RawConceptTag] = Field(default_factory=list)
    concepts_required: List[RawConceptTag] = Field(default_factory=list)


DEFAULT_ALIAS_MAP: Dict[str, str] = {
    # Bases de datos y SQL
    "postgres": "postgresql",
    "psql": "postgresql",
    "postgresql database": "postgresql",
    "sql query": "sql-basics",
    "structured query language": "sql-basics",
    "sql": "sql-basics",
    "rdbms": "relational-databases",
    "relational database": "relational-databases",
    # Web & HTTP
    "http": "http-basics",
    "http protocol": "http-basics",
    "http methods": "http-methods",
    "http verbs": "http-methods",
    "get and post": "http-methods",
    "rest": "rest-api-design",
    "restful": "rest-api-design",
    "rest api": "rest-api-design",
    "restful api": "rest-api-design",
    "json api": "json-api-endpoints",
    "json endpoints": "json-api-endpoints",
    # Seguridad & Criptografía
    "jwt": "jwt-authentication",
    "json web token": "jwt-authentication",
    "json web tokens": "jwt-authentication",
    "crypto hashing": "cryptographic-hashing",
    "hashing": "cryptographic-hashing",
    "hash functions": "cryptographic-hashing",
}


class ConceptNormalizer:
    def __init__(self, alias_map: Dict[str, str] = None):
        self.alias_map = alias_map or DEFAULT_ALIAS_MAP

    def normalize(self, term: str) -> str:
        """Normalizes a raw concept term into its canonical slug."""
        cleaned = term.strip().lower()
        if cleaned in self.alias_map:
            return self.alias_map[cleaned]
        # Slugification fallback for unseen terms
        slug = "-".join(cleaned.replace("_", " ").split())
        return slug

    def normalize_list(self, terms: List[str]) -> List[str]:
        """Normalizes a list of terms, deduplicating while preserving stable order."""
        seen: Set[str] = set()
        result: List[str] = []
        for term in terms:
            canonical = self.normalize(term)
            if canonical and canonical not in seen:
                seen.add(canonical)
                result.append(canonical)
        return result
