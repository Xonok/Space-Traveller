# list all files from defs/items

import os
import json
import pandas as pd


def get_json_files_in(path):
    result_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".json"):
                result_files.append(os.path.join(root, file))
    return result_files


def parse_item_file(file):
    print(file)
    with open(file, "r") as f:
        return json.loads(f.read())


def get_items(files):
    items = []
    for file in files:
        for k,v in parse_item_file(file).items():
            v["item_name"] = k
            items.append(v)

    return items


items = get_items(get_json_files_in(os.path.join("..", "..", "defs", "items")))
# denormalize items and put them into a pandas dataframe
items_df = pd.json_normalize(items)
items_df.to_csv("items.csv", index=False)

recipes = get_items(get_json_files_in(os.path.join("..", "..", "defs", "industries")))
# denormalize items and put them into a pandas dataframe
recipes_df = pd.json_normalize(recipes, max_level=0)
recipes_df.to_csv("industries.csv", index=False)

recipes = get_items([os.path.join("..", "..", "defs", "defs", "machines.json")])
# denormalize items and put them into a pandas dataframe
recipes_df = pd.json_normalize(recipes, max_level=0)
recipes_df.to_csv("machines.csv", index=False)

recipes = get_items(get_json_files_in(os.path.join("..", "..", "defs", "blueprints")))
# denormalize items and put them into a pandas dataframe
recipes_df = pd.json_normalize(recipes, max_level=0)
recipes_df.to_csv("blueprints.csv", index=False)