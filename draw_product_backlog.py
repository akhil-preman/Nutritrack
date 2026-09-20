import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

headers_row1 = ["ID", "NAME", "PRIORITY", "ESTIMATE", "STATUS"]
headers_row2 = ["", "", "<high/medium/low>", "(Hours)", "<Planned/In progress/Completed>"]

data = [
    ["1", "Requirement Analysis & Architecture", "High", "3", "COMPLETED"],
    ["2", "Database Schema Design & Setup", "High", "4", "COMPLETED"],
    ["3", "User Authentication & Security", "High", "4", "COMPLETED"],
    ["4", "Biometric Engine (BMI/BMR)", "High", "4", "COMPLETED"],
    ["5", "Indian Food Dataset & Vitamins", "High", "4", "COMPLETED"],
    ["6", "Daily Dashboard UI", "High", "4", "COMPLETED"],
    ["7", "Meal Logging Interface", "High", "4", "COMPLETED"],
    ["8", "Historical Date Tracking Engine", "Medium", "3", "COMPLETED"],
    ["9", "Weekly Analysis Engine", "High", "4", "COMPLETED"],
    ["10", "Nutritional Deficiency Logic", "High", "4", "COMPLETED"],
    ["11", "AI Diet Suggestions System", "High", "4", "COMPLETED"],
    ["12", "UI Polish & Dashboard Integration", "Medium", "3", "COMPLETED"],
    ["13", "MobileNetV2 + OpenCV Setup", "High", "4", "PENDING"],
    ["14", "Photo Upload API Integration", "High", "4", "PENDING"],
    ["15", "System Testing & Final Documentation", "High", "7", "PENDING"],
    ["", "Total", "", "60", "PENDING"]
]

col_widths = [100, 540, 260, 200, 360]
row_height = 55
header_height = 95
margin = 30
width = sum(col_widths) + margin * 2
height = (len(data)) * row_height + header_height + margin * 2

img = Image.new('RGB', (width, height), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

font_header1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
font_header2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
font_body = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)

x = margin
y = margin

for i in range(len(headers_row1)):
    w = col_widths[i]
    cx = x + w / 2
    
    draw.rectangle([x, y, x + w, y + header_height], fill=(226, 232, 240), outline=(15, 23, 42), width=3)
    
    t1 = headers_row1[i]
    t2 = headers_row2[i]
    
    if t2:
        draw.text((cx, y + header_height * 0.35), t1, font=font_header1, fill=(15, 23, 42), anchor="mm")
        draw.text((cx, y + header_height * 0.72), t2, font=font_header2, fill=(71, 85, 105), anchor="mm")
    else:
        draw.text((cx, y + header_height * 0.5), t1, font=font_header1, fill=(15, 23, 42), anchor="mm")
        
    x += w

y += header_height

for row_idx, row in enumerate(data):
    x = margin
    is_total = (row_idx == len(data) - 1)
    
    for i, cell_text in enumerate(row):
        w = col_widths[i]
        cx = x + w / 2
        cy = y + row_height / 2
        
        draw.rectangle([x, y, x + w, y + row_height], fill=(255, 255, 255), outline=(15, 23, 42), width=2)
        
        use_font = font_bold if (is_total or i == 0) else font_body
        
        if cell_text:
            if i == 1 and not is_total:
                draw.text((x + 20, cy), cell_text, font=use_font, fill=(0, 0, 0), anchor="lm")
            else:
                draw.text((cx, cy), cell_text, font=use_font, fill=(0, 0, 0), anchor="mm")
                
        x += w
    y += row_height

img.save('/Users/akhilpreman/Documents/Nutritrack/Product_Backlog.png')
print("Product_Backlog.png updated.")
