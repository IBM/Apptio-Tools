"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

Authentication Helper Module for Cloudability Scripts

This module provides a unified authentication interface that supports both:
1. Cloudability API Key authentication
2. Frontdoor public/private key authentication

Usage:
    from auth_helper import setup_authentication, add_auth_arguments
    
    # In your script's main():
    parser = argparse.ArgumentParser()
    add_auth_arguments(parser)
    args = parser.parse_args()
    
    api_key, opentoken_headers = setup_authentication(args)
    
    # Then use in API calls:
    response = cldy.get('/endpoint', api_key=api_key, opentoken_headers=opentoken_headers)
"""

import os
import sys
import argparse
from apptio_lib import apptio

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory
except ImportError:
    # python-dotenv not installed, will use system environment variables only
    pass


def add_auth_arguments(parser):
    """
    Add authentication arguments to an ArgumentParser.
    
    Args:
        parser (argparse.ArgumentParser): The parser to add arguments to
    
    Returns:
        argparse.ArgumentParser: The parser with authentication arguments added
    """
    auth_group = parser.add_argument_group(
        'authentication',
        'Choose one authentication method'
    )
    
    # Cloudability API Key
    auth_group.add_argument(
        '--api-key',
        dest='api_key',
        help='Cloudability API key (can also use CLOUDABILITY_API_KEY env var)'
    )
    
    # Frontdoor authentication
    auth_group.add_argument(
        '--frontdoor-public',
        dest='frontdoor_public',
        help='Frontdoor public key (can also use APPTIO_PUBLIC_KEY env var)'
    )
    
    auth_group.add_argument(
        '--frontdoor-private',
        dest='frontdoor_private',
        help='Frontdoor private key (can also use APPTIO_PRIVATE_KEY env var)'
    )
    
    auth_group.add_argument(
        '--domain',
        dest='domain',
        help='Domain name for frontdoor auth (can also use APPTIO_DOMAIN env var)'
    )
    
    auth_group.add_argument(
        '--environment-name',
        dest='environment_name',
        default='main',
        help='Environment name for frontdoor auth (default: "main", can also use APPTIO_ENVIRONMENT_NAME env var)'
    )
    
    auth_group.add_argument(
        '--region',
        dest='region',
        default='',
        help='Region for API calls: "" (US), "eu", "au", "me" (can also use APPTIO_REGION env var)'
    )
    
    return parser


def setup_authentication(args):
    """
    Setup authentication based on provided arguments or environment variables.
    
    Priority order:
    1. Frontdoor keys from command line arguments
    2. Cloudability API key from command line arguments
    3. Frontdoor keys from environment variables
    4. Cloudability API key from environment variables
    5. Legacy positional API key argument (for backward compatibility)
    
    Args:
        args: Parsed command-line arguments (from argparse)
    
    Returns:
        tuple: (api_key, opentoken_headers)
            - api_key (str or None): Cloudability API key if using API key auth
            - opentoken_headers (dict): Headers for frontdoor auth, empty dict if using API key
    
    Exits:
        Exits with code 1 if no valid authentication credentials are found
    """
    
    # Priority 1: Frontdoor keys from command line
    frontdoor_public = getattr(args, 'frontdoor_public', None)
    frontdoor_private = getattr(args, 'frontdoor_private', None)
    domain = getattr(args, 'domain', None)
    environment_name = getattr(args, 'environment_name', 'main')
    region = getattr(args, 'region', '')
    
    if frontdoor_public or frontdoor_private or domain:
        # If any frontdoor arg is provided, all must be provided
        if not frontdoor_public or not frontdoor_private or not domain:
            print('Error: When using frontdoor authentication, all three arguments are required:')
            print('  --frontdoor-public YOUR_PUBLIC_KEY')
            print('  --frontdoor-private YOUR_PRIVATE_KEY')
            print('  --domain YOUR_DOMAIN')
            print('  [--environment-name ENVIRONMENT_NAME]  # optional, defaults to "main"')
            sys.exit(1)
        
        print('Using frontdoor authentication from command line arguments...')
        opentoken_headers = apptio.setup_frontdoor_auth(
            public_key=frontdoor_public,
            private_key=frontdoor_private,
            domain=domain,
            region=region,
            environment_name=environment_name
        )
        
        if not opentoken_headers:
            print('Error: Failed to authenticate with frontdoor')
            sys.exit(1)
        
        print('✓ Frontdoor authentication successful')
        return (None, opentoken_headers)
    
    # Priority 2: Cloudability API key from command line
    api_key = getattr(args, 'api_key', None)
    if api_key:
        print('Using Cloudability API key from command line arguments...')
        return (api_key, {})
    
    # Priority 3: Frontdoor keys from environment variables
    env_public = os.getenv('APPTIO_PUBLIC_KEY')
    env_private = os.getenv('APPTIO_PRIVATE_KEY')
    env_domain = os.getenv('APPTIO_DOMAIN')
    env_environment_name = os.getenv('APPTIO_ENVIRONMENT_NAME', 'main')
    env_region = os.getenv('APPTIO_REGION', region)
    
    if env_public and env_private and env_domain:
        print('Using frontdoor authentication from environment variables...')
        opentoken_headers = apptio.setup_frontdoor_auth(
            public_key=env_public,
            private_key=env_private,
            domain=env_domain,
            region=env_region,
            environment_name=env_environment_name
        )
        
        if not opentoken_headers:
            print('Error: Failed to authenticate with frontdoor using environment variables')
            sys.exit(1)
        
        print('✓ Frontdoor authentication successful')
        return (None, opentoken_headers)
    
    # Priority 4: Cloudability API key from environment
    env_api_key = os.getenv('CLOUDABILITY_API_KEY')
    if env_api_key:
        print('Using Cloudability API key from environment variable...')
        return (env_api_key, {})
    
    # Priority 5: Legacy positional argument (backward compatibility)
    # Check if there's a positional argument that looks like an API key
    if hasattr(args, 'legacy_api_key') and args.legacy_api_key:
        print('Using Cloudability API key from positional argument (legacy format)...')
        return (args.legacy_api_key, {})
    
    # No authentication found
    print('\n' + '='*70)
    print('ERROR: No authentication credentials provided')
    print('='*70)
    print('\nPlease provide authentication using one of these methods:\n')
    print('1. Cloudability API Key (command line):')
    print('   --api-key YOUR_API_KEY\n')
    print('2. Frontdoor Authentication (command line):')
    print('   --frontdoor-public YOUR_PUBLIC_KEY \\')
    print('   --frontdoor-private YOUR_PRIVATE_KEY \\')
    print('   --domain YOUR_DOMAIN \\')
    print('   [--environment-name ENVIRONMENT_NAME] \\  # optional, defaults to "main"')
    print('   [--region REGION]\n')
    print('3. Environment Variables:')
    print('   export CLOUDABILITY_API_KEY=your_key')
    print('   OR')
    print('   export APPTIO_PUBLIC_KEY=your_public_key')
    print('   export APPTIO_PRIVATE_KEY=your_private_key')
    print('   export APPTIO_DOMAIN=your_domain')
    print('   export APPTIO_ENVIRONMENT_NAME=environment_name  # optional, defaults to "main"')
    print('   export APPTIO_REGION=region  # optional: "", "eu", "au", "me"')
    print('\n' + '='*70 + '\n')
    sys.exit(1)


def parse_legacy_args(sys_argv):
    """
    Handle legacy command-line format for backward compatibility.
    
    Old format: python script.py API_KEY [other_args]
    New format: python script.py --api-key API_KEY [other_args]
    
    This function checks if the first argument looks like an API key
    (doesn't start with --) and converts it to the new format.
    
    Args:
        sys_argv (list): sys.argv from the script
    
    Returns:
        list: Modified argv with legacy API key converted to --api-key format
    """
    if len(sys_argv) > 1:
        first_arg = sys_argv[1]
        # If first arg doesn't start with '-' and isn't a known command, treat as legacy API key
        if not first_arg.startswith('-') and first_arg not in ['help', '--help', '-h']:
            # Convert legacy format to new format
            return [sys_argv[0], '--api-key', first_arg] + sys_argv[2:]
    
    return sys_argv


def get_region_from_args(args):
    """
    Get region from args, with fallback to environment variable.
    
    Args:
        args: Parsed arguments
    
    Returns:
        str: Region string (empty string for US, 'eu', 'au', 'me', etc.)
    """
    region = getattr(args, 'region', '')
    if not region:
        region = os.getenv('APPTIO_REGION', '')
    return region

# Made with Bob
