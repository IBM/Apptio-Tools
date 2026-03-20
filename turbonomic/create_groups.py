"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

Turbonomic Group Creator Script
Creates dynamic groups in Turbonomic based on CSV input file.
"""

import requests
import csv
import sys
import json
import time
import logging
import argparse
import os
import getpass
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
from collections import defaultdict

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TurbonomicGroupCreator:
    """Main class for creating Turbonomic groups from CSV"""
    
    # Filter types that use EQ (exact match) instead of RXEQ (regex)
    # Based on Turbonomic API behavior - tag filters and certain exact match filters use EQ
    EQ_FILTER_TYPES = {
        # Tag-based filters (use EQ for tag matching)
        'vmsByTag', 'namespacesByTag', 'podsByTag', 'businessAccountByTag',
        'containersByTag', 'workloadControllersByTag', 'servicesByTag',
        # Cloud provider and exact match filters
        'vmsByCloudProvider', 'vmsByState', 'vmsByDC', 'vmsByClusterName',
        'pmsByDC', 'namespacesByCluster',
        # Numeric comparison filters (use GT, LT, etc. not RXEQ)
        'pmsByMem', 'pmsByNumVms', 'vmsByMem', 'vmsByCPU'
    }
    
    def __init__(self, turbo_url: str, username: str, password: str, dry_run: bool = False, force: bool = False, update_mode: bool = False):
        """
        Initialize the Turbonomic Group Creator
        
        Args:
            turbo_url: Base URL of Turbonomic instance
            username: Username for authentication
            password: Password for authentication
            dry_run: If True, preview changes without creating groups
            force: If True, skip duplicate checking
            update_mode: If True, update existing groups instead of skipping them
        """
        self.turbo_url = turbo_url.rstrip('/')
        self.username = username
        self.password = password
        self.dry_run = dry_run
        self.force = force
        self.update_mode = update_mode
        self.session = requests.Session()
        self.session.verify = False  # For self-signed certificates
        
        # Statistics
        self.stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0
        }
        
    def authenticate(self) -> bool:
        """
        Authenticate to Turbonomic API and get session cookie
        
        Returns:
            True if authentication successful, False otherwise
        """
        login_url = urljoin(self.turbo_url, '/api/v3/login')
        
        try:
            logger.info(f"Authenticating to {self.turbo_url}...")
            response = self.session.post(
                login_url,
                data={
                    'username': self.username,
                    'password': self.password
                },
                params={'hateoas': 'true'}
            )
            
            if response.status_code == 200:
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_existing_groups(self) -> Dict[str, Dict]:
        """
        Get list of existing user-created groups
        
        Returns:
            Dictionary mapping group names to group data
        """
        groups_url = urljoin(self.turbo_url, '/api/v3/groups')
        
        try:
            response = self.session.get(
                groups_url,
                params={'group_origin': 'USER'}
            )
            
            if response.status_code == 200:
                groups = response.json()
                return {group['displayName']: group for group in groups}
            else:
                logger.warning(f"Could not fetch existing groups: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.warning(f"Error fetching existing groups: {str(e)}")
            return {}
    
    def get_default_exp_type(self, filter_type: str) -> str:
        """
        Determine the appropriate expression type based on filter type
        
        Args:
            filter_type: The filter type from CSV
            
        Returns:
            'EQ' for tag/exact match filters, 'RXEQ' for name-based filters
        """
        if filter_type in self.EQ_FILTER_TYPES:
            return 'EQ'
        return 'RXEQ'
    
    def validate_csv_row(self, row: Dict, row_num: int) -> Tuple[bool, Optional[str]]:
        """
        Validate a CSV row has required fields
        
        Args:
            row: Dictionary representing CSV row
            row_num: Row number for error reporting
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['group_name', 'group_type', 'filter_type', 'exp_val']
        
        for field in required_fields:
            if field not in row or not row[field].strip():
                return False, f"Row {row_num}: Missing required field '{field}'"
        
        return True, None
    
    def parse_csv(self, csv_file: str) -> List[Dict]:
        """
        Parse CSV file and return list of group configurations.
        Supports multiple criteria per group by grouping rows with the same group_name.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of group configuration dictionaries
        """
        groups_dict = defaultdict(lambda: {
            'criteriaList': [],
            'groupType': None,
            'logicalOperator': 'AND'
        })
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for idx, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    is_valid, error = self.validate_csv_row(row, idx)
                    
                    if not is_valid:
                        logger.error(error)
                        continue
                    
                    group_name = row['group_name'].strip()
                    group_type = row['group_type'].strip()
                    filter_type = row['filter_type'].strip()
                    logical_op = row.get('logical_operator', 'AND').strip().upper() or 'AND'
                    
                    # Intelligently determine exp_type based on filter_type if not explicitly provided
                    exp_type_raw = row.get('exp_type', '').strip()
                    if exp_type_raw:
                        exp_type = exp_type_raw
                    else:
                        # Auto-select based on filter type
                        exp_type = self.get_default_exp_type(filter_type)
                    
                    # Store group type (should be same for all rows with same group_name)
                    if groups_dict[group_name]['groupType'] is None:
                        groups_dict[group_name]['groupType'] = group_type
                        groups_dict[group_name]['logicalOperator'] = logical_op
                    elif groups_dict[group_name]['groupType'] != group_type:
                        logger.warning(f"Row {idx}: Group '{group_name}' has inconsistent group_type. Using first occurrence.")
                    
                    # Add criteria to the group
                    criteria = {
                        'expVal': row['exp_val'].strip(),
                        'expType': exp_type,
                        'filterType': filter_type,
                        'caseSensitive': row.get('case_sensitive', 'false').strip().lower() == 'true',
                        'entityType': None,
                        'singleLine': False
                    }
                    
                    # Log if auto-selected exp_type
                    if not exp_type_raw:
                        logger.debug(f"Auto-selected exp_type '{exp_type}' for filter_type '{filter_type}'")
                    
                    groups_dict[group_name]['criteriaList'].append(criteria)
            
            # Convert to list of group configurations
            groups = []
            for group_name, group_data in groups_dict.items():
                group_config = {
                    'displayName': group_name,
                    'className': 'Group',
                    'groupType': group_data['groupType'],
                    'isStatic': False,
                    'logicalOperator': group_data['logicalOperator'],
                    'memberUuidList': [],
                    'criteriaList': group_data['criteriaList']
                }
                groups.append(group_config)
            
            logger.info(f"Parsed {len(groups)} groups from CSV file")
            total_criteria = sum(len(g['criteriaList']) for g in groups)
            logger.info(f"Total criteria across all groups: {total_criteria}")
            return groups
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_file}")
            return []
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            return []
    
    def update_group(self, group_uuid: str, group_config: Dict) -> bool:
        """
        Update an existing group in Turbonomic
        
        Args:
            group_uuid: UUID of the group to update
            group_config: Group configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        group_url = urljoin(self.turbo_url, f'/api/v3/groups/{group_uuid}')
        
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would update group: {group_config['displayName']}")
                logger.debug(f"[DRY RUN] Config: {json.dumps(group_config, indent=2)}")
                return True
            
            response = self.session.put(
                group_url,
                json=group_config,
                params={'disable_hateoas': 'true'}
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✓ Updated group: {group_config['displayName']}")
                return True
            else:
                logger.error(f"✗ Failed to update group '{group_config['displayName']}': {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error updating group '{group_config['displayName']}': {str(e)}")
            return False
    
    def create_group(self, group_config: Dict) -> bool:
        """
        Create a group in Turbonomic
        
        Args:
            group_config: Group configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        groups_url = urljoin(self.turbo_url, '/api/v3/groups/')
        
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would create group: {group_config['displayName']}")
                logger.debug(f"[DRY RUN] Config: {json.dumps(group_config, indent=2)}")
                return True
            
            response = self.session.post(
                groups_url,
                json=group_config,
                params={'disable_hateoas': 'true'}
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✓ Created group: {group_config['displayName']}")
                return True
            elif response.status_code == 409:
                logger.warning(f"⚠ Group already exists: {group_config['displayName']}")
                return False
            else:
                logger.error(f"✗ Failed to create group '{group_config['displayName']}': {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error creating group '{group_config['displayName']}': {str(e)}")
            return False
    
    def save_backup(self, groups: List[Dict]):
        """
        Save backup of groups to be created
        
        Args:
            groups: List of group configurations
        """
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        timestamp = int(time.time())
        backup_file = f"backups/groups_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(groups, f, indent=2)
            logger.info(f"Backup saved to: {backup_file}")
        except Exception as e:
            logger.warning(f"Could not save backup: {str(e)}")
    
    def process_groups(self, csv_file: str):
        """
        Main processing function to create or update groups from CSV
        
        Args:
            csv_file: Path to CSV file
        """
        # Parse CSV
        groups = self.parse_csv(csv_file)
        
        if not groups:
            logger.error("No valid groups found in CSV file")
            return
        
        self.stats['total'] = len(groups)
        
        # Save backup
        self.save_backup(groups)
        
        # Get existing groups
        existing_groups = {}
        if not self.dry_run:
            existing_groups = self.get_existing_groups()
            logger.info(f"Found {len(existing_groups)} existing user groups")
        
        # Process each group
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {len(groups)} groups...")
        logger.info(f"{'='*60}\n")
        
        for idx, group_config in enumerate(groups, start=1):
            group_name = group_config['displayName']
            
            logger.info(f"[{idx}/{len(groups)}] Processing: {group_name}")
            
            # Check if group already exists
            if group_name in existing_groups:
                if self.update_mode:
                    # Update existing group
                    group_uuid = existing_groups[group_name].get('uuid')
                    if group_uuid:
                        if self.update_group(group_uuid, group_config):
                            self.stats['updated'] += 1
                        else:
                            self.stats['failed'] += 1
                    else:
                        logger.error(f"  ✗ Could not find UUID for existing group")
                        self.stats['failed'] += 1
                elif self.force:
                    # Force create (will likely fail with 409, but try anyway)
                    if self.create_group(group_config):
                        self.stats['created'] += 1
                    else:
                        self.stats['failed'] += 1
                else:
                    # Skip existing group
                    logger.warning(f"  ⊘ Skipping - group already exists (use --update to modify)")
                    self.stats['skipped'] += 1
            else:
                # Create new group
                if self.create_group(group_config):
                    self.stats['created'] += 1
                else:
                    self.stats['failed'] += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print summary statistics"""
        logger.info(f"\n{'='*60}")
        logger.info("SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total groups in CSV:  {self.stats['total']}")
        logger.info(f"Successfully created: {self.stats['created']}")
        logger.info(f"Successfully updated: {self.stats['updated']}")
        logger.info(f"Skipped (existing):   {self.stats['skipped']}")
        logger.info(f"Failed:               {self.stats['failed']}")
        logger.info(f"{'='*60}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Create or update Turbonomic groups from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (prompt for password)
  python create_groups.py https://turbo.example.com admin groups.csv
  
  # With password as argument
  python create_groups.py https://turbo.example.com admin password123 groups.csv
  
  # Dry run (preview without creating)
  python create_groups.py https://turbo.example.com admin groups.csv --dry-run
  
  # Update existing groups
  python create_groups.py https://turbo.example.com admin groups.csv --update
  
  # Force creation (skip duplicate checking)
  python create_groups.py https://turbo.example.com admin groups.csv --force
  
  # Debug mode
  python create_groups.py https://turbo.example.com admin groups.csv --debug
        """
    )
    
    parser.add_argument('turbo_url', help='Turbonomic instance URL')
    parser.add_argument('username', help='Username for authentication')
    parser.add_argument('password', nargs='?', help='Password for authentication (will prompt if not provided)')
    parser.add_argument('csv_file', help='Path to CSV file with group configurations')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without creating groups')
    parser.add_argument('--update', action='store_true', help='Update existing groups instead of skipping them')
    parser.add_argument('--force', action='store_true', help='Skip duplicate checking (not recommended with --update)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get password if not provided
    password = args.password
    if not password:
        password = getpass.getpass(f"Password for {args.username}: ")
    
    # Create instance and run
    creator = TurbonomicGroupCreator(
        turbo_url=args.turbo_url,
        username=args.username,
        password=password,
        dry_run=args.dry_run,
        force=args.force,
        update_mode=args.update
    )
    
    # Authenticate
    if not creator.authenticate():
        logger.error("Authentication failed. Exiting.")
        sys.exit(1)
    
    # Process groups
    creator.process_groups(args.csv_file)


if __name__ == '__main__':
    main()

# Made with Bob
