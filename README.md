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
- **Cloudability API Key** (see [Getting Your API Key](#getting-your-api-key))
- **Command-line/Terminal access**
- Basic understanding of CSV file formats

## Installation

### 1. Install the Apptio Library

These tools require the [Apptio Tools Library](https://github.com/ibm/apptio-tools-lib). Install it using pip:

```bash
pip install git+https://github.com/ibm/apptio-tools-lib.git
```

### 2. Install Additional Dependencies

Some tools require additional Python packages:

```bash
pip install charset-normalizer requests
```

### 3. Clone This Repository

```bash
git clone https://github.com/IBM/Apptio-Tools.git
cd Apptio-Tools
```

## Getting Your API Key

To use these tools, you'll need a Cloudability API key:

1. Log in to your Cloudability account
2. Navigate to **Person Icon** → **Manage Profile** → **Preferences Tab**
3. Generate a new API key or use an existing one
4. Copy the API key - you'll use it as a command-line argument

**Security Note:** Never commit your API key to version control. Keep it secure and treat it like a password.

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

```bash
cd cloudability/account-group-updater
python update_ag_entries.py <api_key> [-delay <seconds>]
```

**Parameters:**
- `<api_key>` (required): Your Cloudability API key
- `-delay <seconds>` (optional): Delay between API calls to avoid rate limiting (default: 0.5 seconds)

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

```bash
cd cloudability/business-mapping-update
python update_mappings_from_csv.py <api_key> [-test] [-debug]
```

**Parameters:**
- `<api_key>` (required): Your Cloudability API key
- `-test` (optional): Use test mappings instead of CSV files
- `-debug` (optional): Generate JSON files without updating Cloudability

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

```bash
cd cloudability/update-hierarchical-bm
python update_hbm.py <api_key> [-region <region>] [-name <name>]
```

**Parameters:**
- `<api_key>` (required): Your Cloudability API key
- `-region <region>` (optional): Cloudability region (if not default)
- `-name <name>` (optional): Name for the HBM (defaults to CSV filename)

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
- Preserves sharing settings when updating
- Handles all Cloudability filter comparators
- Can process multiple CSV files

#### Usage

```bash
cd cloudability/views-updater
python views_updater.py <api_key> [-region <region>]
```

**Parameters:**
- `<api_key>` (required): Your Cloudability API key
- `-region <region>` (optional): Cloudability region (if not default)

#### CSV Format

**Columns:**
1. **View Name** - Name of the view
2. **Dimension** - The field to filter on
3. **Comparator** - Filter operator (see below)
4. **Value1, Value2, ...** - Values to filter (multiple columns allowed)

**Valid Comparators:**
- `==` : Equals
- `!=` : Not Equals
- `=@` : Contains
- `!=@` : Does Not Contain

**Example CSV:**
```csv
View Name,Dimension,Comparator,Value1,Value2,Value3
Dev Environment,tag1,=@,dev,staging,nonprod
Dev Environment,vendor_identifier,!=,123412341234
Prod Environment,tag1,==,prod,production
Prod Environment,account_identifier,==,123412341234,432143214321
```

This creates:
- **Dev Environment** view with 4 filters
- **Prod Environment** view with 4 filters

#### Important Notes
- Multiple rows with the same view name add filters to that view
- Existing views are updated (not replaced) if filters differ
- Sharing settings are preserved when updating existing views
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

### Common Issues

#### "Missing api key. Quitting"
**Solution:** Ensure you're passing your API key as the first command-line argument:
```bash
python script_name.py YOUR_API_KEY
```

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
