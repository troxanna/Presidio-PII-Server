import re

RU_SAMPLE = (
    "Иван Петров, ИНН 500100732259, СНИЛС 112-233-445 95, "
    "паспорт 45 08 123456, БИК 044525225, р/с 40702810900000000001, "
    "к/с 30101810400000000225, карта 4111 1111 1111 1111."
)

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
