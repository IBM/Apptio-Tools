# Apptio-Tools

Collection of Apptio and Cloudability scripts and tools for automating common tasks via API.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting Your API Key](#getting-your-api-key)
- [Tools](#tools)
  - [Account Group Updater](#1-account-group-updater)
  - [Business Mapping Updater](#2-business-mapping-updater)
  - [Hierarchical Business Mapping Updater](#3-hierarchical-business-mapping-updater)
  - [Views Updater](#4-views-updater)
- [Postman Collections](#postman-collections)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)

## Overview

These tools are primarily intended to be examples of the Cloudability and Apptio APIs, but are fully functioning! They're great for ad-hoc usage and we hope you'll use them to create your own integrations and automations.

**What's included:**
- 4 Python automation tools for bulk operations in Cloudability
- Postman collections for API exploration
- Example CSV files for each tool

## Prerequisites

Before using these tools, ensure you have:

- **Python 3.x** installed on your system
- **Authentication credentials** - Choose one:
  - **Cloudability API Key** (see [Getting Your API Key](#getting-your-api-key)), OR
  - **Frontdoor Public/Private Keys** (see [Frontdoor Authentication](#frontdoor-authentication))
- **Command-line/Terminal access**
- Basic understanding of CSV file formats

## Installation

### Quick Start (Recommended)

1. **Clone this repository:**
   ```bash
   git clone https://github.com/IBM/Apptio-Tools.git
   cd Apptio-Tools
   ```

2. **Install all dependencies at once:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your credentials** (optional but recommended):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run any script** - dependencies will be automatically checked!

### Automatic Dependency Checking

**New Feature!** All scripts now automatically check for missing dependencies when you run them.

- ✅ **Detects missing packages** before the script runs
- 📝 **Shows clear installation instructions** with multiple options
- 💡 **Prompts to install** with your permission (never automatic)
- 🪟 **Checks Windows PowerShell policies** (informational only)

**Example output when dependencies are missing:**
```
⚠️  DEPENDENCY CHECK
======================================================================
❌ REQUIRED packages are missing:

  📦 charset-normalizer
     Purpose: Character encoding detection for CSV files
     Used by: Account Group Updater, Views Updater

📝 INSTALLATION OPTIONS:
======================================================================

✅ RECOMMENDED: Install all dependencies at once
   pip install -r requirements.txt

❓ Would you like to install the missing dependencies now? (yes/no):
```

**To skip the check** (not recommended):
```bash
python script_name.py --skip-dependency-check [other arguments]
```

### Manual Installation

If you prefer to install dependencies manually:

**Option 1: Install from requirements.txt**
```bash
pip install -r requirements.txt
```

**Option 2: Install individual packages**
```bash
pip install charset-normalizer requests
pip install git+https://github.com/ibm/apptio-tools-lib.git
```

**Optional but recommended:**
```bash
pip install python-dotenv  # For automatic .env file loading
```

For detailed troubleshooting and advanced setup options, see [DEPENDENCY_SETUP.md](DEPENDENCY_SETUP.md).

## Authentication

These tools support two authentication methods. Choose the one that works best for your organization.

### Option 1: Cloudability API Key

To use Cloudability API key authentication:

1. Log in to your Cloudability account
2. Navigate to **Person Icon** → **Manage Profile** → **Preferences Tab**
3. Generate a new API key or use an existing one
4. Copy the API key - you'll use it as a command-line argument or environment variable

### Option 2: Frontdoor Authentication

To use Frontdoor public/private key authentication:

1. Log in to your Apptio platform
2. Navigate to **Settings** → **API Keys**
3. Generate a new API key pair (public and private keys)
4. Note your domain name and environment name (usually 'main')
5. Optionally note your region (US, EU, APAC, ME)

For detailed setup instructions, see the [IBM Apptio Platform Documentation](https://www.ibm.com/docs/en/apptio-platform/access-administration/saas?topic=apis-authentication-via-api-keys).

### Security Best Practices

- **Never commit credentials to version control**
- Use environment variables for production deployments
- Rotate keys regularly
- Use separate keys for different environments (dev, staging, production)
- Keep credentials secure and treat them like passwords

### Environment Variables (Recommended)

For better security, use environment variables instead of command-line arguments.

#### Option A: Using .env File (Most Convenient)

Create a `.env` file in your script directory:

```bash
# Option 1: Cloudability API Key
CLOUDABILITY_API_KEY=your_api_key

# Option 2: Frontdoor Authentication
APPTIO_PUBLIC_KEY=your_public_key
APPTIO_PRIVATE_KEY=your_private_key
APPTIO_DOMAIN=your_domain
APPTIO_ENVIRONMENT_NAME=main  # Optional, defaults to "main"
APPTIO_REGION=  # Optional: "", "eu", "au", "me"
```

Install `python-dotenv` for automatic loading:
```bash
pip install python-dotenv
```

Then run scripts - the `.env` file will be loaded automatically:
```bash
python update_ag_entries.py
```

#### Option B: System Environment Variables

Set environment variables in your shell:

```bash
# Linux/Mac
export CLOUDABILITY_API_KEY=your_api_key
# OR
export APPTIO_PUBLIC_KEY=your_public_key
export APPTIO_PRIVATE_KEY=your_private_key
export APPTIO_DOMAIN=your_domain

# Windows PowerShell
$env:CLOUDABILITY_API_KEY="your_api_key"
# OR
$env:APPTIO_PUBLIC_KEY="your_public_key"
$env:APPTIO_PRIVATE_KEY="your_private_key"
$env:APPTIO_DOMAIN="your_domain"
```

Then run scripts without passing credentials:
```bash
python update_ag_entries.py
```

**Note:** The scripts work with system environment variables regardless of whether `python-dotenv` is installed. The `python-dotenv` package simply provides convenience by automatically loading `.env` files.

## Tools

### 1. Account Group Updater

**Purpose:** Bulk update Account Group values for cloud accounts based on CSV files.

**Location:** `cloudability/account-group-updater/update_ag_entries.py`

#### Features
- Updates account group assignments from CSV files
- Automatically creates backups before making changes
- Supports multiple CSV files in one run
- Handles AWS account ID formatting (adds hyphens)
- Can delete entries by leaving values blank

#### Usage

**With Cloudability API Key:**
```bash
cd cloudability/account-group-updater
python update_ag_entries.py --api-key YOUR_API_KEY [--delay SECONDS]
```

**With Frontdoor Authentication:**
```bash
cd cloudability/account-group-updater
python update_ag_entries.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain YOUR_DOMAIN \
  [--environment-name ENV_NAME] \
  [--region REGION] \
  [--delay SECONDS]
```

**With Environment Variables:**
```bash
# Set credentials (see Authentication section above)
cd cloudability/account-group-updater
python update_ag_entries.py [--delay SECONDS]
```

**Legacy Format (Still Supported):**
```bash
python update_ag_entries.py YOUR_API_KEY [--delay SECONDS]
```

**Parameters:**
- `--api-key` : Your Cloudability API key
- `--frontdoor-public` : Frontdoor public key
- `--frontdoor-private` : Frontdoor private key
- `--domain` : Your domain name (for frontdoor auth)
- `--environment-name` : Environment name (optional, defaults to "main")
- `--region` : Region ("", "eu", "au", "me" - optional)
- `--delay` : Delay between API calls in seconds (default: 0.5)

#### CSV Format

The CSV file must be in the same directory as the script. The first column should be one of:
- `vendor_account_identifier`
- `account_identifier`
- `Account Number`

Subsequent columns should be Account Group names (must exist in Cloudability).

**Example CSV:**
```csv
vendor_account_identifier,AG_ACCOUNT_OWNER,AG_ENVIRONMENT,AG_COST_CENTER
1234-5678-9012,John Doe,Production,Finance
9876-5432-1098,Jane Smith,Development,Engineering
```

#### Important Notes
- Account Groups must already exist in Cloudability (they won't be created)
- Backup files are automatically created in a `backups/` folder
- Backup files are compatible with this script for easy restoration
- For large numbers of accounts, you may hit rate limits - use the `-delay` parameter
- Empty values in the CSV will delete the corresponding account group entry

#### Example Workflow

1. Create a CSV file with your account group updates
2. Place it in the `cloudability/account-group-updater/` directory
3. Run the script:
   ```bash
   python update_ag_entries.py YOUR_API_KEY
   ```
4. Review the output for success/failure messages
5. Check the `backups/` folder for the backup file

---

### 2. Business Mapping Updater

**Purpose:** Create and update Business Mappings in Cloudability from CSV files.

**Location:** `cloudability/business-mapping-update/update_mappings_from_csv.py`

#### Features
- Creates new business mappings or updates existing ones
- Groups values into single statements automatically
- Supports multiple business mappings per CSV
- Debug mode for testing without making changes
- Detailed error reporting for invalid expressions

#### Usage

**With Cloudability API Key:**
```bash
cd cloudability/business-mapping-update
python update_mappings_from_csv.py --api-key YOUR_API_KEY [--test] [--debug]
```

**With Frontdoor Authentication:**
```bash
cd cloudability/business-mapping-update
python update_mappings_from_csv.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain YOUR_DOMAIN \
  [--test] [--debug]
```

**With Environment Variables:**
```bash
cd cloudability/business-mapping-update
python update_mappings_from_csv.py [--test] [--debug]
```

**Parameters:**
- `--api-key` : Your Cloudability API key
- `--frontdoor-public` : Frontdoor public key
- `--frontdoor-private` : Frontdoor private key
- `--domain` : Your domain name (for frontdoor auth)
- `--test` : Use test mappings instead of CSV files
- `--debug` : Generate JSON files without updating Cloudability

#### CSV Format

The first column is the **match dimension**, and remaining columns are **business mapping names**.

**Match Dimension Format:**
- Tags: `TAG['tag_name']`
- Business Dimensions: `BUSINESS_DIMENSION['dimension_name']`
- Other dimensions: `DIMENSION['dimension_name']`

**Example CSV:**
```csv
TAG['Cost Center'],Mapped Department,Mapped Team
1234,Finance,Team A
4321,HR,Team B
5678,Finance,Team C
```

This creates:
- **Mapped Department** with 2 values (Finance, HR)
- **Mapped Team** with 3 values (Team A, Team B, Team C)

#### Important Notes
- Business mapping names must exactly match names in Cloudability
- Only one match dimension per CSV file
- Values are automatically grouped by the tool
- Read-only mappings will be skipped
- Use `-debug` mode to preview changes before applying

#### Example Workflow

1. Create a CSV with your business mapping rules
2. Place it in the `cloudability/business-mapping-update/` directory
3. Test first with debug mode:
   ```bash
   python update_mappings_from_csv.py YOUR_API_KEY -debug
   ```
4. Review the generated JSON files in `Debug Files/`
5. Run without debug to apply changes:
   ```bash
   python update_mappings_from_csv.py YOUR_API_KEY
   ```

---

### 3. Hierarchical Business Mapping Updater

**Purpose:** Create and update Hierarchical Business Mappings (HBM) in Cloudability.

**Location:** `cloudability/update-hierarchical-bm/update_hbm.py`

#### Features
- Creates or updates hierarchical business mappings
- Uses the same CSV format as Cloudability's UI import
- Supports multiple hierarchy levels
- Automatically finds base business mapping

#### Usage

**With Cloudability API Key:**
```bash
cd cloudability/update-hierarchical-bm
python update_hbm.py --api-key YOUR_API_KEY [--name HBM_NAME]
```

**With Frontdoor Authentication:**
```bash
cd cloudability/update-hierarchical-bm
python update_hbm.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain YOUR_DOMAIN \
  [--name HBM_NAME] \
  [--region REGION]
```

**With Environment Variables:**
```bash
cd cloudability/update-hierarchical-bm
python update_hbm.py [--name HBM_NAME]
```

**Parameters:**
- `--api-key` : Your Cloudability API key
- `--frontdoor-public` : Frontdoor public key
- `--frontdoor-private` : Frontdoor private key
- `--domain` : Your domain name (for frontdoor auth)
- `--name` : Name for the HBM (defaults to CSV filename)
- `--region` : Region ("", "eu", "au", "me")

#### CSV Format

The first column must be the name of an **existing business mapping**. Subsequent columns define the hierarchy levels.

**Example CSV:**
```csv
Application,L2,L3
App-A,Department-X,Team-1
App-B,Department-X,Team-1
App-C,Department-Y,Team-2
App-D,Department-Y,Team-3
```

This creates a 3-level hierarchy:
- **Base:** Application (must exist as a business mapping)
- **Level 2:** L2
- **Level 3:** L3

#### Important Notes
- The base business mapping (first column) must already exist in Cloudability
- CSV filename becomes the HBM name unless `-name` is specified
- Default value for each level is empty string (can be modified in code)
- The tool will update existing HBMs with the same name

#### Example Workflow

1. Ensure your base business mapping exists in Cloudability
2. Create a CSV file named after your desired HBM (e.g., `Cost_Hierarchy.csv`)
3. Place it in the `cloudability/update-hierarchical-bm/` directory
4. Run the script:
   ```bash
   python update_hbm.py YOUR_API_KEY
   ```
5. Verify the hierarchy in Cloudability UI

---

### 4. Views Updater

**Purpose:** Mass create and update views (filters) in Cloudability.

**Location:** `cloudability/views-updater/views_updater.py`

#### Features
- Creates new views or updates existing ones
- Supports multiple filters per view
- Configure organization sharing for new views
- Preserves sharing settings when updating existing views
- Handles all Cloudability filter comparators
- Can process multiple CSV files

#### Usage

**With Cloudability API Key:**
```bash
cd cloudability/views-updater
python views_updater.py --api-key YOUR_API_KEY [--region REGION]
```

**With Frontdoor Authentication:**
```bash
cd cloudability/views-updater
python views_updater.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain YOUR_DOMAIN \
  [--region REGION]
```

**With Environment Variables:**
```bash
cd cloudability/views-updater
python views_updater.py
```

**Parameters:**
- `--api-key` : Your Cloudability API key
- `--frontdoor-public` : Frontdoor public key
- `--frontdoor-private` : Frontdoor private key
- `--domain` : Your domain name (for frontdoor auth)
- `--region` : Region ("", "eu", "au", "me")

#### CSV Format

**Columns:**
1. **View Name** - Name of the view
2. **Shared With Org** - Share with organization: `true` or `false` (for new views only)
3. **Dimension** - The field to filter on (must use API names for Business Dimensions and Account Groups)
4. **Comparator** - Filter operator (see below)
5. **Value1, Value2, ...** - Values to filter (multiple columns allowed)

**⚠️ IMPORTANT: Use API Names for Dimensions**

When specifying dimensions in the CSV, you must use API names:
- **Business Dimensions**: Use `categoryX` format (e.g., `category1`, `category10`, `category15`)
- **Account Groups**: Use `group_nameX` format (e.g., `group_name1`, `group_name5`)
- **Tags**: Use the API name which is `tagX` where 'X' is the tag dimension index number from the Tags & Labels screen in CLDY (e.g., `tag1`, `tag2`, `tag3`, etc.)

- **Standard dimensions**: Use API names (e.g., `vendor_account_identifier`, `account_identifier`)

**Valid Comparators:**
- `==` : Equals
- `!=` : Not Equals
- `=@` : Contains
- `!=@` : Does Not Contain

**Example CSV:**
```csv
View Name,Shared With Org,Dimension,Comparator,Value1,Value2,Value3
Dev Environment,true,tag1,=@,dev,staging,nonprod
Dev Environment,true,vendor_identifier,!=,123412341234
Prod Environment,false,category10,==,prod,production
Prod Environment,false,group_name5,==,enterprise tenants,MCP
```

This creates:
- **Dev Environment** view (shared with organization) with 4 filters
- **Prod Environment** view (not shared) with 4 filters

#### Important Notes
- Multiple rows with the same view name add filters to that view
- **Shared With Org** only applies when creating NEW views
  - Accepts: `true`, `false` (case-insensitive)
  - If multiple rows for same view have different values, the LAST row's value is used
- Existing views preserve their current sharing settings (CSV value is ignored)
- Existing views are updated (not replaced) if filters differ
- It's easier to use multiple rows than putting all values in one row

#### Example Workflow

1. Create a CSV with your view definitions
2. Place it in the `cloudability/views-updater/` directory
3. Run the script:
   ```bash
   python views_updater.py YOUR_API_KEY
   ```
4. Check Cloudability UI to verify views were created/updated

---

## Postman Collections

**Location:** `cloudability/postman-collection/`

The repository includes Postman collections for exploring the Cloudability API:

- `Cloudability.postman_collection.json.example` - Main API collection
- `Business Metrics.postman_collection.json` - Business metrics endpoints

### Setup

1. Rename `Cloudability.postman_collection.json.example` to `Cloudability.postman_collection.json`
2. Import the collection into Postman
3. Configure your API key in the collection variables
4. Start making API calls!

See the [Postman Collection README](cloudability/postman-collection/README.md) for more details.

---

## Troubleshooting

### Dependency Issues

For detailed dependency troubleshooting, see [DEPENDENCY_SETUP.md](DEPENDENCY_SETUP.md).

**Quick fixes:**

#### "No module named 'apptio_lib'" or other import errors
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

Or let the script's automatic dependency checker guide you through installation.

#### "pip: command not found"
**Solution:** Use python -m pip:
```bash
python -m pip install -r requirements.txt
```

#### Windows PowerShell execution policy errors
**Solution:** Either:
1. Run in Command Prompt (cmd.exe) instead of PowerShell
2. Update policy (as Administrator):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Common Issues

#### "No authentication credentials provided"
**Solution:** Provide authentication using one of these methods:
```bash
# Option 1: Cloudability API Key
python script_name.py --api-key YOUR_API_KEY

# Option 2: Frontdoor Authentication
python script_name.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain YOUR_DOMAIN

# Option 3: Environment Variables
export CLOUDABILITY_API_KEY=your_key
# OR
export APPTIO_PUBLIC_KEY=your_public_key
export APPTIO_PRIVATE_KEY=your_private_key
export APPTIO_DOMAIN=your_domain
python script_name.py
```

#### "Failed to get environment ID"
**Solution:**
- Verify your domain name is correct (just the name, not the full URL)
- Check if you need a custom environment name: `--environment-name production`
- Verify the region matches your Apptio instance: `--region eu`
- Ensure your frontdoor keys have the necessary permissions

#### "Failed to obtain authentication token"
**Solution:**
- Verify your frontdoor public and private keys are correct
- Check if the keys have been deactivated in the Apptio platform
- Ensure you're using the correct region

#### "No csv files found in current directory"
**Solution:** 
- Ensure your CSV file is in the same directory as the script
- Check that the file has a `.csv` extension
- Make sure the file doesn't start with a dot (`.`)

#### Rate Limiting (429 errors)
**Solution:** 
- For Account Group Updater, increase the delay: `python update_ag_entries.py YOUR_API_KEY -delay 1.0`
- Run the script multiple times if it fails partway through
- Process smaller batches of data

#### "Account Groups not found"
**Solution:**
- Verify the account group names in your CSV exactly match those in Cloudability
- Check for extra spaces or typos
- The script will list all valid account groups when this error occurs

#### "Account not found in account mapping"
**Solution:** 
- Verify the account identifier exists in Cloudability
- For AWS accounts, ensure the format matches (with or without hyphens)
- Check that the account is active and not archived

#### CSV Encoding Issues
**Solution:** 
- Save your CSV as UTF-8 encoding
- The tools use `charset-normalizer` to detect encoding automatically
- If issues persist, try opening and re-saving the CSV in a text editor with UTF-8 encoding

#### Business Mapping Expression Errors
**Solution:** 
- Use `-debug` mode to see the generated JSON before applying
- Check for special characters in values (especially single quotes)
- Ensure match dimension format is correct: `TAG['name']` or `DIMENSION['name']`
- The tool will show the exact location of syntax errors

---

## Best Practices

### Before Running Scripts

1. **Test with Small Datasets First**
   - Start with a CSV containing just a few rows
   - Verify the results before processing larger datasets

2. **Backup Your Data**
   - The Account Group Updater creates automatic backups
   - For other tools, export current configurations from Cloudability UI first

3. **Use Debug Mode**
   - Business Mapping Updater supports `-debug` flag
   - Review generated JSON files before applying changes

4. **Validate CSV Format**
   - Check column headers match requirements exactly
   - Ensure no extra spaces or special characters
   - Use UTF-8 encoding

### During Execution

1. **Monitor Output**
   - Scripts provide detailed logging
   - Watch for error messages or warnings
   - Note which items were skipped or failed

2. **Handle Rate Limits**
   - Use delay parameters when available
   - Be prepared to re-run scripts if they timeout
   - Process data in smaller batches for large datasets

### After Running Scripts

1. **Verify in Cloudability UI**
   - Check that changes were applied correctly
   - Verify views, mappings, or account groups as expected

2. **Keep Backup Files**
   - Store backup CSVs in a safe location
   - Document what changes were made and when

3. **Review Logs**
   - Save script output for troubleshooting
   - Note any accounts or items that were skipped

---

## Contributing

We very much welcome contributions! While we can't promise that we'll use everything you might want to share, we're quite eager to see what the Apptio / Cloudability community is cooking up.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more detailed guidelines.

---

## Disclaimer

These tools are provided as-is and are primarily intended to be used as examples for your own integrations. IBM Apptio does not provide direct support for this library, but do feel free to report bugs by [opening an issue](https://github.com/IBM/Apptio-Tools-1/issues).

**Important:**
- Always test in a non-production environment first
- Review all changes before applying to production
- Keep backups of your data
- Use at your own risk

---

## Additional Resources

- [Apptio Tools Library](https://github.com/ibm/apptio-tools-lib) - Required Python library
- [Cloudability API Documentation](https://developers.cloudability.com/) - Official API docs
- [IBM Apptio Support](https://www.ibm.com/products/apptio) - Product information

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/IBM/Apptio-Tools-1/issues) or check existing issues for solutions.
