from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Smart Emergency Corridor",
    description="Emergency Route Optimization using A* and VQC",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {
        "project": "Smart Emergency Corridor",
        "message": "Backend is working successfully",
        "status": "success"
    }

@app.get("/api/status")
def get_status():
    return {
        "backend": "Connected",
        "simulation": "Not initialized",
        "vqc": "Not trained",
        "routing": "Not initialized"
    }