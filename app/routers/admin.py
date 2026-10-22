from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from ..database import get_db
from ..deps import render, require_role, verify_csrf
from ..models import Force

router = APIRouter()

admin_only = require_role("admin")

@router.get("/admin/forze")
def forces_admin(request: Request, user=Depends(admin_only), db=Depends(get_db)):
    items = db.scalars(select(Force).order_by(Force.name)).all()
    return render(request, "admin_forces.html", user, forces=items, error=None)

@router.post("/admin/forze", dependencies=[Depends(verify_csrf)])
def create_force(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    user=Depends(admin_only),
    db=Depends(get_db),
):
    name = name.strip()
    description = description.strip()
    items = db.scalars(select(Force).order_by(Force.name)).all()

    error = None
    if not (2 <= len(name) <= 80):
        error = "Il nome del reparto deve avere tra 2 e 80 caratteri."
    elif len(description) > 1000:
        error = "Descrizione troppo lunga (max 1000 caratteri)."
    elif db.scalar(select(Force).where(Force.name == name)):
        error = "Esiste già un reparto con questo nome."

    if error:
        return render(request, "admin_forces.html", user, status_code=400, forces=items, error=error)

    db.add(Force(name=name, description=description))
    db.commit()
    return RedirectResponse("/admin/forze", status_code=303)