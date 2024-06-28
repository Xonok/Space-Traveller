import pandas as pd
import csv
import json
from collections import defaultdict

def def_value():
    return []

def init_dict(items):
    d = defaultdict(def_value)
    for item in items:
        d[item] = []
    return d

items = pd.read_csv("items.csv")
industries = pd.read_csv("industries.csv")
machines = pd.read_csv("machines.csv")
blueprints = pd.read_csv("blueprints.csv")
# rename inputs and outputs to input and output in blueprints
blueprints.rename(columns={"inputs": "input", "outputs": "output"}, inplace=True)

recipes = pd.concat([industries, machines, blueprints], axis=0)


# find which inputs are used to make which outputs. put them into a dictionary, where the key is the input and the value is a list of outputs

input_to_output = init_dict(items["item_name"])
output_to_input = init_dict(items["item_name"])

for index, row in recipes.iterrows():
    fixed_input = row["input"].replace("'", '"')
    fixed_output = row["output"].replace("'", '"')
    for input in json.loads(fixed_input).keys():
        for output in json.loads(fixed_output).keys():
            input_to_output[input].append(output)
            output_to_input[output].append(input)

# remove duplicates
for key, value in input_to_output.items():
    input_to_output[key] = list(set(value))

for key, value in output_to_input.items():
    output_to_input[key] = list(set(value))


input_to_output = dict(input_to_output)
# turn the dictionary into a pandas dataframe
input_to_output_df = pd.DataFrame.from_dict(input_to_output, orient='index')
input_to_output_df.to_csv("input_to_output.csv", quoting=csv.QUOTE_NONNUMERIC)

output_to_input = dict(output_to_input)
# turn the dictionary into a pandas dataframe
output_to_input_df = pd.DataFrame.from_dict(output_to_input, orient='index')
output_to_input_df.to_csv("output_to_input.csv", quoting=csv.QUOTE_NONNUMERIC)
