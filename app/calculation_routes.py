from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Calculation
from app.schemas import CalculationCreate, CalculationRead
from app.calculation_factory import CalculationFactory

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.get("", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).order_by(Calculation.id).all()


@router.get("/{calc_id}", response_model=CalculationRead)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.get(Calculation, calc_id)
    if calc is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc


@router.post("", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(payload: CalculationCreate, db: Session = Depends(get_db)):
    result = CalculationFactory.compute(payload.type, payload.a, payload.b)
    calc = Calculation(a=payload.a, b=payload.b, type=payload.type, result=result, user_id=payload.user_id)
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@router.put("/{calc_id}", response_model=CalculationRead)
def edit_calculation(calc_id: int, payload: CalculationCreate, db: Session = Depends(get_db)):
    calc = db.get(Calculation, calc_id)
    if calc is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    calc.a = payload.a
    calc.b = payload.b
    calc.type = payload.type
    calc.result = CalculationFactory.compute(payload.type, payload.a, payload.b)
    db.commit()
    db.refresh(calc)
    return calc


@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.get(Calculation, calc_id)
    if calc is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(calc)
    db.commit()
    return None