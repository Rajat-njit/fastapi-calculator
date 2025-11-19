# app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from app.database import Base, engine

# Routers
from app.api.routes.auth import router as auth_router
from app.api.routes.calculations import router as calc_router


# ------------------------------------------------------------------------------
# Lifespan → Create tables on startup
# ------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):

    # ⭐ IMPORTANT: import all models BEFORE create_all
    import app.models.user
    import app.models.calculation

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    yield



# ------------------------------------------------------------------------------
# FastAPI App Initialization
# ------------------------------------------------------------------------------

app = FastAPI(
    title="Calculations API",
    description="API for managing users and calculations",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}  # Keep token on reload
)


# ------------------------------------------------------------------------------
# Custom OpenAPI – Add JWT BearerAuth for Swagger UI
# ------------------------------------------------------------------------------
bearer_scheme = HTTPBearer()

def custom_openapi():
    """
    Add BearerAuth security scheme to Swagger UI so user can paste JWT token.
    This is needed because OAuth2PasswordBearer generates username/password UI,
    not a Bearer token entry field.
    """
    if app.openapi_schema:  # pragma: no cover
        return app.openapi_schema

    openapi_schema = get_openapi(       # pragma: no cover
        title="Calculations API",
        version="1.0.0",
        description="API for managing calculations and authentication.",
        routes=app.routes,
    )

    # Add BearerAuth scheme
    openapi_schema["components"]["securitySchemes"] = { # pragma: no cover
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Apply BearerAuth to protected endpoints
    protected_paths = [ # pragma: no cover
        "/calculations",
        "/calculations/{calc_id}"
    ]

    for path in openapi_schema["paths"]:    # pragma: no cover
        for method in openapi_schema["paths"][path]:
            if any(path.startswith(p) for p in protected_paths):
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ------------------------------------------------------------------------------
# Include Routers
# ------------------------------------------------------------------------------

app.include_router(auth_router, prefix="/auth", tags=["auth"])  # pragma: no cover
app.include_router(calc_router, prefix="/calculations", tags=["calculations"])


# ------------------------------------------------------------------------------
# Health Endpoint
# ------------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def read_health():
    return {"status": "ok"} # pragma: no cover


# ------------------------------------------------------------------------------
# Run the server directly (optional)
# ------------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)   # pragma: no cover
