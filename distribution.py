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

def distribute_trips(affected_trips, restrictions):
    pivot_origins = affected_trips.sum(axis='columns')
    origins_expansion_factors = restrictions['origins'].div(pivot_origins, axis='index')
    affected_trips = affected_trips.mul(origins_expansion_factors, axis='index')
    
    pivot_destinies = affected_trips.sum(axis='index')
    destinies_expansion_factors = restrictions['destinies'].div(pivot_destinies, axis='index')
    affected_trips = affected_trips.mul(destinies_expansion_factors, axis='columns')
    
    return affected_trips


if __name__ == '__main__':
    filepath = get_file_location()
    base_zones, base_trips, base_restrictions = import_json(filepath).values()
    trips, restrictions = convert_to_dataframes(base_zones,
                                                base_trips,
                                                base_restrictions)
    affected_trips = trips.copy()
    distributed_trips = distribute_trips(affected_trips, restrictions)