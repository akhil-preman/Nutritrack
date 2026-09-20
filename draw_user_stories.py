import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

headers = ["User Story ID", "As a type of User", "I want to...", "So that I can..."]

data = [
    ["1", "New User", "Register with my age, weight, and height", "Get personalized BMR and TDEE caloric goals."],
    ["2", "User", "Log securely into my account", "Keep my personal health and biometric data private."],
    ["3", "User", "View a daily dashboard with progress bars", "Track my daily calorie and macro intake against my goals."],
    ["4", "User", "Search and log meals from an Indian food database", "Record what I eat without manually entering nutritional values."],
    ["5", "User", "Upload a photo of my meal to the system", "Let the AI automatically identify the food and its macros."],
    ["6", "User", "Select past dates on an interactive calendar", "Review my historical meal logs and past nutritional intake."],
    ["7", "User", "View a comprehensive 7-day weekly analysis report", "Understand my long-term nutritional trends and patterns."],
    ["8", "User", "Have the system silently track my daily vitamins", "Ensure I am getting essential micronutrients (Iron, Calcium, Vit C)."],
    ["9", "User", "Receive automated AI nutritional deficiency alerts", "Be aware if I am consistently lacking in specific nutrients."],
    ["10", "User", "Get personalized Indian food recommendations", "Know exactly what local foods to eat to fix my deficiencies."]
]

col_widths = [180, 260, 520, 520]
margin = 30

font_header = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
font_body = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)

row_heights = [80] # Header height
for row in data:
    max_h = 75
    for i, text in enumerate(row):
        chars_per_line = int(col_widths[i] / 13)
        lines = textwrap.wrap(text, width=max(1, chars_per_line))
        h = max(len(lines) * 32 + 30, 75)
        if h > max_h:
            max_h = h
    row_heights.append(max_h)

width = sum(col_widths) + margin * 2
height = sum(row_heights) + margin * 2

img = Image.new('RGB', (width, height), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

x = margin
y = margin

for i, h_text in enumerate(headers):
    w = col_widths[i]
    cx = x + w / 2
    cy = y + row_heights[0] / 2
    draw.rectangle([x, y, x + w, y + row_heights[0]], fill=(226, 232, 240), outline=(15, 23, 42), width=3)
    draw.text((cx, cy), h_text, font=font_header, fill=(15, 23, 42), anchor="mm")
    x += w

y += row_heights[0]

for row_idx, row in enumerate(data):
    x = margin
    rh = row_heights[row_idx + 1]
    
    for i, cell_text in enumerate(row):
        w = col_widths[i]
        cx = x + w / 2
        cy = y + rh / 2
        
        draw.rectangle([x, y, x + w, y + rh], fill=(255, 255, 255), outline=(15, 23, 42), width=2)
        
        chars_per_line = int(w / 13)
        lines = textwrap.wrap(cell_text, width=max(1, chars_per_line))
        
        line_height = 30
        total_th = len(lines) * line_height
        start_y = y + (rh - total_th) / 2 + line_height / 2
        
        for l_idx, line in enumerate(lines):
            ly = start_y + l_idx * line_height
            use_font = font_bold if i == 0 else font_body
            
            if i < 2:
                draw.text((cx, ly), line, font=use_font, fill=(0, 0, 0), anchor="mm")
            else:
                draw.text((x + 20, ly), line, font=use_font, fill=(0, 0, 0), anchor="lm")
                
        x += w
    y += rh

img.save('/Users/akhilpreman/Documents/Nutritrack/User_Stories.png')
print("User_Stories.png updated.")
