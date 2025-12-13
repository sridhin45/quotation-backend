from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import items, quotations

# =========================
# CREATE DB TABLES
# =========================
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quotation API")

# =========================
# CORS CONFIG (REQUIRED)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",     # Angular local
        "http://127.0.0.1:4200",
        "https://your-frontend-domain.com",  # optional prod frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================
app.include_router(items.router)
app.include_router(quotations.router)

# =========================
# STATIC FILES (IMAGES)
# =========================
app.mount(
    "/uploads",
    StaticFiles(directory="backend/uploads"),
    name="uploads"
)

# =========================
# ROOT CHECK
# =========================
@app.get("/")
def root():
    return {"message": "Quotation API running"}
