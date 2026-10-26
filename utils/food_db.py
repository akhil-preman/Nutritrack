import csv
import json
import os
import re

FOOD_DATA = {}
FOOD_ALIASES = {}
CANONICAL_NAMES = {}
FOOD_INGREDIENTS = {}
NUTS_SEEDS_DETAILS = {}

# Get absolute path to the dataset to ensure it works regardless of where the app is run from
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(current_dir, 'dataset', 'indian_food_nutrition.csv')
ingredients_path = os.path.join(current_dir, 'dataset', 'food_ingredients.json')
details_path = os.path.join(current_dir, 'dataset', 'nuts_seeds_details.json')

STOP_WORDS = {'ka', 'ki', 'ke', 'aur', 'and', 'with', 'in', 'of', 'the', 'a', 'an'}

def expand_slashes(text):
    """
    Recursively expands words with slashes e.g. 'parantha/paratha' -> ['parantha', 'paratha']
    """
    slash_match = re.search(r'(\w+)/(\w+)', text)
    if not slash_match:
        return [text]
    t1, t2 = slash_match.group(1), slash_match.group(2)
    s1 = text[:slash_match.start()] + t1 + text[slash_match.end():]
    s2 = text[:slash_match.start()] + t2 + text[slash_match.end():]
    res = []
    for r in [s1, s2]:
        res.extend(expand_slashes(r))
    return res

def get_aliases_for_name(name):
    """
    Generates alternative search keywords (Hindi / regional names, English variants,
    slash expansions) for a given food title.
    """
    lower = name.lower().strip()
    aliases = {lower}
    
    # 1. Expand outside and inside parentheses e.g. 'Hot tea (Garam Chai)'
    paren_match = re.search(r'^(.*?)\s*\((.*?)\)$', lower)
    candidates = []
    if paren_match:
        candidates.extend([paren_match.group(1).strip(), paren_match.group(2).strip()])
    else:
        candidates.append(lower)
        
    for cand in candidates:
        for exp in expand_slashes(cand):
            clean = re.sub(r'[^\w\s]', ' ', exp)
            clean = re.sub(r'\s+', ' ', clean).strip()
            if clean and len(clean) > 2:
                aliases.add(clean)
                words_no_stop = [w for w in clean.split() if w not in STOP_WORDS]
                if len(words_no_stop) >= 2:
                    aliases.add(' '.join(words_no_stop))
                if 'zeera' in clean:
                    aliases.add(clean.replace('zeera', 'jeera'))
                if 'jeere' in clean:
                    aliases.add(clean.replace('jeere', 'jeera'))
                    
    return list(aliases)

def load_food_dataset():
    FOOD_DATA.clear()
    FOOD_ALIASES.clear()
    CANONICAL_NAMES.clear()
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_name = row['food_name'].strip()
                food_key = raw_name.lower()
                
                FOOD_DATA[food_key] = {
                    "calories": float(row.get('calories', 0) or 0),
                    "protein": float(row.get('protein', 0) or 0),
                    "carbs": float(row.get('carbs', 0) or 0),
                    "fats": float(row.get('fats', 0) or 0),
                    "vit_c": float(row.get('vit_c', 0) or 0),
                    "calcium": float(row.get('calcium', 0) or 0),
                    "iron": float(row.get('iron', 0) or 0),
                    "serving_unit": row.get('serving_unit', '').strip()
                }
                CANONICAL_NAMES[food_key] = raw_name
                
                for alias in get_aliases_for_name(raw_name):
                    FOOD_ALIASES[alias] = food_key
    except Exception as e:
        print(f"Error loading food dataset: {e}")

    # Load ingredients mapping
    global FOOD_INGREDIENTS, NUTS_SEEDS_DETAILS
    try:
        if os.path.exists(ingredients_path):
            with open(ingredients_path, 'r', encoding='utf-8') as f:
                FOOD_INGREDIENTS = json.load(f)
    except Exception as e:
        print(f"Error loading food ingredients: {e}")

    try:
        if os.path.exists(details_path):
            with open(details_path, 'r', encoding='utf-8') as f:
                NUTS_SEEDS_DETAILS = json.load(f)
                
            # Register comprehensive aliases for all nuts and seeds
            for k in NUTS_SEEDS_DETAILS:
                clean_k = re.sub(r'\([^)]*\)', '', k).strip()
                clean_k = re.sub(r'[\s/]+', ' ', clean_k).strip()
                parens = re.findall(r'\(([^)]+)\)', k)
                candidates = [clean_k]
                for p in parens:
                    for sub in p.split('/'):
                        sub_clean = re.sub(r'[^\w\s]', ' ', sub).strip()
                        sub_clean = re.sub(r'\s+', ' ', sub_clean).strip()
                        if sub_clean:
                            candidates.append(sub_clean)
                for c in list(candidates):
                    for suf in [' seeds', ' seed', ' nuts', ' nut', ' beej', ' magaz', ' kernel', ' kernels']:
                        if suf in c:
                            base = c.replace(suf, '').strip()
                            if len(base) >= 3:
                                candidates.append(base)
                    for pref in ['safed ', 'kala ', 'white ', 'black ']:
                        if c.startswith(pref):
                            base = c[len(pref):].strip()
                            if len(base) >= 3:
                                candidates.append(base)
                for c in candidates:
                    if len(c) >= 3 and c not in FOOD_ALIASES:
                        FOOD_ALIASES[c] = k
                    if c.endswith('s') and len(c) > 3 and c[:-1] not in FOOD_ALIASES:
                        FOOD_ALIASES[c[:-1]] = k
                    elif not c.endswith('s') and len(c) >= 3 and (c + 's') not in FOOD_ALIASES:
                        FOOD_ALIASES[c + 's'] = k
                        
            # Curated popular search aliases and staples for direct 1-to-1 matching
            popular_aliases = {
                'rice': 'rice (boiled white rice / chawal)',
                'chawal': 'rice (boiled white rice / chawal)',
                'bhaat': 'rice (boiled white rice / chawal)',
                'boiled rice': 'rice (boiled white rice / chawal)',
                'white rice': 'rice (boiled white rice / chawal)',
                'milk': 'milk (cow milk / doodh)',
                'doodh': 'milk (cow milk / doodh)',
                'cow milk': 'milk (cow milk / doodh)',
                'bread': 'white bread (slice)',
                'white bread': 'white bread (slice)',
                'brown bread': 'brown bread (slice)',
                'egg': 'boiled egg (anda)',
                'eggs': 'boiled egg (anda)',
                'anda': 'boiled egg (anda)',
                'boiled egg': 'boiled egg (anda)',
                'dal': 'dal (yellow dal tadka)',
                'daal': 'dal (yellow dal tadka)',
                'yellow dal': 'dal (yellow dal tadka)',
                'dal tadka': 'dal (yellow dal tadka)',
                'roti': 'roti (whole wheat chapati / phulka)',
                'rotis': 'roti (whole wheat chapati / phulka)',
                'phulka': 'roti (whole wheat chapati / phulka)',
                'chapati': 'roti (whole wheat chapati / phulka)',
                'chapatis': 'roti (whole wheat chapati / phulka)',
                'tea': 'tea with milk and sugar (chai)',
                'chai': 'tea with milk and sugar (chai)',
                'hot tea': 'tea with milk and sugar (chai)',
                'coffee': 'coffee with milk (hot coffee)',
                'hot coffee': 'coffee with milk (hot coffee)',
                'curd': 'curd',
                'dahi': 'curd',
                'sambar': 'sambar',
                'almond': 'almond (badam)',
                'almonds': 'almond (badam)',
                'badam': 'almond (badam)',
                'walnut': 'walnut (akhrot)',
                'walnuts': 'walnut (akhrot)',
                'akhrot': 'walnut (akhrot)',
                'cashew': 'cashew nut (kaju)',
                'cashews': 'cashew nut (kaju)',
                'kaju': 'cashew nut (kaju)',
                'pistachio': 'pistachio (pista)',
                'pistachios': 'pistachio (pista)',
                'pista': 'pistachio (pista)',
                'chia': 'chia seeds (salvia hispanica)',
                'chia seed': 'chia seeds (salvia hispanica)',
                'chia seeds': 'chia seeds (salvia hispanica)',
                'flax': 'flaxseeds (alsi)',
                'flaxseed': 'flaxseeds (alsi)',
                'flaxseeds': 'flaxseeds (alsi)',
                'alsi': 'flaxseeds (alsi)',
                'pumpkin seed': 'pumpkin seeds (kaddu beej / pepita)',
                'pumpkin seeds': 'pumpkin seeds (kaddu beej / pepita)',
                'kaddu beej': 'pumpkin seeds (kaddu beej / pepita)',
                'pepita': 'pumpkin seeds (kaddu beej / pepita)',
                'pepitas': 'pumpkin seeds (kaddu beej / pepita)',
                'sunflower seed': 'sunflower seeds (surajmukhi beej)',
                'sunflower seeds': 'sunflower seeds (surajmukhi beej)',
                'surajmukhi': 'sunflower seeds (surajmukhi beej)',
                'peanut': 'peanut / groundnut (mungfali)',
                'peanuts': 'peanut / groundnut (mungfali)',
                'mungfali': 'peanut / groundnut (mungfali)',
                'groundnut': 'peanut / groundnut (mungfali)',
                'pine nut': 'pine nut (chilgoza)',
                'pine nuts': 'pine nut (chilgoza)',
                'chilgoza': 'pine nut (chilgoza)',
                'hazelnut': 'hazelnut (pahadi badam)',
                'hazelnuts': 'hazelnut (pahadi badam)',
                'til': 'white sesame seeds (safed til)',
                'sesame': 'white sesame seeds (safed til)',
                'sesame seeds': 'white sesame seeds (safed til)',
                'safed til': 'white sesame seeds (safed til)',
                'kala til': 'black sesame seeds (kala til.)',
                'sabja': 'basil seeds (sabja / tukmaria)',
                'tukmaria': 'basil seeds (sabja / tukmaria)'
            }
            for pa, p_canon in popular_aliases.items():
                if p_canon in CANONICAL_NAMES:
                    FOOD_ALIASES[pa] = p_canon
    except Exception as e:
        print(f"Error loading nuts & seeds details: {e}")

# Load on startup
load_food_dataset()

def get_food_details_extra(food_name):
    """
    Returns optional extra details like health benefits, daily portions, or image links
    for specialized superfoods (like nuts and seeds) if available.
    """
    if not food_name:
        return {}
    key = food_name.strip().lower()
    if key in NUTS_SEEDS_DETAILS:
        return NUTS_SEEDS_DETAILS[key]
    if key in FOOD_ALIASES and FOOD_ALIASES[key] in NUTS_SEEDS_DETAILS:
        return NUTS_SEEDS_DETAILS[FOOD_ALIASES[key]]
    for k, v in NUTS_SEEDS_DETAILS.items():
        if key in k or k in key:
            return v
    return {}

def get_food_ingredients(food_name):
    """
    Returns the list of default ingredients for a given food or recipe name.
    """
    if not food_name:
        return []
    key = food_name.strip().lower()
    
    # 1. Uncooked single items check (egg, fruits, fresh veggies)
    for item in UNCOOKED_SINGLE_ITEMS:
        if item == key or key.startswith(item + ' ') or key.endswith(' ' + item) or f' {item} ' in key:
            return [f"100% Whole fresh {food_name.title()}"]
    
    # 2. Exact match in FOOD_INGREDIENTS
    if key in FOOD_INGREDIENTS:
        return FOOD_INGREDIENTS[key]
        
    # 3. Check canonical name from FOOD_ALIASES
    if key in FOOD_ALIASES:
        canon = FOOD_ALIASES[key]
        if canon in FOOD_INGREDIENTS:
            return FOOD_INGREDIENTS[canon]

    # 4. Substring match using word boundaries
    for k, v in FOOD_INGREDIENTS.items():
        if re.search(r'\b' + re.escape(key) + r'\b', k) or re.search(r'\b' + re.escape(k) + r'\b', key):
            return v

    # 5. Token overlap match
    tokens = [w for w in key.split() if w not in STOP_WORDS]
    if len(tokens) >= 2:
        for k, v in FOOD_INGREDIENTS.items():
            if all(t in k for t in tokens):
                return v

    return ["Traditional Indian home recipe ingredients"]

def get_canonical_food_name(food_name):
    """
    Returns the official canonical food name (e.g. 'Apple', 'Almond (Badam)', 'Rice (Boiled White Rice / Chawal)')
    if the food exists in our database, or None if it's NOT in the database.
    Prevents single alphabets or non-existent items from matching.
    """
    if not food_name:
        return None
    key = food_name.strip().lower()
    
    # Single-letter or 2-letter queries (unless an exact canonical item/alias) must never match
    if len(key) < 3 and key not in FOOD_DATA and key not in FOOD_ALIASES:
        return None
        
    # 1. Exact match in canonical keys
    if key in FOOD_DATA:
        return CANONICAL_NAMES.get(key, key.title())
        
    # 2. Exact match in aliases
    if key in FOOD_ALIASES and FOOD_ALIASES[key] in FOOD_DATA:
        canon_key = FOOD_ALIASES[key]
        return CANONICAL_NAMES.get(canon_key, canon_key.title())
        
    # 3. Normalized alphanumeric match (clean punctuation differences)
    clean_key = re.sub(r'[^\w\s]', ' ', key)
    clean_key = re.sub(r'\s+', ' ', clean_key).strip()
    if clean_key in FOOD_ALIASES and FOOD_ALIASES[clean_key] in FOOD_DATA:
        canon_key = FOOD_ALIASES[clean_key]
        return CANONICAL_NAMES.get(canon_key, canon_key.title())
        
    # 4. Multi-token whole-word match (e.g. 'aloo paratha')
    # Strictly requires >= 2 meaningful words (len >= 3) matching as whole words
    q_tokens = [w for w in key.split() if w not in STOP_WORDS and len(w) >= 3]
    if len(q_tokens) >= 2:
        for alias, canon_key in FOOD_ALIASES.items():
            if all(re.search(r'\b' + re.escape(qt) + r'\b', alias) for qt in q_tokens):
                return CANONICAL_NAMES.get(canon_key, canon_key.title())
                
    return None

def get_food_nutrition(food_name):
    """
    Returns the nutrition dictionary for a food if it exists in our database, or None.
    Strictly avoids false-positive substring matches on single letters or arbitrary words.
    """
    if not food_name:
        return None
    key = food_name.strip().lower()
    if len(key) < 3 and key not in FOOD_DATA and key not in FOOD_ALIASES:
        return None
        
    # 1. Exact match in canonical keys
    if key in FOOD_DATA:
        return FOOD_DATA[key]
        
    # 2. Exact match in aliases
    if key in FOOD_ALIASES and FOOD_ALIASES[key] in FOOD_DATA:
        return FOOD_DATA[FOOD_ALIASES[key]]
        
    # 3. Canonical name resolution
    c_name = get_canonical_food_name(food_name)
    if c_name:
        c_key = c_name.strip().lower()
        if c_key in FOOD_DATA:
            return FOOD_DATA[c_key]
        if c_key in FOOD_ALIASES and FOOD_ALIASES[c_key] in FOOD_DATA:
            return FOOD_DATA[FOOD_ALIASES[c_key]]
            
    return None

def suggest_foods(nutrient, limit=2):
    """
    Suggests the top foods from our database that are highest in a specific nutrient.
    This fulfills the "personalized diet suggestions with Indian food options" requirement.
    """
    sorted_foods = sorted(FOOD_DATA.items(), key=lambda x: x[1][nutrient], reverse=True)
    suggestions = []
    for f, data in sorted_foods:
        c_name = CANONICAL_NAMES.get(f, f.title())
        if c_name not in suggestions:
            suggestions.append(c_name)
            if len(suggestions) >= limit:
                break
    return suggestions

POPULAR_NUTS_SEEDS_CATEGORIES = {
    'nuts': [
        'almond (badam)',
        'walnut (akhrot)',
        'cashew nut (kaju)',
        'pistachio (pista)',
        'peanut / groundnut (mungfali)',
        'pine nut (chilgoza)',
        'hazelnut (pahadi badam)'
    ],
    'seeds': [
        'chia seeds (salvia hispanica)',
        'flaxseeds (alsi)',
        'pumpkin seeds (kaddu beej / pepita)',
        'sunflower seeds (surajmukhi beej)',
        'basil seeds (sabja / tukmaria)',
        'white sesame seeds (safed til)',
        'watermelon seeds (tarbuz magaz)'
    ]
}

def is_nut_or_seed(name_or_key):
    """
    Returns True if a food belongs to the specialized nuts & seeds dataset.
    """
    if not name_or_key:
        return False
    k = name_or_key.strip().lower()
    if k in NUTS_SEEDS_DETAILS:
        return True
    if k in FOOD_ALIASES and FOOD_ALIASES[k] in NUTS_SEEDS_DETAILS:
        return True
    for dk in NUTS_SEEDS_DETAILS:
        if k == dk or k.startswith(dk + ' ') or f'({k})' in dk:
            return True
    return False

def search_food_names(query, limit=5):
    """
    Returns a list of food names that match the query string for autocomplete.
    Uses category triggers, canonical titles, aliases, prefix, substring, and token matching.
    Prioritizes pure standalone nuts and seeds for nut/seed queries.
    """
    query = query.strip().lower()
    if not query:
        return []

    # 1. Category keywords (e.g. 'nuts', 'seeds', 'dry fruits')
    if query in {'nut', 'nuts', 'dry fruit', 'dry fruits', 'dryfruit', 'dryfruits', 'superfood', 'superfoods'}:
        res = [CANONICAL_NAMES[k] for k in POPULAR_NUTS_SEEDS_CATEGORIES['nuts'] if k in CANONICAL_NAMES]
        return res[:limit]

    if query in {'seed', 'seeds', 'super seeds', 'superseeds'}:
        res = [CANONICAL_NAMES[k] for k in POPULAR_NUTS_SEEDS_CATEGORIES['seeds'] if k in CANONICAL_NAMES]
        return res[:limit]
        
    matches = []
    seen = set()
    
    def add_match(canon_key):
        if canon_key not in seen and canon_key in CANONICAL_NAMES:
            c_name = CANONICAL_NAMES[canon_key]
            matches.append(c_name)
            seen.add(canon_key)
            return len(matches) >= limit
        return False
        
    # 2. Exact alias match
    if query in FOOD_ALIASES:
        if add_match(FOOD_ALIASES[query]):
            return matches

    # 3. Pure nuts & seeds priority boost if query matches a nut/seed
    for k in NUTS_SEEDS_DETAILS.keys():
        if k in CANONICAL_NAMES and (k.startswith(query) or re.search(r'\b' + re.escape(query) + r'\b', k)):
            if add_match(k):
                return matches

    # 4. Prefix match on canonical names
    for key in FOOD_DATA.keys():
        if key.startswith(query):
            if add_match(key):
                return matches

    # 5. Prefix match on aliases
    for alias, canon_key in FOOD_ALIASES.items():
        if alias.startswith(query):
            if add_match(canon_key):
                return matches

    # 6. Substring match on canonical names
    for key in FOOD_DATA.keys():
        if query in key:
            if add_match(key):
                return matches

    # 7. Substring match on aliases
    for alias, canon_key in FOOD_ALIASES.items():
        if query in alias:
            if add_match(canon_key):
                return matches

    # 8. Token matching (e.g. 'aloo paratha')
    q_tokens = [w for w in query.split() if w not in STOP_WORDS]
    if q_tokens:
        for alias, canon_key in FOOD_ALIASES.items():
            if all(qt in alias for qt in q_tokens):
                if add_match(canon_key):
                    return matches

    return matches

def add_custom_food(name, calories, protein, carbs, fats, vit_c=0.0, calcium=0.0, iron=0.0, serving_unit=""):
    """
    Adds a new food item to FOOD_DATA in-memory and appends it to the CSV file permanently.
    """
    raw_name = name.strip()
    food_key = raw_name.lower()
    data = {
        "calories": float(calories),
        "protein": float(protein),
        "carbs": float(carbs),
        "fats": float(fats),
        "vit_c": float(vit_c),
        "calcium": float(calcium),
        "iron": float(iron),
        "serving_unit": str(serving_unit).strip()
    }
    FOOD_DATA[food_key] = data
    CANONICAL_NAMES[food_key] = raw_name
    for alias in get_aliases_for_name(raw_name):
        FOOD_ALIASES[alias] = food_key
        
    try:
        with open(csv_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([raw_name.title(), calories, protein, carbs, fats, vit_c, calcium, iron, serving_unit])
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
        if key in CANONICAL_NAMES:
            del CANONICAL_NAMES[key]
        aliases_to_del = [a for a, c in FOOD_ALIASES.items() if c == key]
        for a in aliases_to_del:
            del FOOD_ALIASES[a]
            
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
    for key, data in sorted(FOOD_DATA.items(), key=lambda x: CANONICAL_NAMES.get(x[0], x[0]).lower()):
        c_name = CANONICAL_NAMES.get(key, key.title())
        items.append({
            "name": c_name,
            "calories": data["calories"],
            "protein": data["protein"],
            "carbs": data["carbs"],
            "fats": data["fats"],
            "vit_c": data["vit_c"],
            "calcium": data["calcium"],
            "iron": data["iron"],
            "serving_unit": data.get("serving_unit", "")
        })
    return items

UNCOOKED_SINGLE_ITEMS = [
    'egg', 'apple', 'banana', 'orange', 'mango', 'papaya', 'guava',
    'watermelon', 'grapes', 'grape', 'pineapple', 'strawberry', 'berries', 'berry',
    'pomegranate', 'kiwi', 'pear', 'peach', 'plum', 'fig', 'chikoo',
    'sapota', 'custard apple', 'sweet lime', 'mosambi', 'lemon', 'lime', 'avocado',
    'cucumber', 'tomato', 'carrot', 'radish'
]

COUNT_SERVING_UNITS = [
    'piece', 'slice', 'biscuit', 'cookie', 'ladoo', 'laddu', 'cutlet',
    'samosa', 'burger', 'roll', 'bun', 'egg', 'apple', 'banana', 'orange', 'pear'
]

COOKED_COMPOSITE_WORDS = [
    'curry', 'sabji', 'sabzi', 'masala', 'bhurji', 'fry', 'halwa', 'kheer',
    'vadi', 'rice', 'dal', 'daal', 'biryani', 'pitha',
    'sandwich', 'salad', 'shake', 'juice', 'jam', 'tikka', 'pulao'
]

def is_count_based_food(name):
    """
    Checks if a food is an uncooked single-ingredient item (e.g., egg, apple)
    or piece-based item that should be measured in whole numbers rather than grams.
    """
    if not name:
        return False
    lower = name.lower().strip()
    
    # Check if serving unit in FOOD_DATA is count-based
    food_entry = FOOD_DATA.get(lower) or (FOOD_DATA.get(FOOD_ALIASES.get(lower)) if lower in FOOD_ALIASES else None)
    if food_entry and food_entry.get('serving_unit'):
        unit_lower = food_entry['serving_unit'].lower()
        if any(cu in unit_lower for cu in COUNT_SERVING_UNITS):
            return True
            
    if any(cw in lower for cw in COOKED_COMPOSITE_WORDS):
        return False
    for item in UNCOOKED_SINGLE_ITEMS:
        if item == lower or lower.startswith(item + ' ') or lower.endswith(' ' + item) or f' {item} ' in lower or f'({item}' in lower or f'{item})' in lower:
            return True
        if lower == item + 's' or lower == item + 'es':
            return True
    return False
