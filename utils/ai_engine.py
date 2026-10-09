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
