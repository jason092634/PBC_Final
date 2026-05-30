# utils/recommender.py

from datetime import datetime, date


def get_expiring_ingredients(ingredients, days=3):
    """找出 days 天內即將過期的食材"""

    today = date.today()
    expiring_items = []

    for item in ingredients:
        expiry_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d").date()
        days_left = (expiry_date - today).days

        if 0 <= days_left <= days:
            expiring_items.append({
                "name": item["name"],
                "expiry_date": item["expiry_date"],
                "days_left": days_left
            })

    return expiring_items


def recommend_recipes(ingredients, recipes, warning_days=3):
    """根據現有食材與即期品推薦食譜"""

    fridge_names = [item["name"] for item in ingredients]

    expiring_items = get_expiring_ingredients(ingredients, warning_days)
    expiring_names = [item["name"] for item in expiring_items]

    results = []

    for recipe in recipes:
        recipe_name = recipe["title"]
        required_items = recipe["required_ingredients"].split("|")

        matched = []
        missing = []

        for food in required_items:
            if food in fridge_names:
                matched.append(food)
            else:
                missing.append(food)

        match_rate = round(len(matched) / len(required_items) * 100)

        uses_expiring = False
        for food in matched:
            if food in expiring_names:
                uses_expiring = True

        priority_score = match_rate
        if uses_expiring:
            priority_score += 30

        status = (
            "現有食材即可烹飪"
            if len(missing) == 0
            else f"缺少 {len(missing)} 項食材"
        )

        results.append({
            "name": recipe_name,
            "match_rate": match_rate,
            "ingredients": "、".join(required_items),
            "missing": "無" if len(missing) == 0 else "、".join(missing),
            "status": status,
            "uses_expiring": uses_expiring,
            "priority_score": priority_score,
            "instructions": recipe["instructions"]
        })

    results.sort(
        key=lambda x: x["priority_score"],
        reverse=True
    )

    return results