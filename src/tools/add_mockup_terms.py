import json, os

safe_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

vi_master_path = os.path.join(safe_dir, "vi_text", "i2languages_vi.json")
vi_part8_path = os.path.join(safe_dir, "vi_text", "part_8_vi.json")
terms_path = os.path.join(safe_dir, "raw_text", "i2languages_terms.json")

long_vi = "Chào mừng bạn đến với thế giới đại dương bao la của Flotsam! Hãy cùng các cư dân trôi dạt trục vớt rác thải biển, thu gom gỗ vụn và nhựa trôi nổi để mở rộng cụm bè sinh tồn. Xây dựng các công trình lọc nước ngọt, chế biến thức ăn, thiết lập mạng lưới điện lươn và phân bổ công việc hợp lý để duy trì sự sống. Chúc bạn có một hải trình sinh tồn thật thú vị và kiên cường vượt qua mọi sóng gió!"
short_vi = "Hãy thu gom rác thải trôi nổi và xây dựng cụm bè vững chắc để cùng các cư dân sinh tồn giữa đại dương."
homepage_vi = "Dưới đây là các bài hướng dẫn chi tiết giúp bạn nhanh chóng làm quen và làm chủ thế giới sinh tồn Flotsam!"

mockup_entries = {
    # 1. Exact string from user prompt
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs to be localized, or get a tooltip? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab.": long_vi,

    # 2. Exact string from asset files with double newlines
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs to be localized, or get a tooltip? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab.\n\nAnyway, have fun!": long_vi,

    # 3. Normalized by I2Utils.GetValidTermName
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs to be localized, or get a tooltip? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab. Anyway, have fun!": long_vi,

    # 4. Single newline variant
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs to be localized, or get a tooltip? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab.\nAnyway, have fun!": long_vi,

    # 5. Content size fitter variant
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs a content size fitter? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab.\n\nAnyway, have fun!": long_vi,

    # 6. Content size fitter normalized
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs a content size fitter? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab. Anyway, have fun!": long_vi,

    # 7. Repeating variant
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs to be localized, or get a tooltip? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab.\n\nAnyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!\n": long_vi,

    # 8. Repeating variant normalized
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs to be localized, or get a tooltip? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab. Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun! ": long_vi,
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. Maybe this needs to be localized, or get a tooltip? Oh and by the way, do not override the font settings! That would defeat the purpose of this pretty little prefab. Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!Anyway, have fun!": long_vi,

    # 9. Short variant
    "Well this is a mockup description! It's intent is to test the UI element where this belongs.": short_vi,

    # 10. Short variant with trailing space
    "Well this is a mockup description! It's intent is to test the UI element where this belongs. ": short_vi,

    # 11. Tutorial homepage variant
    "This is a mockup description describing the fact that there's cool tutorials to check out below here! Heyoo": homepage_vi
}

# 1. Update i2languages_vi.json
with open(vi_master_path, "r", encoding="utf-8") as f:
    vi_master = json.load(f)

for k, v in mockup_entries.items():
    vi_master[k] = v

with open(vi_master_path, "w", encoding="utf-8") as f:
    json.dump(vi_master, f, ensure_ascii=False, indent=2)
print(f"Updated {vi_master_path}: total keys = {len(vi_master)}")

# 2. Update part_8_vi.json
with open(vi_part8_path, "r", encoding="utf-8") as f:
    vi_part8 = json.load(f)

for k, v in mockup_entries.items():
    vi_part8[k] = v

with open(vi_part8_path, "w", encoding="utf-8") as f:
    json.dump(vi_part8, f, ensure_ascii=False, indent=2)
print(f"Updated {vi_part8_path}: total keys = {len(vi_part8)}")

# 3. Update i2languages_terms.json
with open(terms_path, "r", encoding="utf-8") as f:
    terms = json.load(f)

existing_terms = {t["term"] for t in terms}
added_count = 0
for k in mockup_entries:
    if k not in existing_terms:
        terms.append({
            "term": k,
            "type": 0,
            "langs": [k] * 15,
            "flags": [0] * 15,
            "touch_date": 0
        })
        added_count += 1

with open(terms_path, "w", encoding="utf-8") as f:
    json.dump(terms, f, ensure_ascii=False, indent=2)
print(f"Updated {terms_path}: total terms = {len(terms)} (added {added_count} terms)")