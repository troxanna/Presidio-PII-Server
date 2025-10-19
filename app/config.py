# Config placeholder

from typing import Any, Dict

# spaCy model configuration for Presidio
NLP_CONFIG: Dict[str, Any] = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "ru", "model_name": "ru_core_news_lg"},
        {"lang_code": "en", "model_name": "en_core_web_lg"},
    ],
}


# Default anonymization policy (can be overridden per-request)
DEFAULT_POLICY: Dict[str, Dict[str, Any]] = {
    "default": {"type": "replace", "new_value": "[REDACTED]"},
    "PERSON": {"type": "replace", "new_value": "Иван Иванов"},
    "ORGANIZATION": {"type": "replace", "new_value": "Компания"},
    "LOCATION": {"type": "replace", "new_value": "Адрес"},
    "GPE": {"type": "replace", "new_value": "Адрес"},
    "EMAIL_ADDRESS": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "PHONE_NUMBER_RU": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "CREDIT_CARD": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_PASSPORT": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_SNILS": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_INN": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_OGRN": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_OGRNIP": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_BIK": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_RS": {"type": "mask", "chars_to_mask": 100, "from_end": False},
    "RU_KS": {"type": "mask", "chars_to_mask": 100, "from_end": False},
}