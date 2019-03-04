import json
# Language dictionaries

with open("it.json", "r", encoding="utf-8") as f:
    lang_it = json.load(f)

with open("en.json", "r", encoding="utf-8") as f:
    lang_en = json.load(f)