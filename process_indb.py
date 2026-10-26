"""
Processor script to merge the Indian Nutrient Databank (INDB) from ICMR-NIN
into NutriTrack's master database (dataset/indian_food_nutrition.csv).
"""

import os
import csv
import re
import zipfile
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDB_XLSX = os.path.join(BASE_DIR, 'dataset', 'INDB', 'INDB.xlsx')
CSV_PATH = os.path.join(BASE_DIR, 'dataset', 'indian_food_nutrition.csv')
BACKUP_PATH = os.path.join(BASE_DIR, 'dataset', 'indian_food_nutrition.backup.csv')

def parse_indb_xlsx(xlsx_path):
    print(f"Reading INDB from {xlsx_path}...")
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                text_pieces = [t.text or '' for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')]
                shared_strings.append(''.join(text_pieces))

        sheet_tree = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        sheet_data = sheet_tree.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData')
        
        rows = []
        for r in sheet_data.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            row_vals = {}
            for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                r_coord = c.get('r')
                col_letter = ''.join([ch for ch in r_coord if ch.isalpha()])
                t = c.get('t')
                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = v.text if v is not None else ''
                if t == 's' and val.isdigit() and int(val) < len(shared_strings):
                    val = shared_strings[int(val)]
                row_vals[col_letter] = val
            rows.append(row_vals)

    data_rows = rows[1:]
    items = []
    for r in data_rows:
        raw_name = re.sub(r'\s+', ' ', r.get('B', '')).strip()
        if not raw_name:
            continue
        
        try:
            kcal = max(0.0, round(float(r.get('E', 0) or 0), 1))
            carb = max(0.0, round(float(r.get('F', 0) or 0), 1))
            prot = max(0.0, round(float(r.get('G', 0) or 0), 1))
            fat  = max(0.0, round(float(r.get('H', 0) or 0), 1))
            ca   = max(0.0, round(float(r.get('O', 0) or 0), 1))
            fe   = max(0.0, round(float(r.get('T', 0) or 0), 1))
            vc   = max(0.0, round(float(r.get('AO', 0) or 0), 1))
            unit = r.get('AQ', '').strip()
            
            items.append({
                'food_name': raw_name,
                'calories': str(kcal),
                'protein': str(prot),
                'carbs': str(carb),
                'fats': str(fat),
                'vit_c': str(vc),
                'calcium': str(ca),
                'iron': str(fe),
                'serving_unit': unit
            })
        except Exception as e:
            print(f"Skipping row {raw_name} due to error: {e}")

    print(f"Successfully parsed {len(items)} recipes from INDB.")
    return items

def merge_datasets():
    # 1. Read existing CSV
    existing_rows = []
    existing_keys = set()
    
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                existing_rows.append(r)
                existing_keys.add(r['food_name'].strip().lower())
                
        # Backup existing CSV
        with open(BACKUP_PATH, 'w', encoding='utf-8', newline='') as f:
            if existing_rows:
                writer = csv.DictWriter(f, fieldnames=list(existing_rows[0].keys()))
                writer.writeheader()
                writer.writerows(existing_rows)
        print(f"Backed up {len(existing_rows)} existing foods to {BACKUP_PATH}.")

    # 2. Parse INDB items
    indb_items = parse_indb_xlsx(INDB_XLSX)

    # 3. Merge: keep existing foods, add new INDB foods
    merged = list(existing_rows)
    added_count = 0
    
    for item in indb_items:
        key = item['food_name'].strip().lower()
        if key not in existing_keys:
            merged.append(item)
            existing_keys.add(key)
            added_count += 1

    print(f"Added {added_count} new authentic Indian foods from INDB.")
    print(f"Total merged database size: {len(merged)} foods.")

    # 4. Write merged CSV
    fieldnames = ['food_name', 'calories', 'protein', 'carbs', 'fats', 'vit_c', 'calcium', 'iron', 'serving_unit']
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in merged:
            row_dict = {
                'food_name': r.get('food_name', '').strip(),
                'calories': r.get('calories', '0.0'),
                'protein': r.get('protein', '0.0'),
                'carbs': r.get('carbs', '0.0'),
                'fats': r.get('fats', '0.0'),
                'vit_c': r.get('vit_c', '0.0'),
                'calcium': r.get('calcium', '0.0'),
                'iron': r.get('iron', '0.0'),
                'serving_unit': r.get('serving_unit', '')
            }
            writer.writerow(row_dict)

    print(f"Successfully saved master database to {CSV_PATH}!")

if __name__ == '__main__':
    merge_datasets()
