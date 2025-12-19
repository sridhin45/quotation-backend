from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import items, quotations

app = FastAPI(title="Quotation API")

# =========================
# CORS (ONLY ONCE)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://quotation-frontend-g74l.onrender.com",   # YOUR FRONTEND
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DATABASE
# =========================
Base.metadata.create_all(bind=engine)

# =========================
# ROUTERS
# =========================
app.include_router(items.router)
app.include_router(quotations.router)

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"message": "Quotation API running"}

@app.get("/cors-test")
def cors_test():
    return {"cors": "working"}
