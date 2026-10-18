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

def search_food_names(query, limit=5):
    """
    Returns a list of food names that match the query string for autocomplete.
    """
    query = query.strip().lower()
    if not query:
        return []
    
    matches = []
    # Find items that start with the query first for better UX
    for key in FOOD_DATA.keys():
        if key.startswith(query):
            matches.append(key.title())
            if len(matches) >= limit:
                return matches
                
    # Then find substring matches if we haven't hit the limit
    for key in FOOD_DATA.keys():
        if query in key and key.title() not in matches:
            matches.append(key.title())
            if len(matches) >= limit:
                break
                
    return matches

def add_custom_food(name, calories, protein, carbs, fats, vit_c=0.0, calcium=0.0, iron=0.0):
    """
    Adds a new food item to FOOD_DATA in-memory and appends it to the CSV file permanently.
    """
    food_name = name.strip().lower()
    data = {
        "calories": float(calories),
        "protein": float(protein),
        "carbs": float(carbs),
        "fats": float(fats),
        "vit_c": float(vit_c),
        "calcium": float(calcium),
        "iron": float(iron)
    }
    FOOD_DATA[food_name] = data
    try:
        with open(csv_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([name.strip().title(), calories, protein, carbs, fats, vit_c, calcium, iron])
        return True
    except Exception as e:
        print(f"Error saving new food to CSV: {e}")
        return False

def delete_custom_food(food_name):
    """
    Deletes a food item from FOOD_DATA in-memory and removes it from the CSV file.
    """
    key = food_name.strip().lower()
    if key in FOOD_DATA:
        del FOOD_DATA[key]
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = list(csv.reader(f))
            if not reader:
                return True
            header = reader[0]
            new_rows = [header] + [row for row in reader[1:] if row and row[0].strip().lower() != key]
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(new_rows)
            return True
        except Exception as e:
            print(f"Error updating CSV: {e}")
            return False
    return False

def get_all_foods():
    """
    Returns a list of all foods sorted alphabetically.
    """
    items = []
    for name, data in sorted(FOOD_DATA.items(), key=lambda x: x[0]):
        items.append({
            "name": name.title(),
            "calories": data["calories"],
            "protein": data["protein"],
            "carbs": data["carbs"],
            "fats": data["fats"],
            "vit_c": data["vit_c"],
            "calcium": data["calcium"],
            "iron": data["iron"]
        })
    return items
