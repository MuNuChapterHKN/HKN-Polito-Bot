"""
Language class. It retrieves from a json file two json object, organized 
as key-value pair
"""
import json

with open("it.json", "r", encoding="utf-8") as f:
    lang_it = json.load(f)

with open("en.json", "r", encoding="utf-8") as f:
    lang_en = json.load(f)