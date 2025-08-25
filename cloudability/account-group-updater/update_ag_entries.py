"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
"""

import os
import csv
import sys
from time import time, sleep
from charset_normalizer import from_path
from apptio_lib import cloudability as cldy
from apptio_lib import apptio as apptio


# Purpose: Update Account Group values for accounts based on CSV files
# Takes in all CSV files in the same directory.
# Looks for "vendor_account_id" or "vendor_account_name" as the first column and AG names the other columns
# Finds the matching account group Ids from the API and matches those IDs to the AG names in the column headers.
# updates all AG values found in the column headers to the associated IDs.
#
# Prerequisite:
#  * account groups must exist in the environment
#  * uses Cloudability API key vs. FD public/secret
#       Put cldy key on the command line
# Known issues:
#   * vendor account ID must be in format ####-####-#### for AWS account IDs. There is untested code to do this included
#   * 429 errors for too many API requests. May need to run repeatedly if there are too many updates being made.
#   * configurable delay has been added 0.5 - 1 sec seems to work best when making more than 1K updates


def main():
    if len(sys.argv) == 1:
        print('Missing api key. Quitting')
        return
    api_key = sys.argv[1]

    # opentoken_headers = make_opentoken_headers()
    opentoken_headers = {}


    files = []
    for file in os.listdir('./'):
        if (file[-4:] != '.csv'):
            continue  # skipping non-csv files
        if file[0] == '.':
            continue  # skipping .trashes and such, just in case.
        files.append('./' + file)
    if not files:
        print('No csv files found in current directory. Quitting')
        return False

    updates = parse_csv(files)
    if not updates:
        print('No values found in csv. Check headers for valid account identifiers?')
        return False
    
    print(f'Found {len(updates)} accounts in csv files.')

    account_groups = get_ag_list(api_key)  #getting AG names and IDs
    ag_entries = get_ag_entries(api_key, account_groups) #get list of current AG entries

    ag_lookup = {}
    for ag in account_groups:
        ag_lookup[ag['name']] = ag['id']
    account_mapping = get_acct_mapping(api_key) #get list of accounts in Cldy
    # account_mapping acts as a dual lookup. ID to name and name to ID

    save_ag_entries_backup(ag_entries, ag_lookup) #save current AG entries to a backup file

    update_data = []
    entry_count = 0
    skip_count = 0
    account_log = {'found': set(), 'not_found': set()}
    deleted_count = 0
    for acc_id, updated_entries in updates.items():
        if acc_id not in account_mapping:
            account_log['not_found'].add(acc_id)
            # print(f'Account {acc_id} not found in account mapping. Skipping')
            continue
        account_log['found'].add(acc_id)
        for ag_name, value in updated_entries.items():
            if not value:
                try:
                    current_entry = ag_entries[acc_id][ag_name]
                    delete_ag_entry(api_key, current_entry)
                    print(f'Deleting entry {current_entry['value']} for {acc_id} {ag_name}')
                    deleted_count += 1
                except KeyError:
                    # There wasn't a value, so there's nothing ot delete.
                    pass
                continue
            entry_id = None
            entry_count += 1
            if acc_id in ag_entries:
                if ag_name in ag_entries[acc_id]:
                    ag_value = ag_entries[acc_id][ag_name]['value']
                    if ag_value == value:
                        skip_count += 1
                        continue
                    entry_id = ag_entries[acc_id][ag_name]['id']
            data = {
                'id': entry_id,
                'value': value,
                'account_group_id': ag_lookup[ag_name],
                'account_identifier': acc_id,
                'ag_name': ag_name
            }
            update_data.append(data)


    if not update_data:
        print('No new or updated values added.')
        return
    
    if deleted_count > 0:
        print(f'Deleted {deleted_count} entries')

    print('')
    print(f'Updating {len(update_data)}')
    update_ag_entries(api_key, update_data)
    print('')
    print(f'Of {len(updates)} accounts in csv:')
    print(f'Found {len(account_log["found"])}')
    print(f'Not found {len(account_log["not_found"])}')
    return

def parse_csv(csv_files): #find csv, find encoding, pass to parse function
    account_ag_values = {}
    for csv_file in csv_files:
        use_encoding = ''
        result = from_path(csv_file).best() #looking for encoding from library
        if result is not None:
            use_encoding = result.encoding
        else:
            # Fallback to something sensible, e.g. 'utf-8'
            use_encoding = 'utf-8'
            
        if use_encoding:
            with open(csv_file, 'r', newline='', encoding=use_encoding) as csvfile:
                records = csv.DictReader(csvfile)
                if records:
                    accounts = parse_ag_updates(records, account_ag_values)
                return accounts
        
        print(f'CSV with unknown encoding. {csv_file}')

def parse_ag_updates(records, account_ag_values={}): #parsing the values in the CSV file
    acct_id_dims = ['Account Number', 'vendor_account_identifier', 'account_identifier']

    account_dim = None
    for record in records:
        acc_id = ''
        if not account_dim:
            for dim in acct_id_dims:
                if dim in record:
                    account_dim = dim
            if not account_dim:
                print('No acc ID found in header. Quitting')
                print(record)
                return False
        acc_id = record[account_dim]
        if acc_id.isnumeric() and len(acc_id) == 12:
            acc_id = format_aws_account_id(acc_id)
        ag_entries = {k:v for k, v in record.items() if k not in acct_id_dims}
        account_ag_values[acc_id] = ag_entries
    return account_ag_values


def get_vendors(api_key):
    # Get the list of vendors from the API
    end_point = f'/vendors'
    response = cldy.get(end_point, api_key)
    if 'error' in response:
        print(f'Error getting vendors: {response["error"]}')
        return []
    
    vendors = []
    for vendor in response['result']:
        vendors.append(vendor['key'])

    return vendors


def get_acct_mapping(api_key, separate_lookups=False):
    vendors = get_vendors(api_key)

    account_mapping = {}
    for vendor in vendors:
        end_point = f'/vendors/{vendor}/accounts?viewId=0'
        results = cldy.get(api_key=api_key, end_point=end_point)['result']
        if results:
            for result in results:
                account_id = result['vendorAccountId']
                if len(str(account_id)) == 12 and account_id.isnumeric() and vendor == 'aws':
                    account_id = format_aws_account_id(account_id)
                if result['vendorAccountName'] in account_mapping:
                    print(f'Warning: Duplicate account name found: {result["vendorAccountName"]}')
                    continue
                account_mapping[result['vendorAccountName']] = account_id
                account_mapping[account_id] = result['vendorAccountName']


    return account_mapping

def get_ag_list(api_key):
    ag_endpoint = f'/account_groups/?auth_token={api_key}'
    timer = time()
    ag_response = cldy.get(ag_endpoint, api_key)
    print(f'Got account group dimension list in {time() - timer} seconds. {len(ag_response)} found.')
    return ag_response

def get_ag_entries(api_key, ag_response):
    ag_entries_endpoint = f'/account_group_entries'

    timer = time()
    ag_entries_response = cldy.get(ag_entries_endpoint, api_key)
    print(f'Got account group entries in {time() - timer} seconds. {len(ag_entries_response)} entries found.')

    account_groups = {}
    for ag in ag_response:
        account_groups[ag['id']] = ag['name']

    account_group_entries = {}
    for entry in ag_entries_response:
        #removing hyphens to match account id format in rightsizing recs
        account_id = entry['account_identifier']
        ag_id = entry['account_group_id']
        if ag_id not in account_groups:
            # print(f'Account group ID {ag_id} not found in account groups. Skipping entry {entry}')
            continue

        if account_id.isnumeric() and len(account_id) == 12:
            print(account_id)
            account_id = format_aws_account_id(account_id)
        
        ag_name = account_groups[ag_id]
        if account_id not in account_group_entries:
            account_group_entries[account_id] = {}

        account_group_entries[account_id][ag_name] = {'ag_id': ag_id, 'value': entry['value'], 'id': entry['id']}

    return account_group_entries


def save_ag_entries_backup(ag_entries, ag_lookup):
    ag_entry_rows = []

    for account_id, entries in ag_entries.items():
        row = {'account_identifier': account_id}
        for ag in ag_lookup.keys():
            row[ag] = ''
            if ag in entries:
                row[ag] = entries[ag]['value']
            ag_entry_rows.append(row)

    # make sure a backups folder exists
    if not os.path.exists('backups'):
        os.makedirs('backups')

    timestamp = round(time())
    backup_filename = f'ag_entries_backup_{timestamp}.csv'
    backup_filepath = os.path.join('backups', backup_filename)
    with open(backup_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['account_identifier'] + list(ag_lookup.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in ag_entry_rows:
            writer.writerow(row)
    


def update_ag_entries(api_key, update_data):
    #Updates AG entries based on changes found when comparing CSV to current Cldy information
    end_point = f'/account_group_entries/'
    # set min time between requests to avoid rate limiting
    delay = 0.50 #time in secs
    timer = time()
    for data in update_data:
        if data['id']:
            ep = f'{end_point}{data["id"]}'
            payload = {'value': data['value']}
            result = cldy.put(ep, api_key, payload)
            if 'error' not in result:
                print(f'Updating value {data}')
                print(result)
            else:
                print(result)
        else:
            result = cldy.post(end_point, api_key, data)
            if 'error' not in result:
                print(f'New value {data}')
                print(result)
            else:
                print(result)
                print(end_point)
                print(data)
                print('\t----')
        time_diff = time() - timer #adding delay to avoid 429 time out errors
        if time_diff < delay:
            sleep(delay - time_diff)
            timer = time()

    return

def delete_ag_entry(api_key, entry):
    entry_id = entry['id']
    #Deletes AG entry based on ID
    end_point = f'/account_group_entries/{entry_id}'
    result = cldy.delete(end_point, api_key)
    if 'error' not in result:
        return True

def format_aws_account_id(id):
    #Format aws account Ids to have 0000-0000-0000, add leading 0s if needed
    id = str(id)
    group = 4
    char = '-'
    return char.join(id[i:i+group] for i in range(0, len(id), group))



if __name__ == '__main__':
    main()
