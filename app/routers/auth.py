from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from pwdlib import PasswordHash
import secrets

from .. import config
from ..database import get_db
from ..deps import get_current_user, render, require_user, verify_csrf
from ..models import User

router = APIRouter()
password_hash = PasswordHash.recommended()

@router.get("/login")
def login_page(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse("/", status_code=303)
    return render(request, "login.html", user, error=None)

@router.post("/login", dependencies=[Depends(verify_csrf)])
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db)
):
    username = username.strip()
    user = db.scalar(select(User).where(User.username == username))
    
    if not user or not password_hash.verify(password, user.password_hash):
        return render(request, "login.html", None, status_code=401, error="Credenziali non valide.")
    
    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)

@router.get("/register")
def register_page(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse("/", status_code=303)
    return render(request, "register.html", user, error=None)

@router.post("/register", dependencies=[Depends(verify_csrf)])
def register_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    access_code: str = Form(...),
    db=Depends(get_db)
):
    username = username.strip()
    
    if not secrets.compare_digest(access_code.encode(), config.ACCESS_PASSWORD.encode()):
        return render(request, "register.html", None, status_code=401, error="Codice di accesso comune errato.")
    
    if db.scalar(select(User).where(User.username == username)):
        return render(request, "register.html", None, status_code=400, error="Questo username è già registrato.")
    
    if len(password) < 6:
        return render(request, "register.html", None, status_code=400, error="La password deve avere almeno 6 caratteri.")
    
    new_user = User(username=username, password_hash=password_hash.hash(password), role="user")
    if db.scalar(select(User).limit(1)) is None:
        new_user.role = "admin"
        
    db.add(new_user)
    db.commit()
    
    request.session.clear()
    request.session["user_id"] = new_user.id
    return RedirectResponse("/", status_code=303)

@router.get("/profilo")
def profilo(request: Request, user=Depends(require_user)):
    return render(request, "profilo.html", user)

@router.get("/impostazioni")
def impostazioni_page(request: Request, user=Depends(require_user)):
    return render(request, "impostazioni.html", user, error=None, success=None)

@router.post("/impostazioni", dependencies=[Depends(verify_csrf)])
def impostazioni_submit(
    request: Request,
    vecchia_password: str = Form(...),
    nuova_password: str = Form(...),
    conferma_password: str = Form(...),
    user=Depends(require_user),
    db=Depends(get_db)
):
    if not password_hash.verify(vecchia_password, user.password_hash):
        return render(request, "impostazioni.html", user, status_code=400, error="La vecchia password non è corretta.")
    
    if nuova_password != conferma_password:
        return render(request, "impostazioni.html", user, status_code=400, error="Le nuove password non coincidono.")
        
    if len(nuova_password) < 6:
        return render(request, "impostazioni.html", user, status_code=400, error="La nuova password deve avere almeno 6 caratteri.")

    user.password_hash = password_hash.hash(nuova_password)
    db.commit()
    
    return render(request, "impostazioni.html", user, success="Password aggiornata con successo!")

@router.post("/logout", dependencies=[Depends(verify_csrf)])
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)