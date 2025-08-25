"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
"""

"""
Example CSV and resulting JSON payload for a Hierarchical Business Mapping (HBM) in Cloudability.
This is the same format of the CSV files used for importing HBM data in the UI.
* Note * We assume that the default value is (not set) (aka null) for each entry.
Also note that the first column must exactly match the name of an existing business mapping.
Application, L2, L3
A, LA, LC
B, LA, LC
C, LA, LC
D, LB, LE
E, LB, LE
F, LD, LF

{
    "orgId": 5432100,
    "name": "Test",
    "baseBusinessMapping": {
        "index": 1
    },
    "hierarchicalBusinessMappings": [
        {
            "defaultValue": "",
            "name": "L3"
        },
        {
            "defaultValue": "",
            "name": "L2"
        }
    ],
    "statementValues": {
        "columns": [
            "Application",
            "L2",
            "L3"
        ],
        "values": [
            {
                "Application": "A",
                "L2": "LA",
                "L3": "LC"
            },
            {
                "Application": "B",
                "L2": "LA",
                "L3": "LC"
            },
            {
                "Application": "C",
                "L2": "LA",
                "L3": "LC"
            },
            {
                "Application": "D",
                "L2": "LB",
                "L3": "LE"
            },
            {
                "Application": "E",
                "L2": "LB",
                "L3": "LE"
            },
            {
                "Application": "F",
                "L2": "LD",
                "L3": "LF"
            }
        ]
    }
}
"""

import os
import csv
import sys
import json
from apptio_lib import cloudability as cldy

def main():

    ####
    # This script is for updating Hierarchical Business Mappings (HBM) in Cloudability.
    # It reads CSV files in the current directory, where each file corresponds to one HBM
    # The name of the file should exactly match the name of the HBM in Cloudability.
    # The format of the CSV should match the template from Cloudability.
    ####

    api_key = ''
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
       print('Missing api key. Quitting')

    region = ''
    name = ''
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg.endswith('-region'):
                region = sys.argv[sys.argv.index(arg) + 1]

            elif arg.endswith('-name'):
                name = sys.argv[sys.argv.index(arg) + 1]
        if not region and not name:
            print('Unknown arguments found. Quitting')
            print('Valid arguments are:')
            print(' -region <region>')
            print(' -name <name>')
            return

    current_bms = {}
    all_bms_response = cldy.get('/business-mappings', api_key=api_key, region=region)
    if isinstance(all_bms_response, dict):
        for bm in all_bms_response.get('result', []):
            current_bms[bm['name']] = bm

    current_hbms = {}
    hbm_ep = '/internal/hierarchical-business-mappings'
    current_result = cldy.get(hbm_ep, api_key=api_key, region=region)
    if isinstance(current_result, dict):
        org_id = current_result.get('orgId', None)
        current_result = current_result['result']['mappings']
        if not org_id:
            # The HBM endpoint should always return the orgId, but juuust in case:
            org_settings = cldy.get('/internal/organization/settings', api_key=api_key, region=region)
            org_id = org_settings['id']
        for hbm in current_result:
            current_hbms[hbm['name']] = hbm

    statements = {
        'columns': [],
        'values': []
    }

    for file in os.listdir('.'):
        # We'll use the first CSV in the current directory to make the mappings.
        # We could set it up so that each CSV is for one HBM
        # but we'll just do one for now.
        file_mappings = {}
        if not file.endswith('.csv'):
            continue 
        
        current_hbm_index = None
        baseBusinessMapping = None
        baseMappingIndex = None
        print(f'Using CSV file: {file}')
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not name:
            print(f'No -name argument found. Using name from file for HBM: {file}')
            name = os.path.splitext(file)[0]

        if name not in current_hbms:
            print(f'{name} not found in current hierarchical business mappings. Creating new HBM.')
        else:
            current_hbm_index = current_hbms[name]['index']

        headers = list(rows[0].keys())
        # Columns go backwards from the end, skipping the first column.
        statements['columns'] = headers
        baseBusinessMapping = headers[0]
        if baseBusinessMapping not in current_bms:
            print(f'ERROR: {baseBusinessMapping} not found in current business mappings. Quitting.')
            exit(1)
        baseMappingIndex = current_bms[baseBusinessMapping]['index']
        statements['values'] = make_hbm_values(rows)

        if not statements['values']:
            print(f'No values found in {file}. Skipping this file.')
            continue

        sub_mappings = []
        for column in headers[-1:0:-1]:
            sub_mapping = {
                "name": column,
                # To change default values, modify the following line
                "defaultValue": ""
            }
            sub_mappings.append(sub_mapping)

        new_mapping = {
            "orgId": org_id,
            "name": name,
            "baseBusinessMapping": {
                "index": baseMappingIndex
            },
            "hierarchicalBusinessMappings": sub_mappings,
            "statementValues": statements
        }
        if current_hbm_index >= 0:
            new_mapping['index'] = current_hbm_index
        print(f'Creating or updating HBM: {name}')
        response = cldy.post('/internal/hierarchical-business-mappings', api_key=api_key, data=new_mapping)
        if isinstance(response, dict) and 'result' in response:
            print(f'Successfully created or updated HBM: {name}')
        else:
            print(f'Failed to create or update HBM: {name}')
            print(response)


def make_hbm_values(rows):
    # This function will take the rows from the CSV and return a list of dictionaries
    # where each dictionary is a row with the business mapping values.
    values = []
    for row in rows:
        value_row = {}
        for key, value in row.items():
            if not value:
                value = ''
            value_row[key] = value
        values.append(value_row)
    return values


if __name__ == '__main__':
    main()