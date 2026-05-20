"""
Cuber Progress — FastAPI Backend
Rubik's Algorithm Memorization Tracker
"""
import os
import sys
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, Integer

# Add current directory to path for serverless environment imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, init_db, seed_db, Case, Algorithm


# ── App Setup ──────────────────────────────────────────
app = FastAPI(title="Cuber Progress", version="1.0.0")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return PlainTextResponse(
        f"Error: {exc.__class__.__name__}: {str(exc)}\n{traceback.format_exc()}",
        status_code=500
    )


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# ── Dependency ─────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Startup ────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    try:
        init_db()
        seed_db()
        print("Database initialized and seeded successfully.")
    except Exception as e:
        import traceback
        print("CRITICAL: Database initialization failed!")
        print(traceback.format_exc())



# ── Pages ──────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


# ── API: Cases ─────────────────────────────────────────
@app.get("/api/cases")
def get_cases(
    category: Optional[str] = Query(None, description="Filter by category: F2L, ZBLS, ZBLL"),
    status: Optional[str] = Query(None, description="Filter by status: memorized, not_memorized"),
    sub_group: Optional[str] = Query(None, description="Filter by sub-group"),
    search: Optional[str] = Query(None, description="Search by case name or algorithm"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Case)

    if category:
        query = query.filter(Case.category == category.upper())
    if status == "memorized":
        query = query.filter(Case.status == True)
    elif status == "not_memorized":
        query = query.filter(Case.status == False)
    if sub_group:
        query = query.filter(Case.sub_group == sub_group)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Case.case_name.ilike(search_term)) |
            (Case.sub_group.ilike(search_term)) |
            (Case.algorithms.any(Algorithm.notation.ilike(search_term)))
        )

    total = query.count()
    cases = query.order_by(Case.id).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "cases": [c.to_dict() for c in cases],
    }


@app.get("/api/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.to_dict()


@app.put("/api/cases/{case_id}/toggle")
def toggle_case_status(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = not case.status
    if case.status:
        case.date_learned = datetime.now(timezone.utc)
    else:
        case.date_learned = None

    db.commit()
    db.refresh(case)
    return case.to_dict()


@app.put("/api/cases/{case_id}/select-algorithm/{algorithm_id}")
def select_algorithm(case_id: int, algorithm_id: int, db: Session = Depends(get_db)):
    """Select which algorithm variation to use for memorization."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Deselect all algorithms for this case
    for alg in case.algorithms:
        alg.is_selected = (alg.id == algorithm_id)

    db.commit()
    db.refresh(case)
    return case.to_dict()


# ── API: Statistics ────────────────────────────────────
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Case).count()
    memorized = db.query(Case).filter(Case.status == True).count()

    # Per-category stats
    categories = {}
    for cat in ["F2L", "ZBLS", "ZBLL"]:
        cat_total = db.query(Case).filter(Case.category == cat).count()
        cat_memorized = db.query(Case).filter(
            Case.category == cat, Case.status == True
        ).count()
        categories[cat] = {
            "total": cat_total,
            "memorized": cat_memorized,
            "percentage": round((cat_memorized / cat_total * 100) if cat_total > 0 else 0, 1),
        }

    # Sub-group stats
    sub_groups = {}
    results = db.query(
        Case.category, Case.sub_group,
        func.count(Case.id).label("total"),
        func.sum(case((Case.status == True, 1), else_=0)).label("memorized"),
    ).group_by(Case.category, Case.sub_group).all()

    for row in results:
        cat = row[0]
        sg = row[1] or "Uncategorized"
        t = row[2]
        m = int(row[3] or 0)
        if cat not in sub_groups:
            sub_groups[cat] = []
        sub_groups[cat].append({
            "name": sg,
            "total": t,
            "memorized": m,
            "percentage": round((m / t * 100) if t > 0 else 0, 1),
        })

    return {
        "total": total,
        "memorized": memorized,
        "percentage": round((memorized / total * 100) if total > 0 else 0, 1),
        "categories": categories,
        "sub_groups": sub_groups,
    }


@app.get("/api/stats/monthly")
def get_monthly_stats(db: Session = Depends(get_db)):
    """Get monthly memorization data for the chart."""
    results = db.query(
        func.strftime('%Y-%m', Case.date_learned).label("month"),
        func.count(Case.id).label("count"),
    ).filter(
        Case.status == True,
        Case.date_learned.isnot(None),
    ).group_by(
        func.strftime('%Y-%m', Case.date_learned)
    ).order_by("month").all()

    # Also get cumulative per category
    cat_results = {}
    for cat in ["F2L", "ZBLS", "ZBLL"]:
        rows = db.query(
            func.strftime('%Y-%m', Case.date_learned).label("month"),
            func.count(Case.id).label("count"),
        ).filter(
            Case.category == cat,
            Case.status == True,
            Case.date_learned.isnot(None),
        ).group_by(
            func.strftime('%Y-%m', Case.date_learned)
        ).order_by("month").all()
        cat_results[cat] = [{"month": r[0], "count": r[1]} for r in rows]

    return {
        "total": [{"month": r[0], "count": r[1]} for r in results],
        "by_category": cat_results,
    }


@app.get("/api/sub-groups")
def get_sub_groups(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get list of sub-groups for filtering."""
    query = db.query(Case.category, Case.sub_group).distinct()
    if category:
        query = query.filter(Case.category == category.upper())
    results = query.order_by(Case.category, Case.sub_group).all()

    grouped = {}
    for cat, sg in results:
        if cat not in grouped:
            grouped[cat] = []
        if sg:
            grouped[cat].append(sg)
    return grouped


# ── Run ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
