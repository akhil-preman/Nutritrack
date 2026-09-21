import csv
import os

FOOD_DATA = {}

# Get absolute path to the dataset to ensure it works regardless of where the app is run from
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(current_dir, 'dataset', 'indian_food_nutrition.csv')

# Load the huge dataset into memory on startup
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            food_name = row['food_name'].strip().lower()
            FOOD_DATA[food_name] = {
                "calories": float(row['calories']),
                "protein": float(row['protein']),
                "carbs": float(row['carbs']),
                "fats": float(row['fats']),
                "vit_c": float(row['vit_c']),
                "calcium": float(row['calcium']),
                "iron": float(row['iron'])
            }
except Exception as e:
    print(f"Error loading food dataset: {e}")

def get_food_nutrition(food_name):
    food_name = food_name.strip().lower()
    
    # 1. Try exact match first
    if food_name in FOOD_DATA:
        return FOOD_DATA[food_name]
        
    # 2. Try partial substring match (e.g., "egg" will match "egg (whole)")
    for key, data in FOOD_DATA.items():
        if food_name in key or key in food_name:
            return data
            
    return None

def suggest_foods(nutrient, limit=2):
    """
    Suggests the top foods from our database that are highest in a specific nutrient.
    This fulfills the "personalized diet suggestions with Indian food options" requirement.
    """
    sorted_foods = sorted(FOOD_DATA.items(), key=lambda x: x[1][nutrient], reverse=True)
    suggestions = [f.title() for f, data in sorted_foods[:limit]]
    return suggestions
