FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt dev-requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends build-essential wget ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir -r requirements.txt -r dev-requirements.txt \
 && python -m spacy download ru_core_news_lg \
 && python -m spacy download en_core_web_lg
COPY . /app
EXPOSE 8000
# Optional: mount fastText model and set FASTTEXT_MODEL=/models/lid.176.bin
ENV FASTTEXT_MODEL=""
CMD ["uvicorn", "app.interface.api:app", "--host", "0.0.0.0", "--port", "8000"]
