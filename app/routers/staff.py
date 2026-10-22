from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from ..database import get_db
from ..deps import render, require_role, verify_csrf
from ..models import Force, User

router = APIRouter()

staff_only = require_role("ufficiale", "admin")


@router.get("/staff/membri")
def manage_members(request: Request, user=Depends(staff_only), db=Depends(get_db)):
    users = db.scalars(select(User).order_by(User.username)).all()
    forces = db.scalars(select(Force).order_by(Force.name)).all()
    return render(request, "staff_members.html", user, users=users, forces=forces)


@router.post("/staff/membri/{user_id}", dependencies=[Depends(verify_csrf)])
def update_member(
    user_id: int,
    force_id: str = Form(""),
    rank: str = Form(""),
    user=Depends(staff_only),
    db=Depends(get_db),
):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    rank = rank.strip()
    if len(rank) > 50:
        raise HTTPException(status_code=400, detail="Grado troppo lungo")

    if force_id == "":
        target.force_id = None
        target.rank = ""
    else:
        force = db.get(Force, int(force_id)) if force_id.isdigit() else None
        if not force:
            raise HTTPException(status_code=400, detail="Forza non valida")
        target.force_id = force.id
        target.rank = rank

    db.commit()
    return RedirectResponse("/staff/membri", status_code=303)