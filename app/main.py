from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from . import config, models  # noqa: F401
from .database import Base, engine
from .routers import admin, auth, public, staff

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)

# Documentazione automatica disattivata: non serve esporla
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    SessionMiddleware,
    secret_key=config.SECRET_KEY,
    https_only=config.HTTPS_ONLY,
    same_site="lax",
    max_age=60 * 60 * 24 * 7,
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    
    # Regola aggiornata per permettere Tailwind, FontAwesome e Google Fonts
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
        "img-src 'self' https: data:; "
        "frame-ancestors 'none'; form-action 'self'"
    )
    return response

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(staff.router)
app.include_router(admin.router)