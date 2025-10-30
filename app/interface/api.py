# FastAPI endpoints placeholder
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

from inspect import signature

from app.application.service import analyzer, anonymizer, post_validate
from app.application.lang_detect import detect_language
from app.infrastructure.policies import get_default_policy, to_operator_config

app = FastAPI(title="Presidio RU+EN PII Server", version="1.3.0")


_ANONYMIZER_SUPPORTS_OPERATORS = "operators" in signature(anonymizer.anonymize).parameters

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
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(req: AnalyzeRequest):
    language = req.language or detect_language(req.text)
    print(f"Analyze called with language: {language}")
    raw = analyzer.analyze(text=req.text, language=language)
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
    language = req.language or detect_language(req.text)
    print(f"Anonymize called with language: {language}")
    raw = analyzer.analyze(text=req.text, language=language)
    results = post_validate(req.text, raw)
    policy = {**get_default_policy(), **(req.policy or {})}
    if _ANONYMIZER_SUPPORTS_OPERATORS:
        operators = to_operator_config(policy)
        out = anonymizer.anonymize(text=req.text, analyzer_results=results, operators=operators)
    else:  # pragma: no cover - exercised only when running against legacy Presidio versions
        out = anonymizer.anonymize(
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
