# Configuration Examples

This document provides example configurations for using the Cloudability scripts with different authentication methods.

## Environment Variables File (.env)

Create a `.env` file in your script directory with the following content:

### Option 1: Cloudability API Key

```bash
# Cloudability API Key Authentication
CLOUDABILITY_API_KEY=your_cloudability_api_key_here

# Optional: Specify region if not US
# CLOUDABILITY_REGION=eu
```

### Option 2: Frontdoor Public/Private Keys

```bash
# Frontdoor Authentication
APPTIO_PUBLIC_KEY=your_frontdoor_public_key_here
APPTIO_PRIVATE_KEY=your_frontdoor_private_key_here
APPTIO_DOMAIN=your_domain_name
APPTIO_ENVIRONMENT_NAME=main  # Optional, defaults to "main" if not specified
APPTIO_REGION=  # Leave empty for US, or use: eu, au, me

# Note: Do not commit this file to version control!
# Add .env to your .gitignore file
```

### Loading Environment Variables

#### Automatic Loading (Recommended)

The scripts will automatically load variables from a `.env` file if you have `python-dotenv` installed:

```bash
# Install python-dotenv (one-time setup)
pip install python-dotenv

# Then simply run your script - .env will be loaded automatically
python update_ag_entries.py
```

#### Manual Loading (Alternative)

If you prefer not to install `python-dotenv`, you can manually source the `.env` file:

```bash
# Linux/Mac
source .env
python update_ag_entries.py

# Windows PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
python update_ag_entries.py

# Windows Command Prompt
for /f "tokens=*" %i in (.env) do set %i
python update_ag_entries.py
```

**Note:** The scripts work with system environment variables regardless of whether `python-dotenv` is installed. The `python-dotenv` package simply provides convenience by automatically loading `.env` files.

## Command Line Examples

### Using Cloudability API Key

#### Basic Usage
```bash
python update_ag_entries.py --api-key YOUR_API_KEY
```

#### With Additional Options
```bash
python update_ag_entries.py --api-key YOUR_API_KEY --delay 1.0
```

#### Legacy Format (Still Supported)
```bash
python update_ag_entries.py YOUR_API_KEY
```

### Using Frontdoor Authentication

#### US Region (Default)
```bash
python update_ag_entries.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain-name
```

#### With Custom Environment Name
```bash
python update_ag_entries.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain-name \
  --environment-name production
```

#### EU Region
```bash
python update_ag_entries.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain-name \
  --region eu
```

#### APAC Region with Custom Environment
```bash
python update_ag_entries.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain-name \
  --environment-name custom-env \
  --region au
```

## Script-Specific Examples

### Account Group Updater (update_ag_entries.py)

```bash
# With API Key
python cloudability/account-group-updater/update_ag_entries.py \
  --api-key YOUR_API_KEY \
  --delay 0.5

# With Frontdoor Auth
python cloudability/account-group-updater/update_ag_entries.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain \
  --delay 0.5
```

### Business Mapping Updater (update_mappings_from_csv.py)

```bash
# With API Key
python cloudability/business-mapping-update/update_mappings_from_csv.py \
  --api-key YOUR_API_KEY

# With Frontdoor Auth
python cloudability/business-mapping-update/update_mappings_from_csv.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain

# Debug mode (no changes made)
python cloudability/business-mapping-update/update_mappings_from_csv.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain \
  --debug
```

### Hierarchical Business Mapping Updater (update_hbm.py)

```bash
# With API Key
python cloudability/update-hierarchical-bm/update_hbm.py \
  --api-key YOUR_API_KEY

# With Frontdoor Auth
python cloudability/update-hierarchical-bm/update_hbm.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain

# With specific HBM name
python cloudability/update-hierarchical-bm/update_hbm.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain \
  --name "My HBM Name"
```

### Views Updater (views_updater.py)

```bash
# With API Key
python cloudability/views-updater/views_updater.py \
  --api-key YOUR_API_KEY

# With Frontdoor Auth
python cloudability/views-updater/views_updater.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain

# With region
python cloudability/views-updater/views_updater.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain \
  --region eu
```

## Python Script Examples

### Using in Your Own Scripts

```python
import os
from apptio_lib import cloudability as cldy
from apptio_lib import apptio

# Method 1: Using Cloudability API Key
api_key = os.getenv('CLOUDABILITY_API_KEY')
response = cldy.get('/account_groups', api_key=api_key)

# Method 2: Using Frontdoor Authentication
public_key = os.getenv('APPTIO_PUBLIC_KEY')
private_key = os.getenv('APPTIO_PRIVATE_KEY')
domain = os.getenv('APPTIO_DOMAIN')
environment_name = os.getenv('APPTIO_ENVIRONMENT_NAME', 'main')
region = os.getenv('APPTIO_REGION', '')

# Setup frontdoor authentication
opentoken_headers = apptio.setup_frontdoor_auth(
    public_key=public_key,
    private_key=private_key,
    domain=domain,
    region=region,
    environment_name=environment_name
)

# Make API calls with frontdoor auth
response = cldy.get('/account_groups', opentoken_headers=opentoken_headers)
```

### Complete Authentication Setup Function

```python
import os
import sys
from apptio_lib import apptio

def setup_authentication(args):
    """
    Setup authentication based on provided arguments or environment variables.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        tuple: (api_key, opentoken_headers)
    """
    # Priority 1: Frontdoor keys from command line
    if hasattr(args, 'frontdoor_public') and args.frontdoor_public:
        if not args.frontdoor_private or not args.domain:
            print('Error: --frontdoor-private and --domain are required with --frontdoor-public')
            sys.exit(1)
        
        opentoken_headers = apptio.setup_frontdoor_auth(
            public_key=args.frontdoor_public,
            private_key=args.frontdoor_private,
            domain=args.domain,
            region=getattr(args, 'region', '')
        )
        
        if not opentoken_headers:
            print('Error: Failed to authenticate with frontdoor')
            sys.exit(1)
        
        return (None, opentoken_headers)
    
    # Priority 2: Cloudability API key from command line
    if hasattr(args, 'api_key') and args.api_key:
        return (args.api_key, {})
    
    # Priority 3: Frontdoor keys from environment variables
    public_key = os.getenv('APPTIO_PUBLIC_KEY')
    private_key = os.getenv('APPTIO_PRIVATE_KEY')
    domain = os.getenv('APPTIO_DOMAIN')
    
    if public_key and private_key and domain:
        region = os.getenv('APPTIO_REGION', '')
        opentoken_headers = apptio.setup_frontdoor_auth(
            public_key=public_key,
            private_key=private_key,
            domain=domain,
            region=region
        )
        
        if not opentoken_headers:
            print('Error: Failed to authenticate with frontdoor using environment variables')
            sys.exit(1)
        
        return (None, opentoken_headers)
    
    # Priority 4: Cloudability API key from environment
    api_key = os.getenv('CLOUDABILITY_API_KEY')
    if api_key:
        return (api_key, {})
    
    # No authentication found
    print('Error: No authentication credentials provided')
    print('Please provide either:')
    print('  1. --api-key YOUR_KEY')
    print('  2. --frontdoor-public, --frontdoor-private, and --domain')
    print('  3. Environment variables (CLOUDABILITY_API_KEY or APPTIO_PUBLIC_KEY/PRIVATE_KEY/DOMAIN)')
    sys.exit(1)
```

## Docker/Container Examples

### Dockerfile with Environment Variables

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy scripts
COPY cloudability/ ./cloudability/
COPY apptio_lib/ ./apptio_lib/

# Set environment variables (override at runtime)
ENV APPTIO_PUBLIC_KEY=""
ENV APPTIO_PRIVATE_KEY=""
ENV APPTIO_DOMAIN=""
ENV APPTIO_REGION=""

# Run script
CMD ["python", "cloudability/account-group-updater/update_ag_entries.py"]
```

### Docker Run with Environment Variables

```bash
docker run \
  -e APPTIO_PUBLIC_KEY="your_public_key" \
  -e APPTIO_PRIVATE_KEY="your_private_key" \
  -e APPTIO_DOMAIN="your_domain" \
  -e APPTIO_REGION="eu" \
  -v $(pwd)/data:/app/data \
  cloudability-scripts
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  cloudability-updater:
    build: .
    environment:
      - APPTIO_PUBLIC_KEY=${APPTIO_PUBLIC_KEY}
      - APPTIO_PRIVATE_KEY=${APPTIO_PRIVATE_KEY}
      - APPTIO_DOMAIN=${APPTIO_DOMAIN}
      - APPTIO_REGION=${APPTIO_REGION:-}
    volumes:
      - ./data:/app/data
```

## CI/CD Examples

### GitHub Actions

```yaml
name: Update Cloudability

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run update script
        env:
          APPTIO_PUBLIC_KEY: ${{ secrets.APPTIO_PUBLIC_KEY }}
          APPTIO_PRIVATE_KEY: ${{ secrets.APPTIO_PRIVATE_KEY }}
          APPTIO_DOMAIN: ${{ secrets.APPTIO_DOMAIN }}
          APPTIO_REGION: ${{ secrets.APPTIO_REGION }}
        run: |
          python cloudability/account-group-updater/update_ag_entries.py
```

### GitLab CI

```yaml
update_cloudability:
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - python cloudability/account-group-updater/update_ag_entries.py
  variables:
    APPTIO_PUBLIC_KEY: $APPTIO_PUBLIC_KEY
    APPTIO_PRIVATE_KEY: $APPTIO_PRIVATE_KEY
    APPTIO_DOMAIN: $APPTIO_DOMAIN
    APPTIO_REGION: $APPTIO_REGION
  only:
    - schedules
```

## Security Best Practices

### 1. Never Commit Credentials

Add to `.gitignore`:
```
.env
config.json
*_credentials.txt
*.key
```

### 2. Use Secret Management

```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id cloudability/frontdoor \
  --query SecretString \
  --output text | jq -r '.public_key'

# Azure Key Vault
az keyvault secret show \
  --vault-name my-vault \
  --name apptio-public-key \
  --query value -o tsv

# HashiCorp Vault
vault kv get -field=public_key secret/cloudability
```

### 3. Rotate Keys Regularly

```bash
# Example rotation script
#!/bin/bash
# rotate_keys.sh

# Get new keys from your key management system
NEW_PUBLIC=$(get_new_public_key)
NEW_PRIVATE=$(get_new_private_key)

# Update environment
export APPTIO_PUBLIC_KEY=$NEW_PUBLIC
export APPTIO_PRIVATE_KEY=$NEW_PRIVATE

# Test authentication
python -c "from apptio_lib import apptio; \
  assert apptio.setup_frontdoor_auth('$NEW_PUBLIC', '$NEW_PRIVATE', '$APPTIO_DOMAIN')"

echo "Keys rotated successfully"
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Authorization key and/or token missing"
```bash
# Solution: Ensure credentials are provided
export CLOUDABILITY_API_KEY=your_key
# OR
export APPTIO_PUBLIC_KEY=your_public_key
export APPTIO_PRIVATE_KEY=your_private_key
export APPTIO_DOMAIN=your_domain
```

#### Issue: "Failed to get environment ID"
```bash
# Solution: Check domain name, environment name, and region
# Domain should be just the name, not the full URL
# Correct: --domain my-company
# Incorrect: --domain my-company.apptio.com

# If using a custom environment name (not "main"), specify it:
# --environment-name production
# OR
# export APPTIO_ENVIRONMENT_NAME=production
```

#### Issue: "Request failed: 401 Unauthorized"
```bash
# Solution: Check if keys are expired or deactivated
# Try generating new keys from Apptio platform
```

#### Issue: Region-specific errors
```bash
# Solution: Ensure region matches your Apptio instance
# US: --region "" (or omit)
# EU: --region eu
# APAC: --region au
# Middle East: --region me