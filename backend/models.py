from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Theme(Base):
    __tablename__ = "themes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    color = Column(String(50))
    tea_category = Column(String(50))
    style = Column(String(50))
    min_people = Column(Integer, default=1)
    max_people = Column(Integer, default=10)
    min_budget = Column(Float, default=0)
    max_budget = Column(Float, default=10000)
    
    plans = relationship("TeaPlan", back_populates="theme")

class Utensil(Base):
    __tablename__ = "utensils"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    category = Column(String(50), index=True)
    material = Column(String(50))
    color = Column(String(50))
    style = Column(String(50))
    price = Column(Float)
    quantity = Column(Integer, default=1)
    available = Column(Integer, default=1)
    description = Column(Text)
    image_url = Column(String(255))
    
    borrow_items = relationship("BorrowItem", back_populates="utensil")
    review_items = relationship("ReviewItem", back_populates="utensil")

class TeaPlan(Base):
    __tablename__ = "tea_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"))
    name = Column(String(100))
    date = Column(Date)
    time_slot = Column(String(20), default="全天")
    people_count = Column(Integer)
    budget = Column(Float)
    photo_style = Column(String(50))
    theme_color = Column(String(50))
    tea_category = Column(String(50))
    status = Column(String(20), default="draft")
    customer_name = Column(String(100))
    customer_phone = Column(String(20))
    total_price = Column(Float, default=0)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    
    theme = relationship("Theme", back_populates="plans")
    borrow_list = relationship("BorrowList", back_populates="plan", uselist=False)
    review = relationship("ActivityReview", back_populates="plan", uselist=False)
    recommended_items = relationship("RecommendedItem", back_populates="plan")
    reservation = relationship("Reservation", back_populates="plans", foreign_keys=[reservation_id])

class RecommendedItem(Base):
    __tablename__ = "recommended_items"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("tea_plans.id"))
    utensil_id = Column(Integer, ForeignKey("utensils.id"))
    quantity = Column(Integer, default=1)
    selected = Column(Boolean, default=True)
    
    plan = relationship("TeaPlan", back_populates="recommended_items")
    utensil = relationship("Utensil")

class BorrowList(Base):
    __tablename__ = "borrow_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("tea_plans.id"))
    borrow_date = Column(Date)
    return_date = Column(Date)
    status = Column(String(20), default="pending")
    
    plan = relationship("TeaPlan", back_populates="borrow_list")
    items = relationship("BorrowItem", back_populates="borrow_list")

class BorrowItem(Base):
    __tablename__ = "borrow_items"
    
    id = Column(Integer, primary_key=True, index=True)
    borrow_list_id = Column(Integer, ForeignKey("borrow_lists.id"))
    utensil_id = Column(Integer, ForeignKey("utensils.id"))
    quantity = Column(Integer)
    borrowed = Column(Boolean, default=False)
    returned = Column(Boolean, default=False)
    
    borrow_list = relationship("BorrowList", back_populates="items")
    utensil = relationship("Utensil", back_populates="borrow_items")

class ActivityReview(Base):
    __tablename__ = "activity_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("tea_plans.id"))
    review_date = Column(Date)
    customer_feedback = Column(Text)
    rating = Column(Integer)
    is_repeat_customer = Column(Boolean, default=False)
    
    plan = relationship("TeaPlan", back_populates="review")
    items = relationship("ReviewItem", back_populates="review")

class ReviewItem(Base):
    __tablename__ = "review_items"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("activity_reviews.id"))
    utensil_id = Column(Integer, ForeignKey("utensils.id"))
    damaged = Column(Boolean, default=False)
    damage_description = Column(Text)
    cleaned = Column(Boolean, default=False)
    
    review = relationship("ActivityReview", back_populates="items")
    utensil = relationship("Utensil", back_populates="review_items")

class Reservation(Base):
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    expected_date = Column(Date, nullable=False)
    time_slot = Column(String(20), nullable=False, default="全天")
    people_count = Column(Integer, nullable=False, default=1)
    budget = Column(Float, nullable=False, default=0)
    preferred_color = Column(String(50))
    preferred_tea = Column(String(50))
    photo_style = Column(String(50))
    remark = Column(Text)
    status = Column(String(20), default="pending")
    
    plans = relationship("TeaPlan", back_populates="reservation", foreign_keys="TeaPlan.reservation_id")
