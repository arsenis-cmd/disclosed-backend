from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import db
from middleware.rate_limit import rate_limit_middleware

from routers import users, campaigns, tasks, proofs, verification, payments, detection

settings = get_settings()

app = FastAPI(
    title="Proof of Consideration API",
    version="1.0.0",
    description="API for the Proof of Consideration marketplace"
)

# Rate Limiting (must be first to protect all endpoints)
app.middleware("http")(rate_limit_middleware)

# CORS - Allow specific origins
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://proof-of-consideration.vercel.app",
    "https://disclosed.vercel.app",
    settings.frontend_url
]
# Remove duplicates
cors_origins = list(set(cors_origins))
print(f"CORS Origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(detection.router, prefix=f"/api/{settings.api_version}", tags=["detection"])  # AI Detection - new core feature
app.include_router(users.router, prefix=f"/api/{settings.api_version}/users", tags=["users"])
app.include_router(campaigns.router, prefix=f"/api/{settings.api_version}/campaigns", tags=["campaigns"])
app.include_router(tasks.router, prefix=f"/api/{settings.api_version}/tasks", tags=["tasks"])
app.include_router(proofs.router, prefix=f"/api/{settings.api_version}/proofs", tags=["proofs"])
app.include_router(verification.router, prefix=f"/api/{settings.api_version}/verify", tags=["verification"])
app.include_router(payments.router, prefix=f"/api/{settings.api_version}/payments", tags=["payments"])


@app.on_event("startup")
async def startup():
    await db.connect()
    print("Database connected")


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    print("Database disconnected")


@app.get("/")
async def root():
    return {"message": "Proof of Consideration API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
