from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import keys, files, sessions

app = FastAPI(title="QuantumSafe VPN API")

# Tighten allow_origins to your deployed frontend URL before going live.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(keys.router)
app.include_router(files.router)
app.include_router(sessions.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
