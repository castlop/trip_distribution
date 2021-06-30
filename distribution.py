import json
import pathlib

import pandas as pd

def import_json(filepath):
    with open(filepath, "r") as read_file:
        data =  json.load(read_file)
    return data

def get_file_location():
    return pathlib.Path(input('Enter file path: '))