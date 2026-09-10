# utils/food_db.py

# Expanded database to include vitamins/minerals for personalized diet suggestions.
FOOD_DATA = {
    # Food Name: Calories, Protein, Carbs, Fats, Vitamin C (mg), Calcium (mg), Iron (mg)
    "chapati": {"calories": 104, "protein": 3.0, "carbs": 22.0, "fats": 0.4, "vit_c": 0, "calcium": 10, "iron": 1.5},
    "paneer butter masala": {"calories": 350, "protein": 12.0, "carbs": 15.0, "fats": 28.0, "vit_c": 5, "calcium": 250, "iron": 1.0},
    "dal tadka": {"calories": 210, "protein": 11.0, "carbs": 29.0, "fats": 6.0, "vit_c": 2, "calcium": 40, "iron": 3.0},
    "biryani": {"calories": 450, "protein": 18.0, "carbs": 60.0, "fats": 15.0, "vit_c": 4, "calcium": 30, "iron": 2.5},
    "palak paneer": {"calories": 280, "protein": 14.0, "carbs": 11.0, "fats": 20.0, "vit_c": 15, "calcium": 300, "iron": 4.5}, # High in Iron/Calcium
    "orange": {"calories": 60, "protein": 1.2, "carbs": 15.0, "fats": 0.2, "vit_c": 70, "calcium": 40, "iron": 0.1}, # High in Vit C
    "milk": {"calories": 42, "protein": 3.4, "carbs": 5.0, "fats": 1.0, "vit_c": 0, "calcium": 125, "iron": 0.0}, # High in Calcium
    "chicken curry": {"calories": 250, "protein": 25.0, "carbs": 5.0, "fats": 14.0, "vit_c": 2, "calcium": 15, "iron": 1.2},
    "dosa": {"calories": 133, "protein": 3.9, "carbs": 29.0, "fats": 0.2, "vit_c": 1, "calcium": 10, "iron": 0.5},
}

def get_food_nutrition(food_name):
    food_name = food_name.strip().lower()
    return FOOD_DATA.get(food_name, None)

def suggest_foods(nutrient, limit=2):
    """
    Suggests the top foods from our database that are highest in a specific nutrient.
    This fulfills the "personalized diet suggestions with Indian food options" requirement.
    """
    sorted_foods = sorted(FOOD_DATA.items(), key=lambda x: x[1][nutrient], reverse=True)
    suggestions = [f.title() for f, data in sorted_foods[:limit]]
    return suggestions
