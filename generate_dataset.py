import csv

# Format: Name, Calories, Protein(g), Carbs(g), Fats(g), Vit C(mg), Calcium(mg), Iron(mg)
foods = [
    # --- RAW INGREDIENTS & STAPLES ---
    ["White Rice (boiled)", 130, 2.7, 28, 0.3, 0, 10, 0.2],
    ["Brown Rice (boiled)", 111, 2.6, 23, 0.9, 0, 10, 0.4],
    ["Wheat Roti / Chapati", 104, 3.0, 22, 0.4, 0, 10, 1.5],
    ["Naan (Plain)", 260, 8.0, 45, 5.0, 0, 30, 2.0],
    ["Toor Dal (raw)", 343, 22.0, 63, 1.5, 0, 130, 2.7],
    ["Moong Dal (raw)", 348, 24.5, 60, 1.2, 0, 132, 6.7],
    ["Masoor Dal (raw)", 352, 24.6, 60, 1.0, 4, 35, 6.5],
    ["Chana Dal (raw)", 378, 20.0, 63, 6.0, 0, 50, 5.0],
    ["Paneer (raw)", 296, 14.0, 3.0, 25.0, 0, 480, 0.1],
    ["Cow Milk", 42, 3.4, 5.0, 1.0, 0, 125, 0.0],
    ["Yogurt / Curd", 61, 3.5, 4.7, 3.3, 0.5, 121, 0.1],
    ["Chicken Breast (raw)", 165, 31.0, 0.0, 3.6, 0, 15, 1.0],
    ["Egg (whole)", 155, 13.0, 1.1, 11.0, 0, 50, 1.2],
    ["Onion (raw)", 40, 1.1, 9.3, 0.1, 7.4, 23, 0.2],
    ["Tomato (raw)", 18, 0.9, 3.9, 0.2, 14, 10, 0.3],
    ["Potato (raw)", 77, 2.0, 17, 0.1, 19.7, 12, 0.8],
    ["Spinach / Palak (raw)", 23, 2.9, 3.6, 0.4, 28.1, 99, 2.7],
    ["Cauliflower (raw)", 25, 1.9, 5.0, 0.3, 48.2, 22, 0.4],
    
    # --- POPULAR INDIAN DISHES ---
    ["Dal Tadka", 210, 11.0, 29, 6.0, 2.0, 40, 3.0],
    ["Dal Makhani", 330, 14.0, 35, 16.0, 1.5, 80, 4.5],
    ["Paneer Butter Masala", 350, 12.0, 15, 28.0, 5.0, 250, 1.0],
    ["Palak Paneer", 280, 14.0, 11, 20.0, 15.0, 300, 4.5],
    ["Matar Paneer", 320, 13.0, 18, 22.0, 10.0, 200, 2.5],
    ["Kadai Paneer", 290, 12.0, 14, 21.0, 12.0, 210, 2.0],
    ["Chicken Tikka Masala", 380, 28.0, 12, 24.0, 8.0, 45, 2.5],
    ["Butter Chicken", 400, 25.0, 15, 28.0, 6.0, 50, 2.0],
    ["Chicken Curry", 250, 25.0, 5.0, 14.0, 2.0, 15, 1.2],
    ["Mutton Curry", 320, 22.0, 4.0, 24.0, 1.0, 20, 2.8],
    ["Fish Curry", 210, 18.0, 6.0, 12.0, 3.0, 25, 1.5],
    ["Chicken Biryani", 450, 18.0, 60, 15.0, 4.0, 30, 2.5],
    ["Mutton Biryani", 510, 20.0, 55, 22.0, 2.0, 35, 3.2],
    ["Veg Biryani", 320, 8.0, 50, 10.0, 6.0, 40, 2.0],
    ["Aloo Gobi", 180, 4.0, 22, 9.0, 35.0, 30, 1.5],
    ["Aloo Jeera", 160, 3.0, 20, 8.0, 12.0, 15, 1.2],
    ["Bhindi Masala", 140, 3.5, 15, 8.0, 20.0, 60, 1.8],
    ["Baingan Bharta", 120, 2.5, 14, 7.0, 15.0, 20, 1.0],
    ["Chana Masala", 260, 12.0, 35, 8.0, 8.0, 60, 4.0],
    ["Rajma Chawal", 340, 14.0, 55, 6.0, 4.0, 50, 4.2],
    ["Masala Dosa", 250, 5.0, 42, 7.0, 2.0, 15, 1.0],
    ["Plain Dosa", 133, 3.9, 29, 0.2, 1.0, 10, 0.5],
    ["Idli (2 pieces)", 110, 4.0, 24, 0.4, 0.5, 10, 0.8],
    ["Sambar", 150, 6.0, 20, 5.0, 8.0, 40, 2.0],
    ["Upma", 220, 5.0, 30, 9.0, 5.0, 20, 1.5],
    ["Poha", 180, 3.5, 35, 3.0, 6.0, 15, 2.0],
    ["Pav Bhaji", 400, 10.0, 55, 16.0, 25.0, 80, 3.5],
    ["Vada Pav", 300, 6.0, 40, 12.0, 4.0, 20, 1.5],
    ["Pani Puri (6 pieces)", 180, 4.0, 32, 4.0, 10.0, 15, 2.0],
    ["Bhel Puri", 220, 5.0, 45, 2.0, 12.0, 20, 1.5],
    ["Samosa (1 piece)", 260, 3.5, 24, 17.0, 4.0, 15, 1.2],
    ["Gulab Jamun (2 pieces)", 300, 3.0, 45, 12.0, 0, 40, 0.5],
    ["Rasgulla (2 pieces)", 250, 4.0, 45, 6.0, 0, 50, 0.2],
    ["Jalebi", 300, 1.5, 55, 8.0, 0, 10, 0.5],
    ["Lassi (Sweet)", 210, 8.0, 28, 7.0, 2.0, 250, 0.2],
    ["Masala Chai", 120, 3.0, 15, 5.0, 0, 100, 0.1],
    
    # --- FRUITS & SNACKS ---
    ["Apple", 52, 0.3, 14, 0.2, 4.6, 6, 0.1],
    ["Banana", 89, 1.1, 23, 0.3, 8.7, 5, 0.3],
    ["Orange", 60, 1.2, 15, 0.2, 70.0, 40, 0.1],
    ["Mango", 60, 0.8, 15, 0.4, 36.4, 11, 0.2],
    ["Papaya", 43, 0.5, 11, 0.3, 60.9, 20, 0.3],
    ["Guava", 68, 2.6, 14, 1.0, 228.3, 18, 0.3],
    ["Almonds (100g)", 579, 21.0, 22, 50.0, 0, 269, 3.7],
    ["Walnuts (100g)", 654, 15.0, 14, 65.0, 1.2, 98, 2.9],
    ["Peanuts (100g)", 567, 26.0, 16, 49.0, 0, 92, 4.6]
]

with open('dataset/indian_food_nutrition.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["food_name", "calories", "protein", "carbs", "fats", "vit_c", "calcium", "iron"])
    for row in foods:
        writer.writerow(row)

print("Dataset generated successfully at dataset/indian_food_nutrition.csv")
