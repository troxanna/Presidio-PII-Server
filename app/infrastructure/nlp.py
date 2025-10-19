# NLP engine placeholder
from presidio_analyzer.nlp_engine import NlpEngineProvider
from app.config import NLP_CONFIG

def create_nlp_engine():
    """Create and return the spaCy-based NLP engine for Presidio."""
    provider = NlpEngineProvider(nlp_configuration=NLP_CONFIG)
    return provider.create_engine()