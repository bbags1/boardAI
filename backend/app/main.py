from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routes import auth, advisors, documents # Add advisors import

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "http://localhost:8501",  # Streamlit default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
app.include_router(advisors.router, prefix=settings.API_V1_STR + "/advisors", tags=["advisors"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

@app.get("/")
def root():
    return {"message": "Welcome to AI Advisory Board API"}