# Recognizers placeholder
from typing import List
from presidio_analyzer import Pattern, PatternRecognizer
from app.domain import entities as E

def build_ru_critical_recognizers() -> List[PatternRecognizer]:
    recs: List[PatternRecognizer] = []

    # Passport (series 4 digits + number 6 digits)
    recs.append(PatternRecognizer(
        supported_entity=E.RU_PASSPORT,
        patterns=[Pattern("russian_passport", r"\b\d{2}\s?\d{2}\s?\d{6}\b", 0.3)],
        context=["паспорт", "серия", "номер"],
        supported_language="ru",
    ))

    # SNILS
    recs.append(PatternRecognizer(
        supported_entity=E.RU_SNILS,
        patterns=[
            Pattern("snils_hyphen", r"\b\d{3}-\d{3}-\d{3}\s?\d{2}\b", 0.2),
            Pattern("snils_compact", r"(?<!\d)\d{11}(?!\d)", 0.05),
        ],
        context=["снилс"],
        supported_language="ru",
    ))

    # INN
    recs.append(PatternRecognizer(
        supported_entity=E.RU_INN,
        patterns=[Pattern("inn_10_12", r"(?<!\d)(?:\d{10}|\d{12})(?!\d)", 0.2)],
        context=["инн"],
        supported_language="ru",
    ))

    # OGRN/OGRNIP
    recs.append(PatternRecognizer(
        supported_entity=E.RU_OGRN,
        patterns=[Pattern("ogrn_13", r"(?<!\d)\d{13}(?!\d)", 0.15)],
        context=["огрн"],
        supported_language="ru",
    ))
    recs.append(PatternRecognizer(
        supported_entity=E.RU_OGRNIP,
        patterns=[Pattern("ogrnip_15", r"(?<!\d)\d{15}(?!\d)", 0.15)],
        context=["огрнип"],
        supported_language="ru",
    ))

    # Phone (RU)
    recs.append(PatternRecognizer(
        supported_entity=E.PHONE_RU,
        patterns=[Pattern("phone_ru", r"\b(?:\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}\b", 0.2)],
        context=["тел", "моб", "телефон"],
        supported_language="ru",
    ))

    # Email
    recs.append(PatternRecognizer(
        supported_entity=E.EMAIL,
        patterns=[Pattern("email_simple", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", 0.2)],
        context=["email", "e-mail", "почта"],
        supported_language=["ru", "en"],
    ))

    # Card PAN (13-19 digits) — needs Luhn in post-validation
    recs.append(PatternRecognizer(
        supported_entity=E.CARD,
        patterns=[Pattern("card_pan", r"\b(?:\d[ -]?){13,19}\b", 0.1)],
        context=["card", "карта", "visa", "mastercard"],
        supported_language=["ru", "en"],
    ))

    return recs


def build_ru_bank_recognizers() -> List[PatternRecognizer]:
    recs: List[PatternRecognizer] = []

    # BIK (9 digits)
    recs.append(PatternRecognizer(
        supported_entity=E.RU_BIK,
        patterns=[Pattern("bik_9", r"(?<![0-9])[0-9]{9}(?![0-9])", 0.1)],
        context=["бик"],
        supported_language="ru",
    ))

    # r/s (settlement account, 20 digits)
    recs.append(PatternRecognizer(
        supported_entity=E.RU_RS,
        patterns=[Pattern("rs_20", r"(?<![0-9])[0-9]{20}(?![0-9])", 0.05)],
        context=["р/с", "расчет", "расчёт", "счет", "счёт"],
        supported_language="ru",
    ))

    # k/s (correspondent account, 20 digits)
    recs.append(PatternRecognizer(
        supported_entity=E.RU_KS,
        patterns=[Pattern("ks_20", r"(?<![0-9])[0-9]{20}(?![0-9])", 0.05)],
        context=["к/с", "корр", "корреспондентский"],
        supported_language="ru",
    ))

    return recs
