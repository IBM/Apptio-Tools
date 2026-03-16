"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
"""

import os
import csv
import re
import sys
import json
import argparse

from time import time
from apptio_lib import cloudability as cldy
from apptio_lib import apptio as apptio

'''
Purpose: Update and create business mappings.
Takes all CSV files in the current directory.
The first column is the match dimension, and the rest are business mapping names.

Notes:
* The business mapping names must exactly match the names in Cloudability.
* The match dimension should be in the same format we'd use when creating a BM via API
  * e.g. TAG['Cost Center'], BUSINESS_DIMENSION['Cost Center']
* Only one dimension is supported per CSV file.

Example CSV:
TAG['Cost Center'],Mapped Department,Mapped Team
1234,Finance,Team A
4321,HR,Team B
5678,Finance,Team C

Usage:
python update_mappings_from_csv.py --cldy-key <api_key> [--region <region>] [--debug]
OR
python update_mappings_from_csv.py --public <pub_key> --private <priv_key>
'''

def main():
    parser = argparse.ArgumentParser(description="Update and create business mappings.")
    
    # Credential Arguments
    parser.add_argument("--cldy-key", help="Cloudability API Key")
    parser.add_argument("--opentoken", help="Existing OpenToken")
    parser.add_argument("--public", help="Apptio Public Key")
    parser.add_argument("--private", help="Apptio Private Key")
    
    # Configuration Arguments
    parser.add_argument("--region", default="", help="Optional region (defaults to US Frontdoor)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (no changes made to Cloudability)")

    args = parser.parse_args()

    # Authentication Logic
    api_key = args.cldy_key
    token = args.opentoken
    public = args.public
    private = args.private
    region = args.region
    debug = args.debug

    if public and private:
        token = apptio.get_auth(public=public, private=private)
    
    opentoken_headers = {}
    if token:
        opentoken_headers = apptio.make_opentoken_headers(token)

    if not (api_key or opentoken_headers):
        print('Missing credentials. Please provide --cldy-key, --opentoken, or BOTH --public and --private keys.')
        sys.exit(1)

    new_mappings = {}
    # We'll use every CSV in the current directory to make the mappings.
    for file in os.listdir('.'):
        file_mappings = {}
        if file.endswith('.csv'):
            print(f'Found CSV file: {file}')
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                if not rows:
                    continue

                headers = list(rows[0].keys())
                match_dim = headers[0]
                bm_names = headers[1:]
                file_mappings = make_mappings(rows, match_dim, bm_names)
            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue

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
        current_mappings_result = cldy.get('/business-mappings', api_key=api_key, region=region, opentoken_headers=opentoken_headers)
        current_mappings_result = current_mappings_result.get('result', [])
        for mapping in current_mappings_result:
            current_mappings[mapping['name']] = mapping

        # backup current mappings
        if not os.path.exists('Backup'):
            os.makedirs('Backup')
        timestamp = str(int(time()))
        with open(f'Backup/current_mappings_{timestamp}.json', 'w') as f:
            json.dump(current_mappings, f, indent=4)

    for new_mapping in new_mappings.values():
        if debug:
            bm_json = json.dumps(new_mapping, indent=4)
            if not os.path.exists('Debug Files'):
                os.makedirs('Debug Files')
            with open(f'Debug Files/{new_mapping["name"]}.json', 'w') as f:
                f.write(bm_json)
            print(f'Debug is on. File saved to Debug Files/{new_mapping["name"]}.json')
            continue

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
            
            response = cldy.put(bm_ep, api_key, data=new_mapping, region=region, opentoken_headers=opentoken_headers)
        else:
            print(f'No existing mapping found for {new_mapping["name"]}. Creating new mapping.')        
            response = cldy.post('/business-mappings', api_key, data=new_mapping, region=region, opentoken_headers=opentoken_headers)

        if not isinstance(response, dict):
            print(f'Error updating mapping: {new_mapping["name"]}')
            parse_and_print_bm_errors(new_mapping, response)


def make_mappings(rows, match_dim, bm_names):
    bms = {}
    for bm_name in bm_names:
        bms[bm_name] = {}

    for row in rows:
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
                continue

            if "'" in bm_value:
                bm_value = bm_value.replace("'", "\\'")
            
            statement = {
                "matchExpression": f"{match_dim} IN ('{match_list_str}')",
                "valueExpression": f"'{bm_value}'"
            }
            bm['statements'].append(statement)
        
        new_mappings[bm_name] = bm
    
    return new_mappings


def parse_and_print_bm_errors(mapping, response):
    if isinstance(response, dict) or not hasattr(response, 'status_code'):
        return
    
    if response.status_code == 400:
        try:
            error_json = response.json()
            messages = error_json.get('error', {}).get('messages', [])
            if not messages:
                print('Error:', error_json)
                return
            
            split_errors = messages[0].split('\n')
            for error in split_errors:
                split_message = error.split(' ')
                statement_number = None
                column = None
                key = None

                if 'statement' in split_message:
                    idx = split_message.index('statement') + 1
                    statement_number = split_message[idx].strip('[](),.')

                if 'column' in split_message:
                    idx = split_message.index('column') + 1
                    column = split_message[idx]

                if 'matchExpression:' in split_message:
                    key = 'matchExpression'
                elif 'valueExpression:' in split_message:
                    key = 'valueExpression'

                if statement_number and column and key:
                    print(f'Error in statement: {statement_number}')
                    print(f'Error in {key} at column {column}-ish')
                    val = mapping['statements'][int(statement_number)-1][key]
                    print(f'"{key}": "{val}"')
        except Exception:
            print("Could not parse error response.")

if __name__ == '__main__':
    main()