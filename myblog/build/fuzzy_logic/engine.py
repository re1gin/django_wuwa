# engine.py

import numpy as np
from build.constants import MAX_BONUS_DMG_PERCENT

def triangular_membership_flat(x, a, b, c):
    if x <= a:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    elif b < x <= c:
        return 1.0 - (x - b) / (c - b)
    else:
        return 0.0

def trapezoidal_membership_percent(x, a, b, c, d):
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif c < x < d:
        return 1.0 - (x - c) / (d - c)

def bonus_stat_membership(x, max_val):
    if x <= 0:
        return 0.0
    elif x >= max_val:
        return 1.0
    else:
        return x / max_val

def calculate_fuzzy_stat_quality(ideal_val, user_val, stat_category, stat_name=None, is_role_priority=False):
    score = 0.0
    if stat_category == 'flat':
        if ideal_val <= 0:
            if user_val == 0:
                score = 100.0
            else:
                score = max(0.0, 100.0 - (user_val / ideal_val if ideal_val else user_val) * 10)
        else:
            score = (user_val / ideal_val) * 100.0
    elif stat_category == 'percent':
        if ideal_val <= 0:
             if user_val == 0:
                score = 100.0
             else:
                score = max(0.0, 100.0 - user_val * 2)
        else:
            score = (user_val / ideal_val) * 100.0
    elif stat_category == 'bonus':
        if stat_name not in MAX_BONUS_DMG_PERCENT:
            return 0.0
        max_bonus = MAX_BONUS_DMG_PERCENT[stat_name]
        if is_role_priority:
            score = bonus_stat_membership(user_val, max_bonus) * 100.0
            if user_val == 0:
                score = 0.0
        else:
            if user_val == 0:
                score = 100.0
            else:
                penalty = (user_val / max_bonus) * 100.0
                score = max(0.0, 100.0 - penalty)
    return max(0.0, min(100.0, score))

def get_overall_build_rating_text(rating):
    if rating >= 95:
        return "Masterpiece Build!"
    elif rating >= 90:
        return "Exceptional Build!"
    elif rating >= 80:
        return "Great Build!"
    elif rating >= 70:
        return "Good Build"
    elif rating >= 60:
        return "Decent Build"
    elif rating >= 50:
        return "Acceptable Build"
    else:
        return "Needs Improvement"
