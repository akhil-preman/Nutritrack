import os
import google.generativeai as genai
from PIL import Image

def predict_food_from_image(filepath):
    """
    Uses Google's Gemini 1.5 Flash model (Free Tier) to recognize the food in the image.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[AI ENGINE] ERROR: GEMINI_API_KEY is missing from .env file!")
        return "error_missing_api_key"
        
    try:
        img = Image.open(filepath)
    except Exception as e:
        print(f"Error loading image: {e}")
        return "error_invalid_image"

    try:
        genai.configure(api_key=api_key)
        
        # We use gemini-3.5-flash-lite for lightning-fast recognition
        model = genai.GenerativeModel('gemini-3.5-flash-lite')
        
        prompt = "Identify the main food item in this image. Reply with ONLY the name of the food, as concisely as possible (e.g. 'apple', 'chicken biryani', 'chapati'). Do not include any other words, punctuation, or explanations."
        
        response = model.generate_content([prompt, img])
        
        predicted_food = response.text.strip().lower()
        
        # Clean up the string just in case
        predicted_food = predicted_food.replace('.', '').replace('\n', '')
        
        print(f"[AI ENGINE] Gemini Predicted: {predicted_food}")
        return predicted_food
        
    except Exception as e:
        print(f"[AI ENGINE] Error during Gemini API call: {e}")
        return "error_api_failed"

import json
from utils.food_db import suggest_foods

def generate_weekly_deficiencies(consumed, requirements, days_logged):
    """
    Uses Gemini 3.5-flash-lite to analyze the user's weekly nutrition and return a JSON list of deficiencies.
    Includes a guaranteed clinical fallback so recommendations ALWAYS work reliably.
    """
    # Quick check: if everything is >= 75% met, no deficits exist
    has_deficiency = False
    for k in ['calories', 'protein', 'carbs', 'fats', 'vit_c', 'calcium', 'iron']:
        req_val = requirements.get(k, 0)
        con_val = consumed.get(k, 0)
        if req_val > 0 and con_val < req_val * 0.75:
            has_deficiency = True
            break
            
    if not has_deficiency:
        return []

    # Try Gemini 3.5-flash-lite for fast personalized clinical insights
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.5-flash-lite')
            
            prompt = f"""
            You are a formal clinical nutritionist for NutriTrack AI. Analyze the user's {days_logged}-day trailing nutrition intake vs clinical targets:
            - Calories: {round(consumed.get('calories', 0), 1)} kcal (Target: {round(requirements.get('calories', 0), 1)} kcal)
            - Protein: {round(consumed.get('protein', 0), 1)}g (Target: {round(requirements.get('protein', 0), 1)}g)
            - Carbohydrates: {round(consumed.get('carbs', 0), 1)}g (Target: {round(requirements.get('carbs', 0), 1)}g)
            - Healthy Fats: {round(consumed.get('fats', 0), 1)}g (Target: {round(requirements.get('fats', 0), 1)}g)
            - Vitamin C: {round(consumed.get('vit_c', 0), 1)}mg (Target: {round(requirements.get('vit_c', 0), 1)}mg)
            - Calcium: {round(consumed.get('calcium', 0), 1)}mg (Target: {round(requirements.get('calcium', 0), 1)}mg)
            - Iron: {round(consumed.get('iron', 0), 1)}mg (Target: {round(requirements.get('iron', 0), 1)}mg)
            
            Identify all nutrients that are significantly under target (< 75% met).
            Return ONLY a valid JSON array of objects. Do NOT use markdown code blocks (no ```json).
            Each object must have these exact keys:
            - "name": Nutrient name (e.g. "Protein", "Vitamin C", "Calcium", "Iron", "Calories", "Carbohydrates", "Healthy Fats")
            - "severity": "critical" if under 40% met, else "moderate"
            - "pct_met": Integer percentage met (e.g. 24)
            - "consumed": string with unit (e.g. "24.5g", "0mg")
            - "target": string with unit (e.g. "80.0g", "65mg")
            - "message": Concise, formal 1-sentence explanation of why this deficit matters.
            - "foods": Array of 3-4 specific healthy Indian foods high in this nutrient.
            """
            
            response = model.generate_content(prompt, request_options={"timeout": 10})
            raw_text = response.text.strip().replace('```json', '').replace('```', '').strip()
            parsed = json.loads(raw_text)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except Exception as e:
            print(f"[AI ENGINE] Gemini call failed: {e}. Falling back to clinical rules.")

    # Guaranteed clinical fallback
    fallback_items = []
    nutrients_meta = [
        ("Calories", "calories", "kcal", "Calorie deficit below basal requirements triggers fatigue and metabolic slowdown.", ["Khichdi with Ghee", "Aloo Paratha", "Banana Shake", "Oats with Nuts"]),
        ("Protein", "protein", "g", "Sub-optimal protein intake impairs lean muscle recovery, enzymatic health, and immune defense.", ["Paneer Bhurji", "Moong Dal", "Soya Chunks", "Boiled Eggs"]),
        ("Carbohydrates", "carbs", "g", "Inadequate carbohydrate stores deplete essential glycogen needed for physical and mental stamina.", ["Steamed Brown Rice", "Roti / Chapati", "Sweet Potato", "Poha"]),
        ("Healthy Fats", "fats", "g", "Low fat intake compromises absorption of vital fat-soluble vitamins (A, D, E, K).", ["Almonds & Walnuts", "Cow Ghee", "Cold-Pressed Mustard Oil", "Chia Seeds"]),
        ("Vitamin C", "vit_c", "mg", "Insufficient Vitamin C weakens immune defenses and diminishes cellular antioxidant protection.", ["Amla (Indian Gooseberry)", "Fresh Orange / Mosambi", "Guava", "Lemon Water"]),
        ("Calcium", "calcium", "mg", "Deficient calcium intake compromises bone mineral density and optimal neuromuscular function.", ["Ragi (Finger Millet)", "Curd / Dahi", "Milk / Paneer", "Sesame Seeds (Til)"]),
        ("Iron", "iron", "mg", "Iron deficiency reduces hemoglobin synthesis, triggering lethargy and impaired oxygen transport.", ["Palak (Spinach) Paneer", "Dal Tadka", "Rajma", "Jaggery (Gur)"])
    ]
    
    for name, key, unit, msg, default_foods in nutrients_meta:
        req_val = requirements.get(key, 0)
        con_val = consumed.get(key, 0)
        if req_val > 0 and con_val < req_val * 0.75:
            pct = int(round((con_val / req_val) * 100))
            severity = "critical" if pct < 40 else "moderate"
            db_foods = suggest_foods(key, 4) if key in ['protein', 'vit_c', 'calcium', 'iron'] else []
            chosen_foods = db_foods if (db_foods and len(db_foods) >= 2) else default_foods
            fallback_items.append({
                "name": name,
                "severity": severity,
                "pct_met": pct,
                "consumed": f"{round(con_val, 1)} {unit}",
                "target": f"{round(req_val, 1)} {unit}",
                "message": msg,
                "foods": chosen_foods
            })
            
    return fallback_items
