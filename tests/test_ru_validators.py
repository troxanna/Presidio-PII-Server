import re

RU_SAMPLE = (
    "Иван Петров, ИНН 500100732259, СНИЛС 112-233-445 95, "
    "паспорт 45 08 123456, БИК 044525225, р/с 40702810900000000001, "
    "к/с 30101810400000000225, карта 4111 1111 1111 1111."
)


def test_ru_phone_number_is_detected(client):
    resp = client.post(
        "/analyze",
        json={"text": "телефон +7 (912) 000-00-00", "language": "ru"},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(item["entity_type"] == "PHONE_NUMBER_RU" for item in items)


def test_ru_phone_detected_inside_larger_text(client):
    text = (
        "Иван Иванов, паспорт 4012 345678 выдан 12.03.2015, телефон +7 (912) "
        "000-00-00"
    )

    resp = client.post("/analyze", json={"text": text, "language": "ru"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(item["entity_type"] == "PHONE_NUMBER_RU" for item in items)


def test_ru_phone_with_non_breaking_spaces(client):
    text = "телефон +7\u00A0(912)\u00A0000\u00A0\u00A000\u00A0\u00A000"

    resp = client.post("/analyze", json={"text": text, "language": "ru"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(item["entity_type"] == "PHONE_NUMBER_RU" for item in items)

def test_analyze_and_anonymize(client):
    # Analyze
    resp = client.post("/analyze", json={"text": RU_SAMPLE, "language": "ru"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    types = {i["entity_type"] for i in items}
    assert {"RU_PASSPORT", "RU_INN", "RU_SNILS"}.issubset(types)

    # Anonymize
    resp2 = client.post("/anonymize", json={"text": RU_SAMPLE, "language": "ru"})
    assert resp2.status_code == 200
    text = resp2.json()["text"]
    # ensure critical numbers are masked/replaced
    assert "500100732259" not in text
    assert re.search(r"\d{2}\s?\d{2}\s?\d{6}", text) is None


def test_generic_phone_numbers_are_detected_and_masked(client):
    text = "Call me at +1 (415) 555-2671 or +44 20 7946 0958 tomorrow."

    analyze = client.post("/analyze", json={"text": text, "language": "en"})
    assert analyze.status_code == 200
    items = analyze.json()["items"]
    assert any(item["entity_type"] == "PHONE_NUMBER" for item in items)

    anonymize = client.post("/anonymize", json={"text": text, "language": "en"})
    assert anonymize.status_code == 200
    masked_text = anonymize.json()["text"]
    assert "+1 (415) 555-2671" not in masked_text
    assert "+44 20 7946 0958" not in masked_text


def test_person_recognizer_detects_names(client):
    resp = client.post(
        "/analyze",
        json={"text": "Неводчикова Анастасия Анреевна", "language": "ru"},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(item["entity_type"] == "PERSON" for item in items)


def test_person_recognizer_rejects_nouns(client):
    resp = client.post(
        "/analyze",
        json={"text": "Коробка Стол Стул", "language": "ru"},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(item["entity_type"] != "PERSON" for item in items)
