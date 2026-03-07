"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
"""

import os
import csv
import sys
import json
import argparse
import requests
from time import time, sleep
from charset_normalizer import from_path
from apptio_lib import cloudability as cldy

# Add parent directory to path to import auth_helper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_helper import setup_authentication, add_auth_arguments, parse_legacy_args, get_region_from_args

"""
Used for mass creation and updating of views in Cloudability.

This script reads CSV files in the current directory
where each CSV file contains view definitions.
Supports both Cloudability API key and Frontdoor public/private key authentication.

A view is defined by its name.
Any additional lines with the same view name will add filters to that view.

The CSV should have the following format:
View Name, Shared With Org, Dimension, Comparator, Value1, Value2, ...

Example CSV:
View Name, Shared With Org, Dimension, Comparator
Dev,true,tag1,=@,dev,staging,nonprod
Dev,true,vendor_identifier,!=,123412341234
Prod,false,tag1,==,prod
Prod,false,tag1,==,production
Prod,false,account_identifier,==,123412341234,432143214321


This would result in two views:
1. A view named "Dev" (shared with organization) with four filters
    -tag1 =@ dev
    -tag1 =@ staging
    -tag1 =@ nonprod
    -vendor_identifier != 123412341234
2. A view named "Prod" (not shared with organization) with four filters
    -tag1 == prod
    -tag1 == production
    -account_identifier == 123412341234
    -account_identifier == 432143214321

Notes on "Shared With Org":
- Accepts "true" or "false" (case-insensitive)
- Only applied when CREATING new views
- Existing views preserve their current sharing settings
- If multiple rows for same view have different values, the LAST row's value is used

It's often easier to create CSVs with many lines,
as opposed to keeping all values on the same line.
Feel free to use as many lines as are needed for each view.

A reminder of valid Cloudability view comparators:
- == : Equals
- != : Not Equals
- =@ : Contains
- !=@ : Does Not Contain

Usage:
  # Cloudability API Key:
  python views_updater.py --api-key YOUR_KEY
  
  # Frontdoor Authentication:
  python views_updater.py --frontdoor-public PUB --frontdoor-private PRIV --domain DOMAIN
  
  # Legacy format (still supported):
  python views_updater.py YOUR_API_KEY

"""

def main():

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Mass create and update views in Cloudability from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Add authentication arguments
    add_auth_arguments(parser)
    
    parser.add_argument(
        '--skip-dependency-check',
        action='store_true',
        help='Skip the dependency check at startup'
    )
    
    # Handle legacy format (positional API key)
    sys.argv = parse_legacy_args(sys.argv)
    
    args = parser.parse_args()
    
    # Check dependencies unless explicitly skipped
    if not args.skip_dependency_check:
        from dependency_checker import check_dependencies
        if not check_dependencies(include_optional=True, silent=False):
            print('\n❌ Cannot proceed without required dependencies.')
            print('   Run with --skip-dependency-check to bypass this check (not recommended).')
            sys.exit(1)
    
    # Setup authentication
    api_key, opentoken_headers = setup_authentication(args)
    
    region = get_region_from_args(args)

    current_views = {}
    views_ep = '/views'
    views_response = cldy.get(views_ep, api_key=api_key, opentoken_headers=opentoken_headers, region=region)
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
    # Skip example files
    csv_files = [f for f in csv_files if not f.startswith('example_')]
    new_views = {}
    view_shared_settings = {}  # Track shared_with_org per view (last row wins)
    
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == ['View Name']:
                    continue
                
                # Parse CSV: View Name, Shared With Org, Dimension, Comparator, Value1, Value2, ...
                view_name = row[0]
                shared_with_org_str = row[1].strip().lower() if len(row) > 1 else 'false'
                filter_dim = row[2] if len(row) > 2 else ''
                comparator = row[3] if len(row) > 3 else ''
                filter_values = row[4:] if len(row) > 4 else []
                
                # Parse shared_with_org (true/false, case-insensitive)
                shared_with_org = shared_with_org_str in ['true', '1', 'yes']
                
                # Store the shared_with_org value (last row wins if there are conflicts)
                view_shared_settings[view_name] = shared_with_org
                
                # Build filters
                filters = []
                for value in filter_values:
                    if value:
                        filters.append({
                            "field": filter_dim,
                            "comparator": comparator,
                            "value": value
                        })

                # Add filters to view
                if view_name in new_views:
                    new_views[view_name].extend(filters)
                else:
                    new_views[view_name] = filters


    for new_name, filters in new_views.items():
        id = None
        shared_with_users = []
        shared_with_org = False
        is_new_view = new_name not in current_views
        
        if new_name in current_views:
            if filters == current_views[new_name]['filters']:
                print(f"View '{new_name}' already exists with the same filters. Skipping update.")
                continue

            id = current_views[new_name]['id']
            shared_with_users = current_views[new_name].get('sharedWithUsers', [])
            # Preserve existing sharedWithOrganization for existing views
            shared_with_org = current_views[new_name].get('sharedWithOrganization', False)
        else:
            # For new views, use the value from CSV
            shared_with_org = view_shared_settings.get(new_name, False)

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
            response = cldy.put(ep, api_key=api_key, data=view_obj, opentoken_headers=opentoken_headers, region=region)
        else:
            shared_status = "shared with organization" if shared_with_org else "not shared with organization"
            print(f"Creating new view '{new_name}' ({shared_status}).")
            print(json.dumps(view_obj, indent=2))
            response = cldy.post(views_ep, api_key=api_key, data=view_obj, opentoken_headers=opentoken_headers)

        if not response:
            print(f"Failed to update or create view '{new_name}'.")
        else:
            print(f"Successfully updated or created view '{new_name}'.")

                



if __name__ == '__main__':
    main()