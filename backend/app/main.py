from fastapi import FastAPI

app = FastAPI(title="Personal Finance Intelligence API")


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}
    