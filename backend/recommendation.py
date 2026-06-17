from sqlalchemy.orm import Session
from models import Utensil
from typing import List, Dict
import random

CATEGORY_PRIORITY = {
    "盖碗": 1,
    "茶海": 1,
    "杯盏": 2,
    "席布": 1,
    "花器": 3
}

COLOR_MATCH_SCORES = {
    "同色系": 10,
    "邻近色": 7,
    "对比色": 5,
    "中性色": 6
}

def get_color_relationship(color1: str, color2: str) -> str:
    warm_colors = ["朱红", "赭石", "胭脂", "琥珀", "金黄", "橙黄"]
    cool_colors = ["青色", "湖蓝", "黛绿", "松石", "月白", "藏青"]
    neutral_colors = ["米白", "象牙", "玄黑", "紫砂", "灰墨", "素白"]
    
    def get_color_family(c):
        if c in warm_colors:
            return "warm"
        elif c in cool_colors:
            return "cool"
        elif c in neutral_colors:
            return "neutral"
        return "neutral"
    
    f1, f2 = get_color_family(color1), get_color_family(color2)
    
    if f1 == f2 and f1 != "neutral":
        return "同色系"
    elif f1 == "neutral" or f2 == "neutral":
        return "中性色"
    elif (f1 == "warm" and f2 == "cool") or (f1 == "cool" and f2 == "warm"):
        return "对比色"
    else:
        return "邻近色"

def calculate_utensil_score(utensil: Utensil, theme_color: str, tea_category: str, 
                          budget: float, photo_style: str) -> float:
    score = 0.0
    
    color_rel = get_color_relationship(utensil.color, theme_color)
    score += COLOR_MATCH_SCORES.get(color_rel, 5)
    
    tea_matches = {
        "绿茶": ["青瓷", "白瓷", "玻璃"],
        "红茶": ["紫砂", "朱泥", "白瓷"],
        "乌龙茶": ["紫砂", "朱泥", "青瓷"],
        "普洱茶": ["紫砂", "粗陶", "柴烧"],
        "白茶": ["白瓷", "青瓷", "玻璃"],
        "黄茶": ["黄釉", "白瓷", "青瓷"]
    }
    
    if utensil.material in tea_matches.get(tea_category, []):
        score += 8
    
    style_matches = {
        "宋韵古风": ["宋代", "仿古", "汝窑"],
        "禅意极简": ["极简", "禅意", "粗陶"],
        "文人雅集": ["青花", "手绘", "粉彩"],
        "现代新中式": ["现代", "简约", "设计感"],
        "自然山野": ["粗陶", "柴烧", "土陶"]
    }
    
    if utensil.style in style_matches.get(photo_style, []):
        score += 7
    
    if utensil.price <= budget * 0.3:
        score += 6
    elif utensil.price <= budget * 0.5:
        score += 4
    elif utensil.price <= budget:
        score += 2
    
    if utensil.available > 0:
        score += 5
    
    score += random.uniform(-1, 1)
    
    return score

def recommend_utensils(db: Session, theme_color: str, tea_category: str, 
                      people_count: int, budget: float, photo_style: str) -> List[Dict]:
    categories = ["盖碗", "茶海", "杯盏", "席布", "花器"]
    recommendations = []
    
    remaining_budget = budget
    
    for category in categories:
        utensils = db.query(Utensil).filter(
            Utensil.category == category,
            Utensil.available > 0
        ).all()
        
        if not utensils:
            continue
        
        scored_utensils = []
        for utensil in utensils:
            if utensil.price > remaining_budget:
                continue
            score = calculate_utensil_score(utensil, theme_color, tea_category, budget, photo_style)
            scored_utensils.append((utensil, score))
        
        scored_utensils.sort(key=lambda x: x[1], reverse=True)
        
        if scored_utensils:
            selected, score = scored_utensils[0]
            quantity = people_count if category == "杯盏" else 1
            
            recommendations.append({
                "utensil": selected,
                "quantity": quantity,
                "score": score,
                "category": category
            })
            
            remaining_budget -= selected.price * quantity
    
    return recommendations
