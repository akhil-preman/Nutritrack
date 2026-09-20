import sys
import math
from PIL import Image, ImageDraw, ImageFont

img_w, img_h = 1600, 1050
img = Image.new('RGB', (img_w, img_h), (255, 255, 255))
draw = ImageDraw.Draw(img)

try:
    title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
    box_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
    sub_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    label_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 17)
    label_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 17)
except:
    box_font = ImageFont.load_default()
    sub_font = box_font
    label_font = box_font
    label_bold = box_font

# Helper to draw rounded rectangle
def draw_box(x, y, w, h, text, is_center=False, process_num=""):
    bg_color = (255, 255, 255)
    border_color = (15, 23, 42)
    
    if is_center:
        draw.rounded_rectangle([x, y, x+w, y+h], radius=25, fill=bg_color, outline=border_color, width=3)
        # draw process num and text
        cy = y + h * 0.25
        draw.text((x + w/2, cy), process_num, font=title_font, fill=(15, 23, 42), anchor="mm")
        
        lines = text.split('\n')
        line_y = y + h * 0.5
        for l in lines:
            draw.text((x + w/2, line_y), l, font=box_font, fill=(15, 23, 42), anchor="mm")
            line_y += 32
    else:
        draw.rectangle([x, y, x+w, y+h], fill=bg_color, outline=border_color, width=3)
        draw.text((x + w/2, y + h/2), text, font=box_font, fill=(15, 23, 42), anchor="mm")

# Helper to draw directed arrow
def draw_arrow(start, end, text_lines, align="center", text_pos=(0,0)):
    sx, sy = start
    ex, ey = end
    
    # Draw line
    draw.line([sx, sy, ex, ey], fill=(15, 23, 42), width=2)
    
    # Calculate angle for arrowhead
    angle = math.atan2(ey - sy, ex - sx)
    arrow_len = 12
    arrow_angle = math.pi / 6
    
    x1 = ex - arrow_len * math.cos(angle - arrow_angle)
    y1 = ey - arrow_len * math.sin(angle - arrow_angle)
    x2 = ex - arrow_len * math.cos(angle + arrow_angle)
    y2 = ey - arrow_len * math.sin(angle + arrow_angle)
    
    draw.polygon([(ex, ey), (x1, y1), (x2, y2)], fill=(15, 23, 42))
    
    # Draw label
    tx, ty = text_pos
    line_h = 22
    start_ty = ty - (len(text_lines) * line_h) / 2 + line_h / 2
    for l_idx, line in enumerate(text_lines):
        ly = start_ty + l_idx * line_h
        if align == "right":
            draw.text((tx, ly), line, font=label_font, fill=(15, 23, 42), anchor="rm")
        elif align == "left":
            draw.text((tx, ly), line, font=label_font, fill=(15, 23, 42), anchor="lm")
        else:
            draw.text((tx, ly), line, font=label_font, fill=(15, 23, 42), anchor="mm")

# Draw Entities
# Central System Box
c_w, c_h = 520, 240
c_x, c_y = (img_w - c_w) / 2, (img_h - c_h) / 2
draw_box(c_x, c_y, c_w, c_h, "AI-Powered Nutrition &\nMeal Tracking System\n(NutriTrack AI)", is_center=True, process_num="0")

# Top Entity: User
t_w, t_h = 320, 85
t_x, t_y = (img_w - t_w) / 2, 60
draw_box(t_x, t_y, t_w, t_h, "User")

# Bottom Entity: Admin
b_w, b_h = 320, 85
b_x, b_y = (img_w - b_w) / 2, img_h - 145
draw_box(b_x, b_y, b_w, b_h, "Admin")

# Left Entity: AI Engine
l_w, l_h = 260, 85
l_x, l_y = 60, (img_h - l_h) / 2
draw_box(l_x, l_y, l_w, l_h, "AI Recognition &\nAnalysis Engine")

# Right Entity: Database
r_w, r_h = 260, 85
r_x, r_h_y = img_w - 320, (img_h - r_h) / 2
draw_box(r_x, r_h_y, r_w, r_h, "Database\n(SQLite)")

# --- ARROWS & LABELS ---

# 1. TOP: User <-> Central System
# User -> System (Down arrow)
draw_arrow((c_x + 160, t_y + t_h), (c_x + 160, c_y), 
           ["User Profile & Meal Input", "(Biometrics, Food Search, Image Upload)"], 
           align="right", text_pos=(c_x + 140, (t_y + t_h + c_y) / 2))

# System -> User (Up arrow)
draw_arrow((c_x + c_w - 160, c_y), (c_x + c_w - 160, t_y + t_h), 
           ["Daily Progress & Weekly Analysis Reports", "(Nutrient Charts & AI Diet Suggestions)"], 
           align="left", text_pos=(c_x + c_w - 140, (t_y + t_h + c_y) / 2))

# 2. BOTTOM: Admin <-> Central System
# Admin -> System (Up arrow)
draw_arrow((c_x + 160, b_y), (c_x + 160, c_y + c_h), 
           ["Manage Food Dataset & Micronutrient Profiles", "(System Config & Model Updates)"], 
           align="right", text_pos=(c_x + 140, (b_y + c_y + c_h) / 2))

# System -> Admin (Down arrow)
draw_arrow((c_x + c_w - 160, c_y + c_h), (c_x + c_w - 160, b_y), 
           ["System Analytics & Dataset Usage Reports", "(Model Performance & User Reports)"], 
           align="left", text_pos=(c_x + c_w - 140, (b_y + c_y + c_h) / 2))

# 3. LEFT: AI Engine <-> Central System
# System -> AI Engine (Left arrow)
draw_arrow((c_x, c_y + 70), (l_x + l_w, c_y + 70), 
           ["Food Photos & 7-Day Nutrient Totals", "(Image Data & Micronutrient Data)"], 
           align="center", text_pos=((c_x + l_x + l_w) / 2, c_y + 35))

# AI Engine -> System (Right arrow)
draw_arrow((l_x + l_w, c_y + c_h - 70), (c_x, c_y + c_h - 70), 
           ["Identified Food Items & Calculated Macros", "(Deficiency Predictions & Recommendations)"], 
           align="center", text_pos=((c_x + l_x + l_w) / 2, c_y + c_h - 35))

# 4. RIGHT: Central System <-> Database
# System -> Database (Right arrow)
draw_arrow((c_x + c_w, c_y + 70), (r_x, c_y + 70), 
           ["Store User Credentials, Biometrics,", "Meal Logs & Micronutrient Records"], 
           align="center", text_pos=((c_x + c_w + r_x) / 2, c_y + 35))

# Database -> System (Left arrow)
draw_arrow((r_x, c_y + c_h - 70), (c_x + c_w, c_y + c_h - 70), 
           ["Retrieve User Profile, Historical Meals,", "7-Day Intake Totals & Dataset Records"], 
           align="center", text_pos=((c_x + c_w + r_x) / 2, c_y + c_h - 35))

img.save('/Users/akhilpreman/Documents/Nutritrack/DFD_Level_0_Diagram.png')
print("DFD_Level_0_Diagram.png generated successfully.")
