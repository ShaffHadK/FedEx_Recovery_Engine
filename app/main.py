from fastapi import FastAPI
from app.routes import router
from services.allocation_service import load_dca_profiles

app = FastAPI(
    title="DCA Priority & Allocation Engine",
    description="AI-powered dynamic case prioritization and DCA allocation system",
    version="1.0.0"
)

app.include_router(router)

@app.on_event("startup")
def startup_event():
    # Load DCA profiles into global memory on startup
    load_dca_profiles()

@app.get("/")
def health_check():
    return {"status": "OK", "message": "DCA Priority Engine is running"}