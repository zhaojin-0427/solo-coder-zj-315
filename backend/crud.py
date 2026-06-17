from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from recommendation import recommend_utensils
from typing import List, Dict
from datetime import date

def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_themes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Theme).offset(skip).limit(limit).all()

def get_theme(db: Session, theme_id: int):
    return db.query(models.Theme).filter(models.Theme.id == theme_id).first()

def create_theme(db: Session, theme: schemas.ThemeCreate):
    db_theme = models.Theme(**theme.model_dump())
    db.add(db_theme)
    db.commit()
    db.refresh(db_theme)
    return db_theme

def get_utensils(db: Session, skip: int = 0, limit: int = 100, category: str = None):
    query = db.query(models.Utensil)
    if category:
        query = query.filter(models.Utensil.category == category)
    return query.offset(skip).limit(limit).all()

def get_utensil(db: Session, utensil_id: int):
    return db.query(models.Utensil).filter(models.Utensil.id == utensil_id).first()

def create_utensil(db: Session, utensil: schemas.UtensilCreate):
    db_utensil = models.Utensil(**utensil.model_dump())
    db.add(db_utensil)
    db.commit()
    db.refresh(db_utensil)
    return db_utensil

def update_utensil(db: Session, utensil_id: int, utensil: schemas.UtensilUpdate):
    db_utensil = get_utensil(db, utensil_id)
    if not db_utensil:
        return None
    update_data = utensil.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_utensil, key, value)
    db.commit()
    db.refresh(db_utensil)
    return db_utensil

def get_tea_plans(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.TeaPlan)
    if status:
        query = query.filter(models.TeaPlan.status == status)
    return query.order_by(models.TeaPlan.date.desc()).offset(skip).limit(limit).all()

def get_tea_plan(db: Session, plan_id: int):
    return db.query(models.TeaPlan).filter(models.TeaPlan.id == plan_id).first()

def create_tea_plan(db: Session, plan: schemas.TeaPlanCreate):
    plan_data = plan.model_dump(exclude={'selected_items'})
    db_plan = models.TeaPlan(**plan_data)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    total_price = 0
    for item in plan.selected_items:
        utensil = get_utensil(db, item.utensil_id)
        if utensil:
            db_rec_item = models.RecommendedItem(
                plan_id=db_plan.id,
                utensil_id=item.utensil_id,
                quantity=item.quantity,
                selected=item.selected
            )
            db.add(db_rec_item)
            if item.selected:
                total_price += utensil.price * item.quantity
    
    db_plan.total_price = total_price
    db.commit()
    db.refresh(db_plan)
    
    return db_plan

def update_tea_plan(db: Session, plan_id: int, plan: schemas.TeaPlanUpdate):
    db_plan = get_tea_plan(db, plan_id)
    if not db_plan:
        return None
    
    update_data = plan.model_dump(exclude_unset=True)
    
    if 'selected_items' in update_data and update_data['selected_items'] is not None:
        db.query(models.RecommendedItem).filter(models.RecommendedItem.plan_id == plan_id).delete()
        total_price = 0
        for item in update_data['selected_items']:
            utensil = get_utensil(db, item['utensil_id'])
            if utensil:
                db_rec_item = models.RecommendedItem(
                    plan_id=plan_id,
                    utensil_id=item['utensil_id'],
                    quantity=item['quantity'],
                    selected=item['selected']
                )
                db.add(db_rec_item)
                if item['selected']:
                    total_price += utensil.price * item['quantity']
        
        if 'total_price' not in update_data:
            db_plan.total_price = total_price
        else:
            db_plan.total_price = update_data['total_price']
        
        del update_data['selected_items']
    
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

def regenerate_recommendations(db: Session, plan_id: int):
    db_plan = get_tea_plan(db, plan_id)
    if not db_plan:
        return None
    
    prev_selections = {}
    for item in db_plan.recommended_items:
        prev_selections[item.utensil_id] = item.selected
    
    db.query(models.RecommendedItem).filter(models.RecommendedItem.plan_id == plan_id).delete()
    
    theme_color = db_plan.theme_color
    tea_category = db_plan.tea_category
    if not theme_color or not tea_category:
        theme = get_theme(db, db_plan.theme_id)
        if theme:
            theme_color = theme_color or theme.color
            tea_category = tea_category or theme.tea_category
    
    if theme_color and tea_category:
        recommendations = recommend_utensils(
            db, theme_color, tea_category,
            db_plan.people_count, db_plan.budget, db_plan.photo_style
        )
        
        total_price = 0
        for rec in recommendations:
            utensil = rec["utensil"]
            quantity = rec["quantity"]
            was_selected = prev_selections.get(utensil.id, False)
            db_rec_item = models.RecommendedItem(
                plan_id=db_plan.id,
                utensil_id=utensil.id,
                quantity=quantity,
                selected=was_selected
            )
            db.add(db_rec_item)
            if was_selected:
                total_price += utensil.price * quantity
        
        db_plan.total_price = total_price
        db.commit()
        db.refresh(db_plan)
    
    return db_plan

def create_borrow_list(db: Session, borrow_list: schemas.BorrowListCreate):
    db_borrow = models.BorrowList(
        plan_id=borrow_list.plan_id,
        borrow_date=borrow_list.borrow_date,
        return_date=borrow_list.return_date,
        status=borrow_list.status
    )
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    
    for item in borrow_list.items:
        db_item = models.BorrowItem(
            borrow_list_id=db_borrow.id,
            utensil_id=item.utensil_id,
            quantity=item.quantity,
            borrowed=item.borrowed,
            returned=item.returned
        )
        db.add(db_item)
    
    db_plan = get_tea_plan(db, borrow_list.plan_id)
    if db_plan:
        db_plan.status = "borrowing"
        db.commit()
    
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def get_borrow_lists(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.BorrowList)
    if status:
        query = query.filter(models.BorrowList.status == status)
    return query.order_by(models.BorrowList.borrow_date.desc()).offset(skip).limit(limit).all()

def get_borrow_list(db: Session, borrow_id: int):
    return db.query(models.BorrowList).filter(models.BorrowList.id == borrow_id).first()

def update_borrow_list(db: Session, borrow_id: int, borrow_list: schemas.BorrowListUpdate):
    db_borrow = get_borrow_list(db, borrow_id)
    if not db_borrow:
        return None
    update_data = borrow_list.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_borrow, key, value)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def update_borrow_item(db: Session, item_id: int, item: schemas.BorrowItemUpdate):
    db_item = db.query(models.BorrowItem).filter(models.BorrowItem.id == item_id).first()
    if not db_item:
        return None
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    
    if db_item.returned:
        utensil = db.query(models.Utensil).filter(models.Utensil.id == db_item.utensil_id).first()
        if utensil:
            utensil.available += db_item.quantity
            db.commit()
    
    return db_item

def create_activity_review(db: Session, review: schemas.ActivityReviewCreate):
    db_review = models.ActivityReview(
        plan_id=review.plan_id,
        review_date=review.review_date,
        customer_feedback=review.customer_feedback,
        rating=review.rating,
        is_repeat_customer=review.is_repeat_customer
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    for item in review.items:
        db_item = models.ReviewItem(
            review_id=db_review.id,
            utensil_id=item.utensil_id,
            damaged=item.damaged,
            damage_description=item.damage_description,
            cleaned=item.cleaned
        )
        db.add(db_item)
    
    db_plan = get_tea_plan(db, review.plan_id)
    if db_plan:
        db_plan.status = "completed"
        db.commit()
    
    db.commit()
    db.refresh(db_review)
    return db_review

def get_activity_reviews(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ActivityReview).order_by(models.ActivityReview.review_date.desc()).offset(skip).limit(limit).all()

def get_activity_review(db: Session, review_id: int):
    return db.query(models.ActivityReview).filter(models.ActivityReview.id == review_id).first()

def update_activity_review(db: Session, review_id: int, review: schemas.ActivityReviewUpdate):
    db_review = get_activity_review(db, review_id)
    if not db_review:
        return None
    update_data = review.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return db_review

def update_review_item(db: Session, item_id: int, item: schemas.ReviewItemUpdate):
    db_item = db.query(models.ReviewItem).filter(models.ReviewItem.id == item_id).first()
    if not db_item:
        return None
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_statistics(db: Session):
    theme_stats = db.query(
        models.Theme.name.label("theme_name"),
        func.count(models.TeaPlan.id).label("count")
    ).join(models.TeaPlan, models.Theme.id == models.TeaPlan.theme_id, isouter=True) \
     .group_by(models.Theme.id).all()
    
    utensil_usage = db.query(
        models.Utensil.name.label("utensil_name"),
        models.Utensil.category.label("category"),
        func.count(models.BorrowItem.id).label("usage_count")
    ).join(models.BorrowItem, models.Utensil.id == models.BorrowItem.utensil_id, isouter=True) \
     .group_by(models.Utensil.id).order_by(func.count(models.BorrowItem.id).desc()).limit(10).all()
    
    damage_stats = db.query(
        models.Utensil.name.label("utensil_name"),
        models.Utensil.category.label("category"),
        func.count(models.ReviewItem.id).filter(models.ReviewItem.damaged == True).label("damage_count"),
        (func.count(models.ReviewItem.id).filter(models.ReviewItem.damaged == True) * 100.0 / 
         func.nullif(func.count(models.BorrowItem.id), 0)).label("damage_rate")
    ).join(models.ReviewItem, models.Utensil.id == models.ReviewItem.utensil_id, isouter=True) \
     .join(models.BorrowItem, models.Utensil.id == models.BorrowItem.utensil_id, isouter=True) \
     .group_by(models.Utensil.id).all()
    
    price_ranges = [
        ("0-500", 0, 500),
        ("500-1000", 500, 1000),
        ("1000-2000", 1000, 2000),
        ("2000-5000", 2000, 5000),
        ("5000+", 5000, float('inf'))
    ]
    
    price_range_stats = []
    for range_name, min_p, max_p in price_ranges:
        count = db.query(models.TeaPlan).filter(
            models.TeaPlan.total_price >= min_p,
            models.TeaPlan.total_price < max_p
        ).count()
        price_range_stats.append({"range": range_name, "count": count})
    
    repeat_type_stats = db.query(
        models.Theme.tea_category.label("tea_type"),
        func.count(models.ActivityReview.id).filter(models.ActivityReview.is_repeat_customer == True).label("count")
    ).join(models.TeaPlan, models.Theme.id == models.TeaPlan.theme_id) \
     .join(models.ActivityReview, models.TeaPlan.id == models.ActivityReview.plan_id, isouter=True) \
     .group_by(models.Theme.tea_category).all()
    
    color_reservation_stats = db.query(
        models.TeaPlan.theme_color,
        func.count(models.TeaPlan.id).label("count")
    ).filter(models.TeaPlan.theme_color.isnot(None), models.TeaPlan.theme_color != '') \
     .group_by(models.TeaPlan.theme_color).all()
    
    tea_category_reservation_stats = db.query(
        models.TeaPlan.tea_category,
        func.count(models.TeaPlan.id).label("count")
    ).filter(models.TeaPlan.tea_category.isnot(None), models.TeaPlan.tea_category != '') \
     .group_by(models.TeaPlan.tea_category).all()
    
    total_orders = db.query(models.TeaPlan).count()
    total_revenue = db.query(func.sum(models.TeaPlan.total_price)).scalar() or 0
    avg_rating = db.query(func.avg(models.ActivityReview.rating)).scalar() or 0
    
    reservation_stats = get_reservation_statistics(db)
    
    return {
        "theme_stats": [{"theme_name": t, "count": c} for t, c in theme_stats],
        "utensil_usage_stats": [{"utensil_name": n, "category": c, "usage_count": u} for n, c, u in utensil_usage],
        "damage_stats": [{"utensil_name": n, "category": c, "damage_count": d, "damage_rate": float(r or 0)} for n, c, d, r in damage_stats],
        "price_range_stats": price_range_stats,
        "repeat_type_stats": [{"tea_type": t, "count": c} for t, c in repeat_type_stats],
        "color_reservation_stats": [{"theme_color": c, "count": n} for c, n in color_reservation_stats],
        "tea_category_reservation_stats": [{"tea_category": t, "count": n} for t, n in tea_category_reservation_stats],
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "avg_rating": float(avg_rating),
        "reservation_stats": reservation_stats
    }

def init_sample_data(db: Session):
    if db.query(models.Theme).count() == 0:
        themes = [
            models.Theme(name="宋韵雅集", description="还原宋代文人品茗雅致", color="青色", tea_category="绿茶", style="宋韵古风", min_people=2, max_people=8, min_budget=500, max_budget=3000),
            models.Theme(name="禅茶一味", description="禅意极简，静谧品茗", color="米白", tea_category="乌龙茶", style="禅意极简", min_people=1, max_people=4, min_budget=300, max_budget=2000),
            models.Theme(name="朱门雅宴", description="朱红喜庆，高端茶席", color="朱红", tea_category="红茶", style="文人雅集", min_people=4, max_people=12, min_budget=1000, max_budget=5000),
            models.Theme(name="山水之间", description="自然山野气息", color="黛绿", tea_category="普洱茶", style="自然山野", min_people=3, max_people=10, min_budget=600, max_budget=3500),
            models.Theme(name="月色荷塘", description="清雅月色，荷塘意境", color="月白", tea_category="白茶", style="现代新中式", min_people=2, max_people=6, min_budget=400, max_budget=2500)
        ]
        db.add_all(themes)
    
    if db.query(models.Utensil).count() == 0:
        utensils = [
            models.Utensil(name="汝窑天青盖碗", category="盖碗", material="青瓷", color="青色", style="宋代", price=280, quantity=5, available=5, description="汝窑天青色，开片细腻"),
            models.Utensil(name="紫砂仿古盖碗", category="盖碗", material="紫砂", color="紫砂", style="仿古", price=320, quantity=4, available=4, description="宜兴紫砂，泥料上乘"),
            models.Utensil(name="朱泥小品盖碗", category="盖碗", material="朱泥", color="朱红", style="仿古", price=260, quantity=6, available=6, description="朱泥烧制，色泽温润"),
            models.Utensil(name="白瓷薄胎盖碗", category="盖碗", material="白瓷", color="象牙", style="极简", price=180, quantity=8, available=8, description="德化白瓷，薄如蝉翼"),
            models.Utensil(name="粗陶手作盖碗", category="盖碗", material="粗陶", color="灰墨", style="粗陶", price=190, quantity=3, available=3, description="手工拉坯，朴拙自然"),
            
            models.Utensil(name="青瓷公道杯", category="茶海", material="青瓷", color="青色", style="宋代", price=160, quantity=5, available=5, description="龙泉青瓷，釉色温润"),
            models.Utensil(name="玻璃公道杯", category="茶海", material="玻璃", color="素白", style="现代", price=80, quantity=10, available=10, description="高硼硅玻璃，观茶汤"),
            models.Utensil(name="紫砂茶海", category="茶海", material="紫砂", color="紫砂", style="禅意", price=220, quantity=4, available=4, description="紫砂烧制，透气养茶"),
            models.Utensil(name="柴烧公道杯", category="茶海", material="粗陶", color="赭石", style="柴烧", price=240, quantity=3, available=3, description="柴烧窑变，独一无二"),
            
            models.Utensil(name="青瓷品茗杯", category="杯盏", material="青瓷", color="青色", style="汝窑", price=60, quantity=30, available=30, description="汝窑开片，养杯乐趣"),
            models.Utensil(name="白瓷蛋壳杯", category="杯盏", material="白瓷", color="象牙", style="极简", price=45, quantity=40, available=40, description="薄胎白瓷，轻盈雅致"),
            models.Utensil(name="紫砂小口杯", category="杯盏", material="紫砂", color="紫砂", style="仿古", price=70, quantity=25, available=25, description="紫砂小口，聚香品茗"),
            models.Utensil(name="手绘青花杯", category="杯盏", material="白瓷", color="青花", style="青花", price=85, quantity=20, available=20, description="手绘青花，文人气息"),
            models.Utensil(name="玻璃品茗杯", category="杯盏", material="玻璃", color="素白", style="设计感", price=35, quantity=50, available=50, description="玻璃直身，观汤色"),
            
            models.Utensil(name="棉麻茶席-米白", category="席布", material="棉麻", color="米白", style="禅意", price=120, quantity=10, available=10, description="天然棉麻，质朴温润"),
            models.Utensil(name="竹编茶席-原色", category="席布", material="竹编", color="金黄", style="自然", price=150, quantity=6, available=6, description="手工竹编，自然清香"),
            models.Utensil(name="织锦茶席-朱红", category="席布", material="织锦", color="朱红", style="粉彩", price=200, quantity=4, available=4, description="宋锦织造，富丽堂皇"),
            models.Utensil(name="亚麻茶席-藏青", category="席布", material="亚麻", color="藏青", style="简约", price=130, quantity=8, available=8, description="亚麻材质，素雅大方"),
            
            models.Utensil(name="青瓷小花瓶", category="花器", material="青瓷", color="青色", style="宋代", price=180, quantity=5, available=5, description="龙泉青瓷，器型雅致"),
            models.Utensil(name="粗陶禅意花器", category="花器", material="粗陶", color="灰墨", style="禅意", price=160, quantity=4, available=4, description="粗陶质感，禅意十足"),
            models.Utensil(name="铜制小花插", category="花器", material="铜器", color="琥珀", style="仿古", price=220, quantity=3, available=3, description="纯铜打造，复古优雅"),
            models.Utensil(name="白瓷玉净瓶", category="花器", material="白瓷", color="象牙", style="极简", price=140, quantity=6, available=6, description="玉净瓶型，清雅脱俗")
        ]
        db.add_all(utensils)
    
    db.commit()

def check_conflict(db: Session, check_date: date, time_slot: str, exclude_reservation_id: int = None, exclude_plan_id: int = None):
    conflicts = []
    
    plan_conflicts = db.query(models.TeaPlan).filter(
        models.TeaPlan.date == check_date,
        models.TeaPlan.status.in_(["confirmed", "borrowing", "completed"]))
    
    if exclude_plan_id:
        plan_conflicts = plan_conflicts.filter(models.TeaPlan.id != exclude_plan_id)
    
    plan_conflicts = plan_conflicts.all()
    
    for plan in plan_conflicts:
        if plan.time_slot == "全天" or time_slot == "全天" or plan.time_slot == time_slot:
            conflicts.append({
                "date": plan.date,
                "time_slot": plan.time_slot,
                "type": "plan",
                "id": plan.id,
                "name": plan.name,
                "customer_name": plan.customer_name
            })
    
    reservation_conflicts = db.query(models.Reservation).filter(
        models.Reservation.expected_date == check_date,
        models.Reservation.status.in_(["pending", "confirmed"]))
    
    if exclude_reservation_id:
        reservation_conflicts = reservation_conflicts.filter(models.Reservation.id != exclude_reservation_id)
    
    reservation_conflicts = reservation_conflicts.all()
    
    for res in reservation_conflicts:
        if res.time_slot == "全天" or time_slot == "全天" or res.time_slot == time_slot:
            conflicts.append({
                "date": res.expected_date,
                "time_slot": res.time_slot,
                "type": "reservation",
                "id": res.id,
                "name": f"客户预约-{res.customer_name}",
                "customer_name": res.customer_name
            })
    
    return conflicts

def get_reservations(db: Session, skip: int = 0, limit: int = 100, status: str = None, 
                    start_date: date = None, end_date: date = None,
                    tea_category: str = None, theme_color: str = None):
    query = db.query(models.Reservation)
    if status:
        query = query.filter(models.Reservation.status == status)
    if start_date:
        query = query.filter(models.Reservation.expected_date >= start_date)
    if end_date:
        query = query.filter(models.Reservation.expected_date <= end_date)
    if tea_category:
        query = query.filter(models.Reservation.preferred_tea == tea_category)
    if theme_color:
        query = query.filter(models.Reservation.preferred_color == theme_color)
    return query.order_by(models.Reservation.expected_date.desc()).offset(skip).limit(limit).all()

def get_reservation(db: Session, reservation_id: int):
    return db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()

def create_reservation(db: Session, reservation: schemas.ReservationCreate):
    db_reservation = models.Reservation(**reservation.model_dump())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def update_reservation(db: Session, reservation_id: int, reservation: schemas.ReservationUpdate):
    db_reservation = get_reservation(db, reservation_id)
    if not db_reservation:
        return None
    update_data = reservation.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reservation, key, value)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def convert_reservation_to_plan(db: Session, reservation_id: int, convert_request: schemas.ConvertToPlanRequest):
    db_reservation = get_reservation(db, reservation_id)
    if not db_reservation:
        return None
    
    theme = get_theme(db, convert_request.theme_id)
    theme_color = db_reservation.preferred_color or (theme.color if theme else None)
    tea_category = db_reservation.preferred_tea or (theme.tea_category if theme else None)
    photo_style = db_reservation.photo_style or (theme.style if theme else None)
    
    plan_data = schemas.TeaPlanCreate(
        theme_id=convert_request.theme_id,
        name=convert_request.name,
        date=db_reservation.expected_date,
        time_slot=db_reservation.time_slot,
        people_count=db_reservation.people_count,
        budget=db_reservation.budget,
        photo_style=photo_style,
        theme_color=theme_color,
        tea_category=tea_category,
        customer_name=db_reservation.customer_name,
        customer_phone=db_reservation.customer_phone,
        status="draft",
        selected_items=[]
    )
    
    db_plan = models.TeaPlan(
        **plan_data.model_dump(exclude={'selected_items'}),
        reservation_id=reservation_id
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    if theme_color and tea_category:
        recommendations = recommend_utensils(
            db, theme_color, tea_category,
            db_plan.people_count, db_plan.budget, db_plan.photo_style
        )
        
        total_price = 0
        for rec in recommendations:
            utensil = rec["utensil"]
            quantity = rec["quantity"]
            db_rec_item = models.RecommendedItem(
                plan_id=db_plan.id,
                utensil_id=utensil.id,
                quantity=quantity,
                selected=True
            )
            db.add(db_rec_item)
            total_price += utensil.price * quantity
        
        db_plan.total_price = total_price
        db.commit()
        db.refresh(db_plan)
    
    db_reservation.status = "converted"
    db.commit()
    db.refresh(db_reservation)
    
    return db_plan

def get_schedule_occupancy(db: Session, start_date: date, end_date: date, only_conflicts: bool = False):
    from datetime import timedelta
    
    days = []
    total_occupied = 0
    total_conflicts = 0
    
    current_date = start_date
    while current_date <= end_date:
        day_data = {
            "date": current_date,
            "has_conflict": False,
            "morning": [],
            "afternoon": [],
            "evening": [],
            "full_day": []
        }
        
        all_items = []
        
        plan_conflicts = db.query(models.TeaPlan).filter(
            models.TeaPlan.date == current_date,
            models.TeaPlan.status.in_(["confirmed", "borrowing", "completed"])
        ).all()
        
        for plan in plan_conflicts:
            item = {
                "id": f"plan_{plan.id}",
                "date": plan.date,
                "time_slot": plan.time_slot,
                "source_type": "plan",
                "source_name": plan.name,
                "customer_name": plan.customer_name,
                "business_type": "茶席方案",
                "status": plan.status,
                "related_id": plan.reservation_id
            }
            all_items.append(item)
        
        reservation_conflicts = db.query(models.Reservation).filter(
            models.Reservation.expected_date == current_date,
            models.Reservation.status.in_(["pending", "confirmed", "converted"])
        ).all()
        
        for res in reservation_conflicts:
            item = {
                "id": f"reservation_{res.id}",
                "date": res.expected_date,
                "time_slot": res.time_slot,
                "source_type": "reservation",
                "source_name": f"客户预约",
                "customer_name": res.customer_name,
                "business_type": "预约",
                "status": res.status,
                "related_id": None
            }
            all_items.append(item)
        
        for item in all_items:
            slot = item["time_slot"]
            if slot == "上午":
                day_data["morning"].append(item)
            elif slot == "下午":
                day_data["afternoon"].append(item)
            elif slot == "晚上":
                day_data["evening"].append(item)
            elif slot == "全天":
                day_data["full_day"].append(item)
        
        slot_groups = {
            "morning": day_data["morning"] + day_data["full_day"],
            "afternoon": day_data["afternoon"] + day_data["full_day"],
            "evening": day_data["evening"] + day_data["full_day"]
        }
        
        for slot_name, items in slot_groups.items():
            if len(items) > 1:
                day_data["has_conflict"] = True
                break
        
        if day_data["has_conflict"]:
            total_conflicts += 1
        
        day_count = len(all_items)
        if day_count > 0:
            total_occupied += 1
        
        if not only_conflicts or day_data["has_conflict"] or day_count > 0:
            days.append(day_data)
        
        current_date += timedelta(days=1)
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_occupied": total_occupied,
        "total_conflicts": total_conflicts,
        "days": days
    }

def get_reservation_statistics(db: Session):
    total_reservations = db.query(models.Reservation).count()
    confirmed_reservations = db.query(models.Reservation).filter(
        models.Reservation.status.in_(["confirmed", "converted"])).count()
    cancelled_reservations = db.query(models.Reservation).filter(
        models.Reservation.status == "cancelled").count()
    converted_plans = db.query(models.TeaPlan).filter(
        models.TeaPlan.reservation_id.isnot(None)).count()
    
    conversion_rate = 0.0
    if total_reservations > 0:
        conversion_rate = round(converted_plans / total_reservations * 100, 2)
    
    time_slot_stats = db.query(
        models.Reservation.time_slot,
        func.count(models.Reservation.id).label("count")
    ).filter(models.Reservation.status != "cancelled") \
     .group_by(models.Reservation.time_slot).all()
    
    popular_tea_stats = db.query(
        models.Reservation.preferred_tea.label("tea_category"),
        func.count(models.Reservation.id).label("count")
    ).filter(models.Reservation.preferred_tea.isnot(None), 
             models.Reservation.preferred_tea != '',
             models.Reservation.status != "cancelled") \
     .group_by(models.Reservation.preferred_tea) \
     .order_by(func.count(models.Reservation.id).desc()).limit(5).all()
    
    popular_color_stats = db.query(
        models.Reservation.preferred_color.label("theme_color"),
        func.count(models.Reservation.id).label("count")
    ).filter(models.Reservation.preferred_color.isnot(None), 
             models.Reservation.preferred_color != '',
             models.Reservation.status != "cancelled") \
     .group_by(models.Reservation.preferred_color) \
     .order_by(func.count(models.Reservation.id).desc()).limit(5).all()
    
    return {
        "conversion_rate": conversion_rate,
        "total_reservations": total_reservations,
        "confirmed_reservations": confirmed_reservations,
        "converted_plans": converted_plans,
        "cancelled_reservations": cancelled_reservations,
        "time_slot_stats": [{"time_slot": t, "count": c} for t, c in time_slot_stats],
        "popular_tea_stats": [{"tea_category": t, "count": c} for t, c in popular_tea_stats],
        "popular_color_stats": [{"theme_color": c, "count": n} for c, n in popular_color_stats]
    }
