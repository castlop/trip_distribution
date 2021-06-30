import json
import pathlib

import pandas as pd

def import_json(filepath):
    with open(filepath, "r") as read_file:
        data =  json.load(read_file)
    return data

def get_file_location():
    return pathlib.Path(input('Enter file path: '))

def convert_to_dataframes(zones, trips, restrictions):
    return [pd.DataFrame(base_trips, index=base_zones, columns=base_zones),
            pd.DataFrame(base_restrictions, index=base_zones)]

if __name__ == '__main__':
    filepath = get_file_location()
    base_zones, base_trips, base_restrictions = import_json(filepath).values()
    trips, restrictions = convert_to_dataframes(base_zones,
                                                base_trips,
                                                base_restrictions)
