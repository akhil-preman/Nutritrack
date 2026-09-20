import sys
import math
from PIL import Image, ImageDraw, ImageFont

img_w, img_h = 1600, 1100
img = Image.new('RGB', (img_w, img_h), (255, 255, 255))
draw = ImageDraw.Draw(img)

try:
    title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
    box_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
    box_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    label_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
    ds_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
except:
    box_bold = ImageFont.load_default()
    box_font = box_bold
    label_font = box_bold
    ds_font = box_bold
    title_font = box_bold

# Main Title
draw.text((img_w / 2, 40), "NutriTrack AI - Level 1 Data Flow Diagram (DFD)", font=title_font, fill=(15, 23, 42), anchor="mm")

def draw_entity(x, y, w, h, text):
    draw.rectangle([x, y, x+w, y+h], fill=(241, 245, 249), outline=(15, 23, 42), width=3)
    draw.text((x+w/2, y+h/2), text, font=box_bold, fill=(15, 23, 42), anchor="mm")

def draw_process(x, y, w, h, p_num, p_title):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=20, fill=(255, 255, 255), outline=(15, 23, 42), width=3)
    draw.text((x+w/2, y+25), p_num, font=box_bold, fill=(37, 99, 235), anchor="mm")
    
    lines = p_title.split('\n')
    line_y = y + 55
    for line in lines:
        draw.text((x+w/2, line_y), line, font=box_font, fill=(15, 23, 42), anchor="mm")
        line_y += 24

def draw_datastore(x, y, w, h, ds_id, ds_name):
    # Open ended rectangle (left line open or classic open-right format)
    draw.line([x, y, x+w, y], fill=(15, 23, 42), width=2)
    draw.line([x, y+h, x+w, y+h], fill=(15, 23, 42), width=2)
    draw.line([x, y, x, y+h], fill=(15, 23, 42), width=2)
    draw.line([x+45, y, x+45, y+h], fill=(15, 23, 42), width=2)
    
    draw.text((x+22, y+h/2), ds_id, font=ds_font, fill=(15, 23, 42), anchor="mm")
    draw.text((x+45 + (w-45)/2, y+h/2), ds_name, font=box_font, fill=(15, 23, 42), anchor="mm")

def draw_arrow(start, end, text="", align="center", text_pos=None):
    sx, sy = start
    ex, ey = end
    
    draw.line([sx, sy, ex, ey], fill=(15, 23, 42), width=2)
    
    angle = math.atan2(ey - sy, ex - sx)
    arrow_len = 10
    arrow_angle = math.pi / 6
    
    x1 = ex - arrow_len * math.cos(angle - arrow_angle)
    y1 = ey - arrow_len * math.sin(angle - arrow_angle)
    x2 = ex - arrow_len * math.cos(angle + arrow_angle)
    y2 = ey - arrow_len * math.sin(angle + arrow_angle)
    
    draw.polygon([(ex, ey), (x1, y1), (x2, y2)], fill=(15, 23, 42))
    
    if text and text_pos:
        tx, ty = text_pos
        lines = text.split('\n')
        line_h = 18
        start_ty = ty - (len(lines)*line_h)/2 + line_h/2
        for l_idx, line in enumerate(lines):
            ly = start_ty + l_idx * line_h
            if align == "left":
                draw.text((tx, ly), line, font=label_font, fill=(15, 23, 42), anchor="lm")
            elif align == "right":
                draw.text((tx, ly), line, font=label_font, fill=(15, 23, 42), anchor="rm")
            else:
                draw.text((tx, ly), line, font=label_font, fill=(15, 23, 42), anchor="mm")

# --- LAYOUT PLACEMENT ---
# External Entities
draw_entity(60, 200, 200, 80, "User")
draw_entity(60, 850, 200, 80, "Admin")

# Processes (1.0 to 4.0 in middle grid)
draw_process(450, 150, 320, 140, "1.0", "Auth & Biometrics\nProcessing Engine")
draw_process(450, 380, 320, 140, "2.0", "Food Logging & AI\nPhoto Recognition")
draw_process(450, 610, 320, 140, "3.0", "Daily Tracking &\nDashboard Renderer")
draw_process(450, 840, 320, 140, "4.0", "Weekly Analysis &\nDeficiency Engine")

# Datastores (Right Side)
draw_datastore(1150, 180, 350, 70, "D1", "User Table (SQLite)")
draw_datastore(1150, 410, 350, 70, "D2", "Meal Table (SQLite)")
draw_datastore(1150, 640, 350, 70, "D3", "Indian Food Dataset (food_db.py)")

# --- DATA FLOW ARROWS ---

# User -> Process 1.0
draw_arrow((260, 220), (450, 220), "Registration & Credentials", text_pos=(355, 205))
# Process 1.0 -> User
draw_arrow((450, 260), (260, 260), "BMR, TDEE & BMI Targets", text_pos=(355, 280))

# User -> Process 2.0
draw_arrow((200, 280), (450, 420), "Food Search / Photo", text_pos=(310, 340))
# Process 2.0 -> User
draw_arrow((450, 470), (230, 390), "Logged Meal Summary", text_pos=(330, 450))

# User -> Process 3.0
draw_arrow((170, 280), (450, 650), "Date Picker Selection", text_pos=(270, 500))
# Process 3.0 -> User
draw_arrow((450, 700), (200, 280), "Daily Progress Bars & Macros", text_pos=(280, 620))

# User -> Process 4.0
draw_arrow((140, 280), (450, 890), "Request Weekly Report", text_pos=(240, 720))
# Process 4.0 -> User
draw_arrow((450, 930), (160, 280), "7-Day Deficiency Alerts & Suggestions", text_pos=(280, 850))

# Admin -> Process 2.0 / 4.0
draw_arrow((260, 890), (450, 500), "Dataset Updates & Food Profiles", text_pos=(330, 780))

# --- PROCESS TO DATASTORE ARROWS ---
# 1.0 <-> D1
draw_arrow((770, 215), (1150, 215), "Write User Profile & Hashed Passwords", text_pos=(960, 195))

# 2.0 <-> D3 (Read Food DB)
draw_arrow((770, 430), (1150, 655), "Lookup Nutrition Profiles", text_pos=(960, 540))
# 2.0 -> D2 (Write Meal)
draw_arrow((770, 450), (1150, 450), "Write Meal Record & Micronutrients", text_pos=(960, 430))

# 3.0 <- D1 & D2 (Read User & Meals)
draw_arrow((1150, 230), (770, 650), "Fetch User Targets", text_pos=(980, 340))
draw_arrow((1150, 460), (770, 680), "Fetch Daily Meals", text_pos=(960, 600))

# 4.0 <- D2 (Read 7-Day Meals)
draw_arrow((1150, 475), (770, 900), "Fetch 7-Day Meal Logs", text_pos=(960, 760))

img.save('/Users/akhilpreman/Documents/Nutritrack/DFD_Level_1_Diagram.png')
print("DFD_Level_1_Diagram.png generated successfully.")
