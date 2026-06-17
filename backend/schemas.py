from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class ThemeBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str
    tea_category: str
    style: str
    min_people: int = 1
    max_people: int = 10
    min_budget: float = 0
    max_budget: float = 10000

class ThemeCreate(ThemeBase):
    pass

class Theme(ThemeBase):
    id: int
    
    class Config:
        from_attributes = True

class UtensilBase(BaseModel):
    name: str
    category: str
    material: str
    color: str
    style: str
    price: float
    quantity: int = 1
    available: int = 1
    description: Optional[str] = None
    image_url: Optional[str] = None

class UtensilCreate(UtensilBase):
    pass

class UtensilUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    available: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class Utensil(UtensilBase):
    id: int
    
    class Config:
        from_attributes = True

class RecommendedItemBase(BaseModel):
    utensil_id: int
    quantity: int = 1
    selected: bool = True

class RecommendedItemCreate(RecommendedItemBase):
    pass

class RecommendedItem(RecommendedItemBase):
    id: int
    utensil: Utensil
    
    class Config:
        from_attributes = True

class TeaPlanBase(BaseModel):
    theme_id: int
    name: str
    date: date
    people_count: int
    budget: float
    photo_style: str
    customer_name: str
    customer_phone: str
    status: str = "draft"

class TeaPlanCreate(TeaPlanBase):
    pass

class TeaPlanUpdate(BaseModel):
    theme_id: Optional[int] = None
    name: Optional[str] = None
    date: Optional[date] = None
    people_count: Optional[int] = None
    budget: Optional[float] = None
    photo_style: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    status: Optional[str] = None
    total_price: Optional[float] = None

class TeaPlan(TeaPlanBase):
    id: int
    total_price: float = 0
    theme: Optional[Theme] = None
    recommended_items: List[RecommendedItem] = []
    
    class Config:
        from_attributes = True

class BorrowItemBase(BaseModel):
    utensil_id: int
    quantity: int
    borrowed: bool = False
    returned: bool = False

class BorrowItemCreate(BorrowItemBase):
    pass

class BorrowItemUpdate(BaseModel):
    borrowed: Optional[bool] = None
    returned: Optional[bool] = None

class BorrowItem(BorrowItemBase):
    id: int
    utensil: Utensil
    
    class Config:
        from_attributes = True

class BorrowListBase(BaseModel):
    plan_id: int
    borrow_date: date
    return_date: date
    status: str = "pending"

class BorrowListCreate(BorrowListBase):
    items: List[BorrowItemCreate]

class BorrowListUpdate(BaseModel):
    borrow_date: Optional[date] = None
    return_date: Optional[date] = None
    status: Optional[str] = None

class BorrowList(BorrowListBase):
    id: int
    items: List[BorrowItem] = []
    
    class Config:
        from_attributes = True

class ReviewItemBase(BaseModel):
    utensil_id: int
    damaged: bool = False
    damage_description: Optional[str] = None
    cleaned: bool = False

class ReviewItemCreate(ReviewItemBase):
    pass

class ReviewItemUpdate(BaseModel):
    damaged: Optional[bool] = None
    damage_description: Optional[str] = None
    cleaned: Optional[bool] = None

class ReviewItem(ReviewItemBase):
    id: int
    utensil: Utensil
    
    class Config:
        from_attributes = True

class ActivityReviewBase(BaseModel):
    plan_id: int
    review_date: date
    customer_feedback: Optional[str] = None
    rating: int
    is_repeat_customer: bool = False

class ActivityReviewCreate(ActivityReviewBase):
    items: List[ReviewItemCreate]

class ActivityReviewUpdate(BaseModel):
    customer_feedback: Optional[str] = None
    rating: Optional[int] = None
    is_repeat_customer: Optional[bool] = None

class ActivityReview(ActivityReviewBase):
    id: int
    items: List[ReviewItem] = []
    plan: TeaPlan
    
    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    theme_color: str
    tea_category: str
    people_count: int
    budget: float
    photo_style: str

class ThemeStats(BaseModel):
    theme_name: str
    count: int

class UtensilUsageStats(BaseModel):
    utensil_name: str
    category: str
    usage_count: int

class DamageStats(BaseModel):
    utensil_name: str
    category: str
    damage_count: int
    damage_rate: float

class PriceRangeStats(BaseModel):
    range: str
    count: int

class RepeatTypeStats(BaseModel):
    tea_type: str
    count: int

class StatisticsResponse(BaseModel):
    theme_stats: List[ThemeStats]
    utensil_usage_stats: List[UtensilUsageStats]
    damage_stats: List[DamageStats]
    price_range_stats: List[PriceRangeStats]
    repeat_type_stats: List[RepeatTypeStats]
    total_orders: int
    total_revenue: float
    avg_rating: float
