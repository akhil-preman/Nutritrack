import sys
from PIL import Image, ImageDraw, ImageFont

headers = ["Sprint & Backlog Task", "Status", "Est", "D 1-2", "D 3-4", "D 5-6", "D 7-8", "D 9-10"]
data = [
    ["SPRINT 1: Foundation (15 Hrs)", "", "", "", "", "", "", ""],
    ["  ↳ Req. Analysis & Architecture", "Done", "3", "3", "0", "0", "0", "0"],
    ["  ↳ Database Schema (SQLite)", "Done", "4", "0", "4", "0", "0", "0"],
    ["  ↳ User Auth (Register/Login)", "Done", "4", "0", "0", "4", "0", "0"],
    ["  ↳ Biometric Engine (BMI/BMR)", "Done", "4", "0", "0", "0", "4", "0"],
    ["SPRINT 2: Tracking Core (15 Hrs)", "", "", "", "", "", "", ""],
    ["  ↳ Indian Food DB & Vitamins", "Done", "4", "4", "0", "0", "0", "0"],
    ["  ↳ Daily Dashboard UI", "Done", "4", "0", "4", "0", "0", "0"],
    ["  ↳ Meal Logging Interface", "Done", "4", "0", "0", "4", "0", "0"],
    ["  ↳ Historical Date Engine", "Done", "3", "0", "0", "0", "3", "0"],
    ["SPRINT 3: Weekly Analytics (15 Hrs)", "", "", "", "", "", "", ""],
    ["  ↳ Weekly Analysis Engine", "Done", "4", "4", "0", "0", "0", "0"],
    ["  ↳ Deficiency Detection Logic", "Done", "4", "0", "4", "0", "0", "0"],
    ["  ↳ AI Diet Suggestions System", "Done", "4", "0", "0", "4", "0", "0"],
    ["  ↳ UI Polish & Integration", "Done", "3", "0", "0", "0", "3", "0"],
    ["SPRINT 4: Photo Recognition (15 Hrs)", "", "", "", "", "", "", ""],
    ["  ↳ OpenCV & TF Prep", "To Do", "4", "4", "0", "0", "0", "0"],
    ["  ↳ Photo Upload API", "To Do", "4", "0", "4", "0", "0", "0"],
    ["  ↳ AI Engine Integration", "To Do", "4", "0", "0", "4", "0", "0"],
    ["  ↳ System Testing & Docs", "To Do", "3", "0", "0", "0", "3", "0"],
    ["TOTAL PROJECT HOURS", "", "60", "", "", "", "", ""]
]

col_widths = [320, 80, 50, 70, 70, 70, 70, 70]
row_height = 36
margin = 20
width = sum(col_widths) + margin*2
height = (len(data) + 1) * row_height + margin*2

img = Image.new('RGB', (width, height), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    bold_font = ImageFont.truetype("/System/Library/Fonts/Helvetica-Bold.ttc", 16)
except:
    font = ImageFont.load_default()
    bold_font = font

def draw_cell(x, y, w, h, text, is_header=False, is_sprint=False, is_total=False, col_idx=0):
    fill_color = (255, 255, 255)
    text_color = (0, 0, 0)
    use_font = font
    if is_header:
        fill_color = (241, 245, 249)
        use_font = bold_font
    elif is_sprint:
        fill_color = (226, 232, 240)
        use_font = bold_font
    elif is_total:
        fill_color = (241, 245, 249)
        use_font = bold_font
    draw.rectangle([x, y, x+w, y+h], fill=fill_color, outline=(203, 213, 225))
    if text:
        bbox = draw.textbbox((0,0), text, font=use_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x + (w - tw)/2 if col_idx > 0 else x + 15
        ty = y + (h - th)/2 - 2
        draw.text((tx, ty), text, fill=text_color, font=use_font)

x = margin
y = margin
for i, h_text in enumerate(headers):
    draw_cell(x, y, col_widths[i], row_height, h_text, is_header=True, col_idx=i)
    x += col_widths[i]

y += row_height
for row in data:
    x = margin
    is_sprint = row[0].startswith("SPRINT")
    is_total = row[0].startswith("TOTAL")
    for i, cell_text in enumerate(row):
        draw_cell(x, y, col_widths[i], row_height, cell_text, is_sprint=is_sprint, is_total=is_total, col_idx=i)
        x += col_widths[i]
    y += row_height

img.save('/Users/akhilpreman/Documents/Nutritrack/Sprint_Backlog.png')
print("Image generated successfully.")
