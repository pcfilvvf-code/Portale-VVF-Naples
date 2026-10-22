import secrets
from pathlib import Path

from fastapi import Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates

from .database import get_db
from .models import User

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def verify_csrf(request: Request, csrf_token: str = Form("")):
    expected = request.session.get("csrf", "")
    if not expected or not secrets.compare_digest(csrf_token.encode(), expected.encode()):
        raise HTTPException(status_code=403, detail="Token CSRF non valido")


def get_current_user(request: Request, db=Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


def require_user(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


def require_role(*roles):
    def checker(user=Depends(require_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Permesso negato")
        return user

    return checker


def render(request: Request, name: str, user=None, status_code: int = 200, **ctx):
    ctx["user"] = user
    ctx["csrf_token"] = get_csrf_token(request)
    return templates.TemplateResponse(request, name, ctx, status_code=status_code)