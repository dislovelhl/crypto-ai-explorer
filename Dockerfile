FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/x402-api/ ./services/x402-api/
COPY scripts/ ./scripts/

EXPOSE 8402

CMD ["uvicorn", "services.x402-api.server:app", "--host", "0.0.0.0", "--port", "8402"]
