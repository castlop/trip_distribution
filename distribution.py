import json
import pathlib

import pandas as pd

def import_json(filepath):
    with open(filepath, "r") as read_file:
        data =  json.load(read_file)
    return data

def get_file_location():
    return pathlib.Path(input('Enter file path: '))

if __name__ == '__main__':
    filepath = get_file_location()
    base_zones, base_trips, base_restrictions = import_json(filepath).values()
