from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import items, quotations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quotation API")

# =========================
# CORS (FINAL WORKING)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ✅ allow all (dev fix)
    allow_credentials=False,      # ✅ MUST be False with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================
app.include_router(items.router)
app.include_router(quotations.router)

# =========================
# STATIC FILES
# =========================
app.mount(
    "/uploads",
    StaticFiles(directory="backend/uploads"),
    name="uploads"
)

@app.get("/")
def root():
    return {"message": "Quotation API running"}
