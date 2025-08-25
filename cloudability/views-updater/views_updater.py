"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
"""

import os
import csv
import sys
import json
import requests
from time import time, sleep
from charset_normalizer import from_path
from apptio_lib import cloudability as cldy

"""
Used for mass creation and updating of views in Cloudability.

General usage
python view_updater.py <api_key> [-region <region>]

This script reads CSV files in the current directory
where each CSV file contains view definitions.

A view is defined by its name. 
Any additional lines with the same view name will add filters to that view. 

The CSV should have the following format:
View Name, Dimension, Comparator, Value1, Value2, ...

Example CSV:
View Name, Dimension, Comparator
Dev,tag1,=@,dev,staging,nonprod
Dev,vendor_identifier,!=,123412341234
Prod,tag1,==,prod
Prod,tag1,==,production
Prod,account_identifier,==,123412341234,432143214321


This would result in two views:
1. A view named "Dev" with four filters
    -tag1 =@ dev
    -tag1 =@ staging
    -tag1 =@ nonprod
    -vendor_identifier != 123412341234
2. A view named "Prod" with four filters
    -tag1 == prod
    -tag1 == production
    -account_identifier == 123412341234
    -account_identifier == 432143214321


It's often easier to create CSVs with many lines,
as opposed to keeping all values on the same line.
Feel free to use as many lines as are needed for each view.

A reminder of valid Cloudability view comparators:
- == : Equals
- != : Not Equals
- =@ : Contains
- !=@ : Does Not Contain



"""

def main():

    if len(sys.argv) < 2:
        print("Usage: python view_updater.py <api_key>")
        sys.exit(1)

    api_key = sys.argv[1]

    region = ''
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if 'region' in arg:
                # set region to next arg index
                region = sys.argv[sys.argv.index(arg) + 1]             

    current_views = {}
    views_ep = '/views'
    views_response = cldy.get(views_ep, api_key=api_key, region=region)
    if not views_response:
        print(views_response)
        print("Failed to retrieve views.")
        sys.exit(1)

    if 'result' not in views_response:
        print("No views found in the response.")
        sys.exit(1)

    for view in views_response['result']:
        current_views[view['title']] = view

    # time for the csvs!
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    new_views = {}
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == ['View Name']:
                    continue
                view_name = row[0]
                filter_dim = row[1]
                comparator = row[2]
                filter_values = row[3:]
                filters = []
                for value in filter_values:
                    if value:
                        filters.append({
                            "field": filter_dim,
                            "comparator": comparator,
                            "value": value
                        })


                if view_name in new_views:
                    new_views[view_name].extend(filters)
                else:
                    new_views[view_name] = filters


    for new_name, filters in new_views.items():
        id = None
        shared_with_users = []
        shared_with_org = False
        if new_name in current_views:        
            if filters == current_views[new_name]['filters']:
                print(f"View '{new_name}' already exists with the same filters. Skipping update.")
                continue

            id = current_views[new_name]['id']
            shared_with_users = current_views[new_name].get('sharedWithUsers', [])
            shared_with_org = current_views[new_name].get('sharedWithOrganization', False)

        view_obj = {
                "id": id,
                "title": new_name,
                "filters": filters,
                "sharedWithUsers": shared_with_users,
                "sharedWithOrganization": shared_with_org,
            }
        
        if view_obj['id']:
            print(f"Updating view '{new_name}' with ID {view_obj['id']}.")
            ep = f"{views_ep}/{view_obj['id']}"
            response = cldy.put(ep, api_key=api_key, data=view_obj, region=region)
        else:
            print(f"Creating new view '{new_name}'.")
            print(json.dumps(view_obj, indent=2))
            response = cldy.post(views_ep, api_key=api_key, data=view_obj)

        if not response:
            print(f"Failed to update or create view '{new_name}'.")
        else:
            print(f"Successfully updated or created view '{new_name}'.")

                



if __name__ == '__main__':
    main()