from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Buscaí API", version="0.1.0")


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "healthy"})
