FROM python:3.12-slim
WORKDIR /srv/flare-x
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 flare
COPY src/ src/
COPY app/ app/
COPY project-page/ project-page/
COPY cache/ cache/
COPY models/ models/
COPY data/metadata/ data/metadata/
USER flare
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT', '8000') + '/health', timeout=4)"
CMD ["sh", "-c", "exec python -m uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
