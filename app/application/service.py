# Service placeholder
from typing import List
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, RecognizerResult
from presidio_anonymizer import AnonymizerEngine

from app.infrastructure.nlp import create_nlp_engine
from app.infrastructure.recognizers import build_ru_critical_recognizers, build_ru_bank_recognizers
from app.domain.validators import (
    luhn_ok, snils_checksum_ok, inn_checksum_ok, ogrn_checksum_ok,
    bik_ok, account_checksum_ok, find_all_biks,
)
from app.domain import entities as E

# Build engines & registry as singletons
_nlp_engine = create_nlp_engine()
_registry = RecognizerRegistry()
_registry.load_predefined_recognizers(nlp_engine=_nlp_engine)

# Add custom recognizers
for r in build_ru_critical_recognizers() + build_ru_bank_recognizers():
    _registry.add_recognizer(r)

analyzer = AnalyzerEngine(nlp_engine=_nlp_engine, registry=_registry, supported_languages=["ru", "en"])
anonymizer = AnonymizerEngine()

def post_validate(text: str, results: List[RecognizerResult]) -> List[RecognizerResult]:
    """Apply checksum/context validation and dedupe results."""
    validated: List[RecognizerResult] = []
    biks_in_text = [b for b in find_all_biks(text) if bik_ok(b)]

    for r in results:
        et = r.entity_type
        span = text[r.start:r.end]

        # Filter noisy low-score ML entities
        if et in {E.PERSON, E.ORG, E.LOC, E.GPE} and (r.score is not None and r.score < 0.55):
            continue

        # Structured checks
        if et == E.RU_SNILS and not snils_checksum_ok(span):
            continue
        if et == E.RU_INN and not inn_checksum_ok(span):
            continue
        if et in {E.RU_OGRN, E.RU_OGRNIP} and not ogrn_checksum_ok(span):
            continue
        if et == E.CARD and not luhn_ok(span):
            continue
        if et == E.RU_PASSPORT:
            digits = ''.join(ch for ch in span if ch.isdigit())
            if len(digits) != 10 or set(digits) == {"0"}:
                continue
        if et in {E.RU_RS, E.RU_KS}:
            if not biks_in_text:
                continue
            is_corr = (et == E.RU_KS)
            if not any(account_checksum_ok(span, b, is_corr=is_corr) for b in biks_in_text):
                continue
        if et == E.RU_BIK and not bik_ok(span):
            continue

        validated.append(r)

    # dedupe by (start, end, type)
    seen, out = set(), []
    for r in validated:
        key = (r.start, r.end, r.entity_type)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out
