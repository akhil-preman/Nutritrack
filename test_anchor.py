from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (400, 100), (255, 255, 255))
draw = ImageDraw.Draw(img)
font1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
font2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)

draw.rectangle([10, 10, 390, 90], fill=(226, 232, 240), outline=(15, 23, 42), width=2)
# Draw line 1 at y=32, line 2 at y=68 using anchor="mm"
draw.text((200, 34), "PRIORITY", font=font1, fill=(15, 23, 42), anchor="mm")
draw.text((200, 66), "<high/medium/low>", font=font2, fill=(71, 85, 105), anchor="mm")

img.save("test_anchor.png")
print("Saved test_anchor.png")
