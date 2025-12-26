from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import items, quotations
from backend import auth

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(title="Quotation API")

# =========================
# CORS (ONLY ONCE)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://quotation-frontend-g74l.onrender.com",
        "https://quotation-frontend-1.onrender.com",
         "http://localhost:8080",
        "http://127.0.0.1:8080",
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
app.include_router(auth.router)        # 🔥 include auth first (important)
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
