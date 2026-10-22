from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..deps import get_current_user, render, require_user
from ..models import Force, User, Turno

router = APIRouter()

GRADI_VVF = {
    "Dirigente": 10, "Ispettore": 9, "Capo Reparto": 8,
    "Capo Squadra": 7, "Vigile del Fuoco": 6, "Recluta": 5, "": 0
}

@router.get("/")
def home(request: Request, user=Depends(get_current_user), db=Depends(get_db)):
    if not user:
        return RedirectResponse("/login", status_code=303)
        
    n_members = db.scalar(select(func.count(User.id)).where(User.force_id.is_not(None)))
    n_forces = db.scalar(select(func.count(Force.id)))
    reparti = db.scalars(select(Force).order_by(Force.name)).all()
    
    # 1. Prende TUTTI i turni attivi (senza filtri su grado o forza)
    turni_attivi = db.scalars(
        select(Turno).where(Turno.fine == None).options(selectinload(Turno.user), selectinload(Turno.force))
    ).all()
    
    personale = []
    for t in turni_attivi:
        p = t.user
        # Se il turno ha un reparto assegnato lo usa, altrimenti "Non assegnato"
        p.reparto_servizio = t.force.name if t.force else "Non assegnato"
        p.mezzo = "APS 1A" # Mezzo fittizio
        personale.append(p)
    
    # Trova Capo Partenza (grado più alto tra chi è in servizio)
    capo_partenza = None
    max_grado = -1
    for p in personale:
        livello = GRADI_VVF.get(p.rank, 0)
        if livello > max_grado:
            max_grado = livello
            capo_partenza = p
            
    n_capi = len([p for p in personale if GRADI_VVF.get(p.rank, 0) >= 7])
    n_vigili = len([p for p in personale if GRADI_VVF.get(p.rank, 0) < 7])
    
    # 2. Prende gli ultimi 5 turni CONCLUSI dell'utente loggato
    turni_precedenti = db.scalars(
        select(Turno).where(Turno.user_id == user.id, Turno.fine != None)
        .order_by(Turno.fine.desc()).limit(5)
    ).all()
    
    return render(
        request, "home.html", user, 
        n_members=n_members, 
        n_forces=n_forces,
        personale=personale,
        capo_partenza=capo_partenza,
        n_capi=n_capi,
        n_vigili=n_vigili,
        reparti=reparti,
        turni_precedenti=turni_precedenti
    )

@router.get("/forze")
def forces(request: Request, user=Depends(get_current_user), db=Depends(get_db)):
    items = db.scalars(select(Force).order_by(Force.name)).all()
    return render(request, "forces.html", user, forces=items)

@router.get("/membri")
def members(request: Request, user=Depends(get_current_user), db=Depends(get_db)):
    items = db.scalars(select(User).where(User.force_id.is_not(None)).order_by(User.force_id, User.username)).all()
    return render(request, "members.html", user, members=items)

@router.post("/api/turno/start")
def start_shift(force_id: int = Form(None), user=Depends(require_user), db=Depends(get_db)):
    turno_aperto = db.scalar(select(Turno).where(Turno.user_id == user.id, Turno.fine == None))
    if turno_aperto:
        inizio_str = turno_aperto.inizio.isoformat() + "Z" if not turno_aperto.inizio.tzinfo else turno_aperto.inizio.isoformat()
        return JSONResponse({"status": "already_active", "inizio": inizio_str})
    
    nuovo_turno = Turno(user_id=user.id, inizio=datetime.now(timezone.utc), force_id=force_id)
    db.add(nuovo_turno)
    db.commit()
    inizio_str = nuovo_turno.inizio.isoformat() + "Z" if not nuovo_turno.inizio.tzinfo else nuovo_turno.inizio.isoformat()
    return JSONResponse({"status": "started", "inizio": inizio_str})

@router.post("/api/turno/stop")
def stop_shift(user=Depends(require_user), db=Depends(get_db)):
    turno_aperto = db.scalar(select(Turno).where(Turno.user_id == user.id, Turno.fine == None))
    if not turno_aperto:
        return JSONResponse({"status": "not_active"})
    turno_aperto.fine = datetime.now(timezone.utc)
    db.commit()
    return JSONResponse({"status": "stopped"})

@router.get("/api/turno/status")
def shift_status(user=Depends(require_user), db=Depends(get_db)):
    turno_aperto = db.scalar(select(Turno).where(Turno.user_id == user.id, Turno.fine == None))
    if turno_aperto:
        inizio_str = turno_aperto.inizio.isoformat() + "Z" if not turno_aperto.inizio.tzinfo else turno_aperto.inizio.isoformat()
        return JSONResponse({"active": True, "inizio": inizio_str})
    return JSONResponse({"active": False})