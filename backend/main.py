from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.database import Base, engine
from backend.routers import items, quotations

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quotation API")

# Routers
app.include_router(items.router)
app.include_router(quotations.router)

# Serve uploaded images
app.mount(
    "/uploads",
    StaticFiles(directory="backend/uploads"),
    name="uploads"
)


@app.get("/")
def root():
    return {"message": "Quotation API running"}
