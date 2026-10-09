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
        
        # We use gemini-3.8-flash as it is extremely fast and has a generous free tier for vision tasks
        model = genai.GenerativeModel('gemini-3.8-flash')
        
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

def generate_weekly_deficiencies(consumed, requirements, days_logged):
    """
    Uses Gemini to analyze the user's weekly nutrition and return a JSON list of deficiencies.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[AI ENGINE] ERROR: GEMINI_API_KEY is missing!")
        return []
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = f"""
        You are an expert AI nutritionist. The user has logged food for {days_logged} days this week.
        Here is what they consumed total over those days vs their requirements:
        Calories: {consumed['calories']} (Target: {requirements['calories']})
        Protein: {consumed['protein']}g (Target: {requirements['protein']}g)
        Carbs: {consumed['carbs']}g (Target: {requirements['carbs']}g)
        Fats: {consumed['fats']}g (Target: {requirements['fats']}g)
        Vitamin C: {consumed['vit_c']}mg (Target: {requirements['vit_c']}mg)
        Calcium: {consumed['calcium']}mg (Target: {requirements['calcium']}mg)
        Iron: {consumed['iron']}mg (Target: {requirements['iron']}mg)
        
        Analyze this data. If they are significantly under any target (less than 75%), generate a deficiency alert.
        Return ONLY a JSON array of objects. Do NOT use markdown code blocks. 
        Each object must have these exact keys:
        - "name": The nutrient name (e.g. "Protein", "Iron")
        - "message": A 1-sentence explanation of why they need it.
        - "foods": A list of 2-3 specific Indian foods that are high in this nutrient.
        
        Example:
        [
            {{"name": "Iron", "message": "Your Iron intake is low, which can cause fatigue.", "foods": ["Spinach", "Lentils"]}}
        ]
        
        If they hit all their targets, return an empty array: []
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        try:
            return json.loads(raw_text)
        except Exception as json_e:
            print(f"[AI ENGINE] JSON Parse Error: {json_e} - Raw text: {raw_text}")
            return []
            
    except Exception as e:
        print(f"[AI ENGINE] Error during Gemini Insights call: {e}")
        return []
