import json
import pathlib
import sys

import pandas as pd


class ExternalDataManager:
    
    def __init__(self):
        self._filepath = pathlib.Path()
        self._supported_formats = {
            'import': {
                '.json': self._import_json
            },
            'export': {
                '.json': self._export_json
            }
        }
    

    def input_filepath(self, message):
        try:
            user_filepath = pathlib.Path(input(message))
            if not user_filepath.exists():
                raise OSError('Enter a path to an existing file')
            if not user_filepath.is_file():
                raise OSError('Only files are allowed')
            if user_filepath.is_reserved():
                raise OSError('Do not use reserved files!')
        except OSError as ose:
            print(ose)
            sys.exit(1)
        self._filepath = user_filepath


    def io_data(self, action, *args, **kwargs):
        if not action in self._supported_formats:
            raise KeyError('Please, only pass "import" or "export"')
        try:
            return self._supported_formats[action][self._filepath.suffix](*args, **kwargs)
        except KeyError as ke:
            print('Sorry, no file format supported ;(')
            sys.exit(1)

    
    def _import_json(self):
        with open(self._filepath, "r") as read_file:
            data =  json.load(read_file)
        return data

    
    def _export_json(self, data):
        export_filepath = self._filepath.with_name(f'results_{self._filepath.name}')
        with open(export_filepath, "w") as write_file:
            json.dump(data, write_file, indent=4)
        return export_filepath


def convert_to_dataframes(zones, trips, restrictions):
    return [pd.DataFrame(base_trips, index=base_zones, columns=base_zones),
            pd.DataFrame(base_restrictions, index=base_zones)]

def prepare_export_data(trips, restrictions):
    return {
        'zones': trips.index.tolist(),
        'trips': trips.values.tolist(),
        'restrictions': {
            'origins': trips.sum(axis="columns").values.tolist(),
            'destinies': trips.sum(axis="index").values.tolist()
        }
    }

def distribute_trips(trips, restrictions):
    affected_trips = trips.copy()
    pivot_origins = affected_trips.sum(axis='columns')
    origins_expansion_factors = restrictions['origins'].div(pivot_origins, axis='index')
    affected_trips = affected_trips.mul(origins_expansion_factors, axis='index')
    affected_trips = affected_trips.round(0)
    pivot_destinies = affected_trips.sum(axis='index')
    destinies_expansion_factors = restrictions['destinies'].div(pivot_destinies, axis='index')
    affected_trips = affected_trips.mul(destinies_expansion_factors, axis='columns')
    affected_trips = affected_trips.round(0)
    return affected_trips


if __name__ == '__main__':
    data_manager = ExternalDataManager()
    data_manager.input_filepath('Enter source file path: ')
    base_zones, base_trips, base_restrictions = data_manager.io_data('import').values()
    trips, restrictions = convert_to_dataframes(base_zones,
                                                base_trips,
                                                base_restrictions)
    distributed_trips = distribute_trips(trips, restrictions)
    export_data = prepare_export_data(distributed_trips, restrictions)
    export_path = data_manager.io_data('export', data=export_data)
    print(f'Done! Results published in {export_path}.')