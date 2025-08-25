"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
"""

import os
import csv
import sys
import json
from apptio_lib import cloudability as cldy

def main():
    api_key = ''
    if len(sys.argv) >= 1:
        api_key = sys.argv[1]
    else:
       print('Missing api key. Quitting')

    debug = False
    region = ''
    
    for arg in sys.argv:
        if 'debug' in arg:
            debug = True
        
    use_test_mapping = False
    if len(sys.argv) >= 2:
        if '-test' in sys.argv:
            use_test_mapping = True

    new_mappings = {}
    if use_test_mapping:
        new_mappings = make_test_mappings()

    if not new_mappings:
        # We'll use every CSV in the current directory to make the mappings.
        for file in os.listdir('.'):
            file_mappings = {}
            if file.endswith('.csv'):
                print(f'Found CSV file: {file}')
                with open(file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                headers = list(rows[0].keys())
                match_dim = headers[0]
                match_dim_type = 'DIMENSION'
                bm_names = [headers[1]]
                file_mappings = make_mappings(rows, match_dim, bm_names, match_dim_type)
                break


        for bm_name, bm in file_mappings.items():
            # if the mapping already exists, merge the new values with the existing ones
            if bm_name in new_mappings:
                combined_statements = new_mappings[bm_name]['statements'] + bm['statements']
                new_mappings[bm_name]['statements'] = combined_statements
            else:
                new_mappings[bm_name] = bm
        
        
    
    # get current mappings from Cloudability
    current_mappings = {}
    if not debug:
        current_mappings_result = cldy.get('/business-mappings', api_key=api_key)
        current_mappings_result = current_mappings_result['result']
        for mapping in current_mappings_result:
            current_mappings[mapping['name']] = mapping

    for new_mapping in new_mappings.values():
        if new_mapping['name'] in current_mappings:
            current_mapping = current_mappings[new_mapping['name']]
            if current_mapping.get('isReadOnly'):
                print(f'{new_mapping["name"]} is read only. Skipping')
                continue
            if new_mapping['statements'] == current_mapping['statements']:
                print(f'{new_mapping["name"]} matches. Skipping')
                continue
            print(f'Replacing {new_mapping["name"]} with new values')
            index = current_mapping['index']
            bm_ep = f'/business-mappings/{index}'
            if debug:
                bm_json = json.dumps(new_mapping, indent=4)
                # check for Debug Files folder
                if not os.path.exists('Debug Files'):
                    os.makedirs('Debug Files')
                with open(f'Debug Files/{new_mapping["name"]}.json', 'w') as f:
                    f.write(bm_json)
                print(f'Debug is on. No changes made to CLDY.')
                print(f'File saved to Debug Files/{new_mapping["name"]}.json')
            else:
                response = cldy.put(bm_ep, api_key, new_mapping)
        else:
            print(f'No existing mapping found for {new_mapping["name"]}. Creating new mapping.')
            if debug:
                bm_json = json.dumps(new_mapping, indent=4)
                # check for Debug Files folder
                if not os.path.exists('Debug Files'):
                    os.makedirs('Debug Files')
                with open(f'Debug Files/{new_mapping["name"]}.json', 'w') as f:
                    f.write(bm_json)
                print(f'Debug is on. No changes made to CLDY.')
                print(f'File saved to Debug Files/{new_mapping["name"]}.json')
            else:
                response = cldy.post('/business-mappings', api_key, new_mapping)

        if not debug and not isinstance(response, dict):
            print(f'Error creating mapping: {new_mapping["name"]}')
            # print(response)
            cldy.parse_and_print_bm_errors(new_mapping, response)


def make_mappings(rows, match_dim, bm_names, match_dim_type):
    bms = {}

    for bm_name in bm_names:
        bms[bm_name] = {}

    for row in rows:
        # collecting unique values and their corresponding match_dim values
        for bm_name, value in row.items():
            
            if bm_name == match_dim or bm_name not in bm_names:
                continue
            if value not in bms[bm_name]:
                bms[bm_name][value] = set()
            bms[bm_name][value].add(row[match_dim])

    new_mappings = {}
    for bm_name, bm_values in bms.items():
        bm = {
            "name": bm_name,
            "kind": "BUSINESS_DIMENSION",
            "defaultValue": "(not set)",
            'statements': []
        }
        for bm_value, match_list in bm_values.items():
            match_list_str = "', '".join(match_list)
            if not bm_value:
                print(f'WARNING: {len(match_list)} rows with no value for {bm_name}')
                # print(', '.join(match_list))
                continue
            if "\\" in bm_value:
                print(bm_value)
                print(repr(bm_value))
                print(repr(json.dumps(bm_value)))
                # bm_value = bm_value.replace("\\", "\\\\")
                print(repr(json.dumps(bm_value)))

            if "'" in bm_value:
                # escape single quotes with backslash
                bm_value = bm_value.replace("'", "\\'")
            statement = {
                "matchExpression": f"{match_dim_type}['{match_dim}'] IN ('{match_list_str}')",
                "valueExpression": f"'{bm_value}'"
            }
            if "\\" in bm_value:
                print(json.dumps(statement))
                exit()
            
            bm['statements'].append(statement)
        

        new_mappings[bm_name] = bm
    
    return new_mappings
                
def make_test_mappings():
    # mapping with purposefully bad matchExpression and valueExpression to test error handling
    # if you use a working BM it will be uploaded to CLDY, so be careful!
    return {
        'Test Mapping': {
            "name": "Test Mapping",
            "kind": "BUSINESS_DIMENSION",
            "defaultValue": "(not set)",
            'statements': [
                {
                    "matchExpression": "BUSINESS_DIMENSION['Account'] IN ('1234567890')",
                    "valueExpression": "'Test Mapping"
                    # missing closing quote
                },
                {
                    "matchExpression": "BUSINESS_DIMENSION['Account'] IN ('0987654321', '1234', 123', '4533', '123')",
                    # missing opening quote
                    "valueExpression": "'Test Mapping'"
                }
            ]
        }
    }

def parse_and_print_bm_errors(mapping, response):
    if isinstance(response,dict):
        return
    
    if response.status_code == 400:
        error_json = response.json()
        if 'error' not in error_json:
            print('Error: ', error)
            return
        
        if 'messages' not in error_json['error']:
            print('Error: ', error_json['error'])
            return
        
        split_errors = error_json['error']['messages'][0].split('\n')
        
        for error in split_errors:
            statement_number = False
            column = False
            key = False
            split_message = error.split(' ')
            if 'statement' in split_message:
                statement_number = split_message.index('statement') + 1
                statement_number = split_message[statement_number]
                # removing the 1st and last character of string
                statement_number = statement_number[1:-1]
                # print('statement_number')

            if 'column' in split_message:
                column = split_message.index('column') + 1
                column = split_message[column]

            if 'matchExpression:' in split_message:
                key = 'matchExpression'
            elif 'valueExpression:' in split_message:
                key = 'valueExpression'

            if statement_number and column and key:

                print(f'Error in statement: {statement_number}')
                print(f'Error in {key} at column {column}-ish')
                value = mapping['statements'][int(statement_number)-1][key]
                print(f'"{key}": "{value}"')
                # print carrot under the error
                col_padding = len(key) + 4
                print(' ' * (int(column)-5 + col_padding) + '^^^^^^^^')

    return


if __name__ == '__main__':
    main()