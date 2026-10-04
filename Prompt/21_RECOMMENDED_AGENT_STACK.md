# Recommended Technical Stack

## Data / Science
- Python 3.11+
- pandas
- numpy
- scipy
- scikit-learn
- xgboost/lightgbm only if justified
- pydantic

## Retrieval
- structured SQL/Parquet queries first
- sentence-transformers or hosted embeddings for text
- FAISS/Chroma/Qdrant as appropriate
- reranking when needed

## Backend
- FastAPI
- Uvicorn
- Pydantic

## Frontend
- Next.js or React
- TypeScript
- Plotly/ECharts
- optional Three.js for scientific visualizations

## Testing
- pytest
- Playwright for frontend E2E

## Reproducibility
- requirements.txt / uv / poetry
- fixed random seeds
- model metadata
- dataset hashes
