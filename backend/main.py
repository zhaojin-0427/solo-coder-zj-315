from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import engine, SessionLocal
from recommendation import recommend_utensils

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="新中式茶席主题策划与器物借用管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        crud.init_sample_data(db)
    finally:
        db.close()

@app.get("/api/themes", response_model=List[schemas.Theme], tags=["主题管理"])
def read_themes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_themes(db, skip=skip, limit=limit)

@app.get("/api/themes/{theme_id}", response_model=schemas.Theme, tags=["主题管理"])
def read_theme(theme_id: int, db: Session = Depends(get_db)):
    db_theme = crud.get_theme(db, theme_id=theme_id)
    if db_theme is None:
        raise HTTPException(status_code=404, detail="Theme not found")
    return db_theme

@app.post("/api/themes", response_model=schemas.Theme, tags=["主题管理"])
def create_theme(theme: schemas.ThemeCreate, db: Session = Depends(get_db)):
    return crud.create_theme(db=db, theme=theme)

@app.get("/api/utensils", response_model=List[schemas.Utensil], tags=["器物库"])
def read_utensils(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(get_db)):
    return crud.get_utensils(db, skip=skip, limit=limit, category=category)

@app.get("/api/utensils/{utensil_id}", response_model=schemas.Utensil, tags=["器物库"])
def read_utensil(utensil_id: int, db: Session = Depends(get_db)):
    db_utensil = crud.get_utensil(db, utensil_id=utensil_id)
    if db_utensil is None:
        raise HTTPException(status_code=404, detail="Utensil not found")
    return db_utensil

@app.post("/api/utensils", response_model=schemas.Utensil, tags=["器物库"])
def create_utensil(utensil: schemas.UtensilCreate, db: Session = Depends(get_db)):
    return crud.create_utensil(db=db, utensil=utensil)

@app.put("/api/utensils/{utensil_id}", response_model=schemas.Utensil, tags=["器物库"])
def update_utensil(utensil_id: int, utensil: schemas.UtensilUpdate, db: Session = Depends(get_db)):
    db_utensil = crud.update_utensil(db, utensil_id=utensil_id, utensil=utensil)
    if db_utensil is None:
        raise HTTPException(status_code=404, detail="Utensil not found")
    return db_utensil

@app.get("/api/tea-plans", response_model=List[schemas.TeaPlan], tags=["茶席方案"])
def read_tea_plans(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db)):
    return crud.get_tea_plans(db, skip=skip, limit=limit, status=status)

@app.get("/api/tea-plans/{plan_id}", response_model=schemas.TeaPlan, tags=["茶席方案"])
def read_tea_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = crud.get_tea_plan(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Tea plan not found")
    return db_plan

@app.post("/api/tea-plans", response_model=schemas.TeaPlan, tags=["茶席方案"])
def create_tea_plan(plan: schemas.TeaPlanCreate, db: Session = Depends(get_db)):
    return crud.create_tea_plan(db=db, plan=plan)

@app.put("/api/tea-plans/{plan_id}", response_model=schemas.TeaPlan, tags=["茶席方案"])
def update_tea_plan(plan_id: int, plan: schemas.TeaPlanUpdate, db: Session = Depends(get_db)):
    db_plan = crud.update_tea_plan(db, plan_id=plan_id, plan=plan)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Tea plan not found")
    return db_plan

@app.post("/api/tea-plans/{plan_id}/regenerate", response_model=schemas.TeaPlan, tags=["茶席方案"])
def regenerate_recommendations(plan_id: int, db: Session = Depends(get_db)):
    db_plan = crud.regenerate_recommendations(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Tea plan not found")
    return db_plan

@app.post("/api/recommend", tags=["智能推荐"])
def get_recommendation(request: schemas.RecommendationRequest, db: Session = Depends(get_db)):
    recommendations = recommend_utensils(
        db,
        theme_color=request.theme_color,
        tea_category=request.tea_category,
        people_count=request.people_count,
        budget=request.budget,
        photo_style=request.photo_style
    )
    return {
        "recommendations": [
            {
                "utensil": schemas.Utensil.model_validate(rec["utensil"]).model_dump(),
                "quantity": rec["quantity"],
                "score": rec["score"],
                "category": rec["category"]
            }
            for rec in recommendations
        ]
    }

@app.get("/api/borrow-lists", response_model=List[schemas.BorrowList], tags=["布席清单"])
def read_borrow_lists(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db)):
    return crud.get_borrow_lists(db, skip=skip, limit=limit, status=status)

@app.get("/api/borrow-lists/{borrow_id}", response_model=schemas.BorrowList, tags=["布席清单"])
def read_borrow_list(borrow_id: int, db: Session = Depends(get_db)):
    db_borrow = crud.get_borrow_list(db, borrow_id=borrow_id)
    if db_borrow is None:
        raise HTTPException(status_code=404, detail="Borrow list not found")
    return db_borrow

@app.post("/api/borrow-lists", response_model=schemas.BorrowList, tags=["布席清单"])
def create_borrow_list(borrow_list: schemas.BorrowListCreate, db: Session = Depends(get_db)):
    return crud.create_borrow_list(db=db, borrow_list=borrow_list)

@app.put("/api/borrow-lists/{borrow_id}", response_model=schemas.BorrowList, tags=["布席清单"])
def update_borrow_list(borrow_id: int, borrow_list: schemas.BorrowListUpdate, db: Session = Depends(get_db)):
    db_borrow = crud.update_borrow_list(db, borrow_id=borrow_id, borrow_list=borrow_list)
    if db_borrow is None:
        raise HTTPException(status_code=404, detail="Borrow list not found")
    return db_borrow

@app.put("/api/borrow-items/{item_id}", response_model=schemas.BorrowItem, tags=["布席清单"])
def update_borrow_item(item_id: int, item: schemas.BorrowItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_borrow_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Borrow item not found")
    return db_item

@app.get("/api/activity-reviews", response_model=List[schemas.ActivityReview], tags=["活动复盘"])
def read_activity_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_activity_reviews(db, skip=skip, limit=limit)

@app.get("/api/activity-reviews/{review_id}", response_model=schemas.ActivityReview, tags=["活动复盘"])
def read_activity_review(review_id: int, db: Session = Depends(get_db)):
    db_review = crud.get_activity_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Activity review not found")
    return db_review

@app.post("/api/activity-reviews", response_model=schemas.ActivityReview, tags=["活动复盘"])
def create_activity_review(review: schemas.ActivityReviewCreate, db: Session = Depends(get_db)):
    return crud.create_activity_review(db=db, review=review)

@app.put("/api/activity-reviews/{review_id}", response_model=schemas.ActivityReview, tags=["活动复盘"])
def update_activity_review(review_id: int, review: schemas.ActivityReviewUpdate, db: Session = Depends(get_db)):
    db_review = crud.update_activity_review(db, review_id=review_id, review=review)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Activity review not found")
    return db_review

@app.put("/api/review-items/{item_id}", response_model=schemas.ReviewItem, tags=["活动复盘"])
def update_review_item(item_id: int, item: schemas.ReviewItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_review_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Review item not found")
    return db_item

@app.get("/api/reservations", response_model=List[schemas.Reservation], tags=["预约管理"])
def read_reservations(
    skip: int = 0, 
    limit: int = 100, 
    status: str = None,
    start_date: str = None,
    end_date: str = None,
    tea_category: str = None,
    theme_color: str = None,
    db: Session = Depends(get_db)
):
    parsed_start = parse_date(start_date) if start_date else None
    parsed_end = parse_date(end_date) if end_date else None
    return crud.get_reservations(
        db, skip=skip, limit=limit, status=status,
        start_date=parsed_start, end_date=parsed_end,
        tea_category=tea_category, theme_color=theme_color
    )

@app.get("/api/reservations/{reservation_id}", response_model=schemas.Reservation, tags=["预约管理"])
def read_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return db_reservation

@app.get("/api/reservations/check-conflict", response_model=schemas.ConflictCheckResponse, tags=["预约管理"])
def check_reservation_conflict(
    check_date: str,
    time_slot: str,
    exclude_reservation_id: int = None,
    exclude_plan_id: int = None,
    db: Session = Depends(get_db)
):
    parsed_date = parse_date(check_date)
    conflicts = crud.check_conflict(
        db, check_date=parsed_date, time_slot=time_slot,
        exclude_reservation_id=exclude_reservation_id, exclude_plan_id=exclude_plan_id
    )
    serializable_conflicts = []
    for c in conflicts:
        c_dict = dict(c)
        c_dict['date'] = str(c_dict['date'])
        serializable_conflicts.append(c_dict)
    return {
        "has_conflict": len(conflicts) > 0,
        "conflicts": serializable_conflicts
    }

@app.post("/api/reservations", response_model=schemas.Reservation, tags=["预约管理"])
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    conflicts = crud.check_conflict(
        db, check_date=reservation.expected_date, time_slot=reservation.time_slot
    )
    if len(conflicts) > 0:
        serializable_conflicts = []
        for c in conflicts:
            c_dict = dict(c)
            c_dict['date'] = str(c_dict['date'])
            serializable_conflicts.append(c_dict)
        raise HTTPException(
            status_code=409,
            detail={
                "message": "该日期时段已有活动安排，请选择其他时段",
                "conflicts": serializable_conflicts
            }
        )
    return crud.create_reservation(db=db, reservation=reservation)

@app.put("/api/reservations/{reservation_id}", response_model=schemas.Reservation, tags=["预约管理"])
def update_reservation(reservation_id: int, reservation: schemas.ReservationUpdate, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    check_date = reservation.expected_date or db_reservation.expected_date
    check_time_slot = reservation.time_slot or db_reservation.time_slot
    
    if reservation.expected_date is not None or reservation.time_slot is not None:
        conflicts = crud.check_conflict(
            db, check_date=check_date, time_slot=check_time_slot,
            exclude_reservation_id=reservation_id
        )
        if len(conflicts) > 0:
            serializable_conflicts = []
            for c in conflicts:
                c_dict = dict(c)
                c_dict['date'] = str(c_dict['date'])
                serializable_conflicts.append(c_dict)
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "该日期时段已有活动安排，请选择其他时段",
                    "conflicts": serializable_conflicts
                }
            )
    
    return crud.update_reservation(db, reservation_id=reservation_id, reservation=reservation)

@app.post("/api/reservations/{reservation_id}/confirm", response_model=schemas.Reservation, tags=["预约管理"])
def confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    conflicts = crud.check_conflict(
        db, check_date=db_reservation.expected_date, time_slot=db_reservation.time_slot,
        exclude_reservation_id=reservation_id
    )
    if len(conflicts) > 0:
        serializable_conflicts = []
        for c in conflicts:
            c_dict = dict(c)
            c_dict['date'] = str(c_dict['date'])
            serializable_conflicts.append(c_dict)
        raise HTTPException(
            status_code=409,
            detail={
                "message": "该日期时段已有活动安排，无法确认预约",
                "conflicts": serializable_conflicts
            }
        )
    
    return crud.update_reservation(
        db, reservation_id=reservation_id,
        reservation=schemas.ReservationUpdate(status="confirmed")
    )

@app.post("/api/reservations/{reservation_id}/cancel", response_model=schemas.Reservation, tags=["预约管理"])
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.update_reservation(
        db, reservation_id=reservation_id,
        reservation=schemas.ReservationUpdate(status="cancelled")
    )

@app.post("/api/reservations/{reservation_id}/convert", response_model=schemas.TeaPlan, tags=["预约管理"])
def convert_reservation_to_plan(
    reservation_id: int,
    convert_request: schemas.ConvertToPlanRequest,
    db: Session = Depends(get_db)
):
    db_reservation = crud.get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if db_reservation.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="只有已确认的预约才能转化为茶席方案"
        )
    
    db_plan = crud.convert_reservation_to_plan(
        db, reservation_id=reservation_id, convert_request=convert_request
    )
    if db_plan is None:
        raise HTTPException(status_code=500, detail="转化失败")
    return db_plan

@app.get("/api/statistics", response_model=schemas.StatisticsResponse, tags=["数据统计"])
def get_statistics(db: Session = Depends(get_db)):
    return crud.get_statistics(db)

def parse_date(v):
    if v is None:
        return None
    from datetime import date, datetime
    import re
    if isinstance(v, date):
        return v
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, str):
        if re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            return date.fromisoformat(v)
        try:
            return datetime.fromisoformat(v.replace('Z', '+00:00')).date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无法解析日期: {v}")
    raise HTTPException(status_code=400, detail=f"无法解析日期: {v}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9702)
