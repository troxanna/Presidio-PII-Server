"""NLP engine helpers."""

import logging
from typing import Set

import spacy
from presidio_analyzer.nlp_engine import NlpEngine, NlpEngineProvider
from presidio_analyzer.nlp_engine.spacy_nlp_engine import SpacyNlpEngine

from app.config import NLP_CONFIG

logger = logging.getLogger(__name__)


def _blank_spacy_engine(languages: Set[str]) -> NlpEngine:
    """Create a spaCy NLP engine backed by blank language pipelines."""

    engine = SpacyNlpEngine(
        models=[{"lang_code": lang, "model_name": f"blank_{lang}"} for lang in sorted(languages)]
    )
    engine.nlp = {lang: spacy.blank(lang) for lang in languages}
    return engine


def create_nlp_engine() -> NlpEngine:
    """Create and return the spaCy-based NLP engine for Presidio."""

    provider = NlpEngineProvider(nlp_configuration=NLP_CONFIG)
    try:
        return provider.create_engine()
    except Exception as exc:  # pragma: no cover - fallback path depends on env
        logger.warning("Falling back to blank spaCy models: %s", exc)
        languages = {model["lang_code"] for model in NLP_CONFIG.get("models", [])}
        if not languages:
            languages = {"ru", "en"}
        return _blank_spacy_engine(languages)
