import logging
from inspect import signature
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from presidio_anonymizer import AnonymizerEngine

from app.application.lang_detect import detect_language
from app.application.service import (
    get_analyzer,
    get_anonymizer,
    post_validate,
    runtime_status,
)
from app.infrastructure.policies import get_default_policy, to_operator_config

app = FastAPI(title="Presidio RU+EN PII Server", version="1.3.0")


_ANONYMIZER_SUPPORTS_OPERATORS = "operators" in signature(AnonymizerEngine.anonymize).parameters
logger = logging.getLogger(__name__)

class AnalyzeRequest(BaseModel):
    text: str
    language: Optional[str] = Field(default=None, description="'ru' or 'en'")

class AnalyzeResponse(BaseModel):
    items: List[Dict[str, Any]]

class AnonymizeRequest(BaseModel):
    text: str
    language: Optional[str] = None
    policy: Optional[Dict[str, Dict[str, Any]]] = None

class AnonymizeResponse(BaseModel):
    text: str
    items: List[Dict[str, Any]]

@app.get("/health")
def health() -> Dict[str, Any]:
    status = runtime_status()
    overall = "ok"
    if status["nlp"].get("fallback_used"):
        overall = "degraded"
    elif not status["nlp"].get("initialized"):
        overall = "cold_start"
    return {"status": overall, **status}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(req: AnalyzeRequest):
    try:
        detection = detect_language(req.text, explicit_language=req.language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    language = detection.language
    logger.info("Analyze called with language %s via %s", language, detection.method)
    raw = get_analyzer().analyze(text=req.text, language=language)
    results = post_validate(req.text, raw)
    items = [{
        "entity_type": r.entity_type,
        "start": r.start,
        "end": r.end,
        "text": req.text[r.start:r.end],
        "score": r.score,
    } for r in results]
    return {"items": items}

@app.post("/anonymize", response_model=AnonymizeResponse)
def anonymize_endpoint(req: AnonymizeRequest):
    try:
        detection = detect_language(req.text, explicit_language=req.language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    language = detection.language
    logger.info("Anonymize called with language %s via %s", language, detection.method)
    raw = get_analyzer().analyze(text=req.text, language=language)
    results = post_validate(req.text, raw)
    policy = {**get_default_policy(), **(req.policy or {})}
    if _ANONYMIZER_SUPPORTS_OPERATORS:
        operators = to_operator_config(policy)
        out = get_anonymizer().anonymize(text=req.text, analyzer_results=results, operators=operators)
    else:  # pragma: no cover - exercised only when running against legacy Presidio versions
        out = get_anonymizer().anonymize(
            text=req.text, analyzer_results=results, anonymizers_config=policy
        )
    items = [{
        "entity_type": r.entity_type,
        "start": r.start,
        "end": r.end,
        "text": req.text[r.start:r.end],
        "score": r.score,
    } for r in results]
    return {"text": out.text, "items": items}
