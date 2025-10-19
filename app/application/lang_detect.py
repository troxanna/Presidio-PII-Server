# Language detection placeholder
import os

def detect_language(text: str) -> str:
    """Detect language 'ru' or 'en' using fastText (optional), then langdetect, then script heuristic."""
    # 1) fastText if FASTTEXT_MODEL provided (e.g. /models/lid.176.bin)
    model_path = os.getenv("FASTTEXT_MODEL")
    if model_path and os.path.exists(model_path):
        try:
            import fasttext  # type: ignore
            model = fasttext.load_model(model_path)
            label = model.predict(text.replace("\n", " ")[:2000])[0][0]  # __label__ru
            lang = label.split("__label__")[-1]
            if lang.startswith("ru"): return "ru"
            if lang.startswith("en"): return "en"
        except Exception:
            pass
    # 2) langdetect fallback
    try:
        from langdetect import detect  # type: ignore
        lang = detect(text)
        if lang == "ru": return "ru"
        if lang == "en": return "en"
    except Exception:
        pass
    # 3) script heuristic
    if any("\u0400" <= ch <= "\u04FF" for ch in text):
        return "ru"
    return "en"
