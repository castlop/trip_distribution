import json
import pathlib
import sys

import pandas as pd


SETTINGS = {
    'extraction': {
        'columns': {'start': 'P01', 'end': 'P12'},
        'index': {'start': 'P01', 'end': 'P12'},
        'restrictions': ['origins', 'destinies']
    }
}


class ExternalDataManager:
    
    def __init__(self):
        self._filepath = pathlib.Path()
        self._export_filepath = pathlib.Path()
        self._supported_formats = {
            'import': {
                '.json': self._import_json,
                '.csv': self._import_csv
            },
            'export': {
                '.json': self._export_json,
                '.csv': self._export_csv
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
    

    def output_filepath(self, message_dirpath, message_filename):
        try:
            user_output_dirpath = ''
            user_output_filename = ''

            user_output_dirpath = input(message_dirpath)
            user_output_dirpath = pathlib.Path(user_output_dirpath) \
                                if user_output_dirpath \
                                else self._filepath.parent
            if not user_output_dirpath.is_dir():
                raise OSError('** Enter only valid directories **')
            if user_output_dirpath.is_reserved():
                raise OSError('**Do not use reserved directories! **')
            user_output_filename = input(message_filename)
            user_output_filename = pathlib.Path(user_output_filename) \
                                if user_output_filename \
                                else pathlib.Path(f'results_{self._filepath.name}')
            if not user_output_filename.suffix in self._supported_formats['export']:
                raise OSError('** File format is not supported **')
            self._export_filepath = user_output_dirpath / user_output_filename
        except OSError as ose:
            print(ose)
            sys.exit(1)
        return self._export_filepath


    def io_data(self, action, *args, **kwargs):
        if not action in self._supported_formats:
            raise KeyError('Please, only pass "import" or "export"')
        try:
            if action == 'import':
                return self._supported_formats[action][self._filepath.suffix](*args, **kwargs)
            elif action == 'export':
                return self._supported_formats[action][self._export_filepath.suffix](*args, **kwargs)
        except KeyError as ke:
            print('Sorry, no file format supported ;(')
            sys.exit(1)

    
    def _import_json(self):
        return pd.read_json(self._filepath)
    

    def _import_csv(self):
        return pd.read_csv(self._filepath)

    
    def _export_json(self, data):
        data.to_json(self._export_filepath, indent=4)
        return self._export_filepath
    
    
    def _export_csv(self, data):
        data.to_csv(self._export_filepath)
        return self._export_filepath


def prepare_export_data(trips):
    export_trips = trips.copy()
    export_trips['origins'] = export_trips.sum(axis='columns')
    export_trips.loc['destinies'] = export_trips.sum(axis='index')
    return export_trips


def extract_data_from_import(imported_data):
    setting_columns = SETTINGS['extraction']['columns']
    setting_index = SETTINGS['extraction']['index']
    setting_origins, setting_destinies = SETTINGS['extraction']['restrictions']
    return {
        'trips': imported_data.loc[
            setting_columns['start'] : setting_columns['end'],
            setting_index['start'] : setting_index['end']
        ],
        'restrictions': {
            'origins': imported_data.loc[
                setting_columns['start'] : setting_columns['end'],
                setting_origins
            ],
            'destinies': imported_data.loc[
                setting_destinies,
                setting_index['start'] : setting_index['end']
            ]
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
    data_manager.output_filepath('Enter output directory (same as input if empty): ',
                                'Enter output filename ("results_*<input>" if empty): ')
    imported_data = data_manager.io_data('import')
    extracted_data = extract_data_from_import(imported_data)
    distributed_trips = distribute_trips(extracted_data['trips'],
                                         extracted_data['restrictions'])
    export_data = prepare_export_data(distributed_trips)
    export_path = data_manager.io_data('export', data=export_data)
    print(f'Done! Results published in {export_path}.')