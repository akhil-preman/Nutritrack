"""
Script to parse raw_nuts_seeds.csv, filter out inedible/unsafe entries,
and integrate safe, high-nutrient nuts, seeds, and kernels into:
1. dataset/indian_food_nutrition.csv
2. dataset/food_ingredients.json
3. dataset/nuts_seeds_details.json
"""

import os
import csv
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_CSV = os.path.join(BASE_DIR, 'dataset', 'raw_nuts_seeds.csv')
MASTER_CSV = os.path.join(BASE_DIR, 'dataset', 'indian_food_nutrition.csv')
ING_JSON = os.path.join(BASE_DIR, 'dataset', 'food_ingredients.json')
DETAILS_JSON = os.path.join(BASE_DIR, 'dataset', 'nuts_seeds_details.json')

UNSAFE_KEYWORDS = [
    'not for consumption', 'inedible', 'not safe', 'not recommended',
    'discard', 'toxicity', 'do not include', 'no standard data'
]

def clean_entity_name(raw_name):
    # Remove botanical Latin names after hyphen: e.g. 'Almond (Badam - Prunus dulcis)' -> 'Almond (Badam)'
    name = re.sub(r'\s*-\s*[A-Z][a-z]+(?:\s+[a-z]+|\s+species|\s+var\.)*', '', raw_name)
    name = re.sub(r'\s*\(\s*\)', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def parse_range_or_num(s):
    if not s:
        return 0.0
    # Range like '25-30'
    m_range = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', s)
    if m_range:
        return round((float(m_range.group(1)) + float(m_range.group(2))) / 2.0, 1)
    m_single = re.search(r'(\d+(?:\.\d+)?)', s)
    if m_single:
        return float(m_single.group(1))
    return 0.0

def process():
    with open(RAW_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Total raw items: {len(rows)}")

    # Load existing master foods
    existing_foods = []
    existing_keys = set()
    with open(MASTER_CSV, 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            existing_foods.append(r)
            existing_keys.add(r['food_name'].strip().lower())

    # Load existing ingredients
    if os.path.exists(ING_JSON):
        with open(ING_JSON, 'r', encoding='utf-8') as f:
            ingredients_db = json.load(f)
    else:
        ingredients_db = {}

    details_db = {}
    added_foods = []

    for r in rows:
        raw_name = r['Name of the Entity'].strip()
        safety = (r.get('Safety Flag') or '').lower()
        nutr_text = r['Nutritious Components (per 100g)']
        benefits = r['Benefits of Eating (for 11-15 yr students)']
        daily = r['How Much to Eat Per Day']
        img = r.get('Image Link', '').strip()

        # Check safety
        is_unsafe = False
        for kw in UNSAFE_KEYWORDS:
            if kw in safety or kw in daily.lower() or 'not for consumption' in benefits.lower():
                is_unsafe = True
                break

        if is_unsafe:
            continue

        clean_name = clean_entity_name(raw_name)
        if not clean_name:
            continue

        # Extract calories
        cal_m = re.search(r'(?:approx\.?|~)?\s*(\d+(?:\.\d+)?)\s*kcal', nutr_text, re.IGNORECASE)
        cal = float(cal_m.group(1)) if cal_m else 0.0

        # Extract protein
        prot_m = re.search(r'protein\s*[~:]?\s*(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*g', nutr_text, re.IGNORECASE)
        prot = parse_range_or_num(prot_m.group(1)) if prot_m else 0.0

        # Extract fat
        fat_m = re.search(r'(?:healthy\s+fat|fat)\s*[~:]?\s*(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*g', nutr_text, re.IGNORECASE)
        fat = parse_range_or_num(fat_m.group(1)) if fat_m else 0.0

        # Extract carbs
        carb_m = re.search(r'carbs?\s*[~:]?\s*(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*g', nutr_text, re.IGNORECASE)
        if carb_m:
            carb = parse_range_or_num(carb_m.group(1))
        elif cal > 0 and (prot > 0 or fat > 0):
            carb = max(0.0, round((cal - (4.0 * prot) - (9.0 * fat)) / 4.0, 1))
        else:
            carb = 0.0

        # Extract calcium
        ca_m = re.search(r'calcium\s*[~:]?\s*(\d+(?:\.\d+)?)\s*mg', nutr_text, re.IGNORECASE)
        ca = float(ca_m.group(1)) if ca_m else 0.0

        # Extract iron
        fe_m = re.search(r'iron\s*[~:]?\s*(\d+(?:\.\d+)?)\s*mg', nutr_text, re.IGNORECASE)
        fe = float(fe_m.group(1)) if fe_m else 0.0

        # Extract vitamin C
        vc_m = re.search(r'vitamin\s*c\s*[~:]?\s*(\d+(?:\.\d+)?)\s*mg', nutr_text, re.IGNORECASE)
        vc = float(vc_m.group(1)) if vc_m else 0.0

        # If calories was missing but macros exist
        if cal == 0.0 and (prot > 0 or fat > 0 or carb > 0):
            cal = round((prot * 4.0) + (carb * 4.0) + (fat * 9.0), 1)

        if cal == 0.0 and prot == 0.0:
            continue

        # Extract serving unit from daily guidance
        if 'almond' in daily.lower():
            serv_unit = 'almonds'
        elif 'walnut' in daily.lower():
            serv_unit = 'walnuts'
        elif 'cashew' in daily.lower():
            serv_unit = 'cashews'
        elif 'kernel' in daily.lower():
            serv_unit = 'kernels'
        elif 'tablespoon' in daily.lower() or 'tbsp' in daily.lower():
            serv_unit = 'tablespoon'
        elif 'teaspoon' in daily.lower() or 'tsp' in daily.lower():
            serv_unit = 'teaspoon'
        elif 'handful' in daily.lower():
            serv_unit = 'small handful'
        elif 'piece' in daily.lower():
            serv_unit = 'pieces'
        else:
            serv_unit = 'serving'

        food_item = {
            'food_name': clean_name,
            'calories': str(cal),
            'protein': str(prot),
            'carbs': str(carb),
            'fats': str(fat),
            'vit_c': str(vc),
            'calcium': str(ca),
            'iron': str(fe),
            'serving_unit': serv_unit
        }

        # Store details
        details_db[clean_name.lower()] = {
            'name': clean_name,
            'category': 'Nuts, Seeds & Kernels',
            'benefits': benefits.strip(),
            'daily_portion': daily.strip(),
            'image_link': img
        }

        # Default ingredients
        ingredients_db[clean_name.lower()] = [
            f"100% Pure Whole {clean_name}"
        ]

        if clean_name.lower() not in existing_keys:
            added_foods.append(food_item)
            existing_keys.add(clean_name.lower())

    print(f"Adding {len(added_foods)} new edible nuts & seeds to master dataset...")

    # Write merged master dataset
    fieldnames = ['food_name', 'calories', 'protein', 'carbs', 'fats', 'vit_c', 'calcium', 'iron', 'serving_unit']
    all_foods = existing_foods + added_foods
    with open(MASTER_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in all_foods:
            writer.writerow(item)

    # Save ingredients JSON
    with open(ING_JSON, 'w', encoding='utf-8') as f:
        json.dump(ingredients_db, f, indent=2, ensure_ascii=False)

    # Save details JSON
    with open(DETAILS_JSON, 'w', encoding='utf-8') as f:
        json.dump(details_db, f, indent=2, ensure_ascii=False)

    print(f"Master dataset now contains: {len(all_foods)} foods!")
    print(f"Details saved for {len(details_db)} nuts & seeds.")

if __name__ == '__main__':
    process()
