import sys
import math
from PIL import Image, ImageDraw, ImageFont

img_w, img_h = 1600, 1050
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
draw.text((img_w / 2, 40), "NutriTrack AI - Level 2 Data Flow Diagram (Process 2.0: Food Logging & AI Recognition)", font=title_font, fill=(15, 23, 42), anchor="mm")

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

# Entities
draw_entity(60, 480, 200, 80, "User")

# Sub-Processes of 2.0 (Sequential Pipeline Flow)
draw_process(360, 180, 320, 140, "2.1", "Image Preprocessing\n(OpenCV Pipeline)")
draw_process(820, 180, 320, 140, "2.2", "AI Food Classification\n(MobileNetV2 Model)")
draw_process(820, 580, 320, 140, "2.3", "Nutrient Profile\nLookup Engine")
draw_process(360, 580, 320, 140, "2.4", "Meal Log Serialization\n& DB Commit")

# Datastores
draw_datastore(1220, 615, 340, 70, "D3", "Indian Food Dataset (food_db.py)")
draw_datastore(350, 880, 340, 70, "D2", "Meal Table (SQLite)")

# --- ARROWS ---

# User -> 2.1 (Upload Photo)
draw_arrow((160, 480), (360, 250), "Upload Meal Photo File", align="right", text_pos=(230, 340))

# User -> 2.3 (Direct Text Search)
draw_arrow((260, 520), (820, 620), "Manual Text Search Query (e.g. 'Biryani')", align="center", text_pos=(540, 540))

# 2.1 -> 2.2 (Tensor)
draw_arrow((680, 250), (820, 250), "Resized & Normalized Image Tensor\n(224x224 RGB)", align="center", text_pos=(750, 215))

# 2.2 -> 2.3 (Predicted Class)
draw_arrow((980, 320), (980, 580), "Predicted Food Label\n(e.g., 'Palak Paneer')", align="left", text_pos=(995, 450))

# 2.3 <-> D3 (Dataset Lookup)
draw_arrow((1140, 650), (1220, 650), "Fetch Macro & Micronutrients", align="center", text_pos=(1180, 625))

# 2.3 -> 2.4 (Full Nutrient Data)
draw_arrow((820, 650), (680, 650), "Full Nutritional Profile\n(Cal, Protein, Vit C, Iron, Calcium)", align="center", text_pos=(750, 620))

# 2.4 -> D2 (Write Log)
draw_arrow((520, 720), (520, 880), "Write Record to Meal Table", align="left", text_pos=(535, 800))

# 2.4 -> User (Success Notification)
draw_arrow((360, 620), (220, 560), "Logged Meal Confirmation\n& Updated Daily Totals", align="right", text_pos=(260, 620))

img.save('/Users/akhilpreman/Documents/Nutritrack/DFD_Level_2_Diagram.png')
print("DFD_Level_2_Diagram.png generated successfully.")
