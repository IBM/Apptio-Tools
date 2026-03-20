# Turbonomic Group Creator

Automate the creation and updating of dynamic groups in Turbonomic using CSV file input. This script supports multiple entity types, flexible filtering criteria, and multiple criteria per group based on the official Turbonomic API v3.

## Features

- ✅ **Dynamic Group Creation** - Create groups with regex patterns and tag-based filtering
- ✅ **Group Updates** - Update existing groups with new criteria
- ✅ **Multiple Criteria** - Support multiple filter criteria per group with AND/OR logic
- ✅ **Multiple Entity Types** - Support for VMs, Physical Machines, Namespaces, Pods, and more
- ✅ **CSV-Based Configuration** - Easy-to-manage group definitions in CSV format
- ✅ **Secure Password Input** - Prompt for password to avoid exposing credentials
- ✅ **Dry-Run Mode** - Preview changes before creating groups
- ✅ **Duplicate Detection** - Automatically skip existing groups
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **Backup** - Automatic backup of group configurations
- ✅ **Progress Tracking** - Real-time progress and summary statistics

## Requirements

- Python 3.6 or higher
- `requests` library
- `urllib3` library

Install dependencies:
```bash
pip install requests urllib3
```

## Quick Start

1. **Create a CSV file** with your group configurations (see `groups_example.csv`)

2. **Run the script** (will prompt for password):
```bash
python create_groups.py https://your-turbo-instance.com username groups.csv
```

3. **Review the output** to see which groups were created or updated

## CSV File Format

The CSV file must contain the following columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `group_name` | Yes | Display name for the group | "Production VMs" |
| `group_type` | Yes | Entity type | "VirtualMachine" |
| `filter_type` | Yes | Filter to apply | "vmsByName" |
| `exp_type` | No | Comparison operator (auto-selected if empty) | "RXEQ", "EQ", "NEQ", "GT" |
| `exp_val` | Yes | Value or regex pattern | "prod.*" |
| `case_sensitive` | No | Case sensitivity (default: false) | "true", "false" |
| `logical_operator` | No | Logic for multiple criteria (default: AND) | "AND", "OR" |
| `description` | No | Optional description | "All production VMs" |

### Intelligent Expression Type Selection

**NEW in v2.0**: The script now automatically selects the correct `exp_type` based on `filter_type` if you leave it empty:

- **Tag-based filters** (e.g., `vmsByTag`, `namespacesByTag`, `businessAccountByTag`) → Auto-selects `EQ`
- **Name-based filters** (e.g., `vmsByName`, `namespacesByName`) → Auto-selects `RXEQ`
- **Exact match filters** (e.g., `vmsByDC`, `vmsByClusterName`, `vmsByCloudProvider`) → Auto-selects `EQ`
- **Numeric filters** (e.g., `pmsByMem`, `vmsByCPU`) → You must specify `GT`, `LT`, `GTE`, or `LTE`

**Recommendation**: Leave `exp_type` empty in your CSV to use intelligent auto-selection. Only specify it when you need a specific comparison operator.

### Multiple Criteria Per Group

To create a group with multiple filter criteria, use **multiple rows with the same `group_name`**. Each row adds another criterion to the group.

- Use `logical_operator` set to `AND` to require all criteria to match (default)
- Use `logical_operator` set to `OR` to match any criterion

### Example CSV

```csv
group_name,group_type,filter_type,exp_type,exp_val,case_sensitive,logical_operator,description
Production VMs,VirtualMachine,vmsByName,,prod.*,false,AND,All VMs starting with prod (auto RXEQ)
High Criticality,VirtualMachine,vmsByTag,,criticality=high,false,AND,High criticality VMs (auto EQ)
Dev Namespaces,Namespace,namespacesByTag,,environment=dev,false,AND,Development namespaces (auto EQ)
High Memory PMs,PhysicalMachine,pmsByMem,GT,64,false,AND,PMs with >64GB RAM (must specify GT)
Azure VMs,VirtualMachine,vmsByCloudProvider,,AZURE,false,AND,Azure VMs (auto EQ)
Production AWS VMs,VirtualMachine,vmsByName,,prod.*,false,AND,Production VMs on AWS (auto RXEQ)
Production AWS VMs,VirtualMachine,vmsByTag,,cloud=aws,false,AND,Production VMs on AWS (auto EQ)
Dev or Test VMs,VirtualMachine,vmsByName,,dev.*,false,OR,Development or test VMs (auto RXEQ)
Dev or Test VMs,VirtualMachine,vmsByName,,test.*,false,OR,Development or test VMs (auto RXEQ)
```

**Notes**:
- Leave `exp_type` empty to use intelligent auto-selection
- "Production AWS VMs" has two criteria (name AND tag)
- "Dev or Test VMs" matches either dev OR test names
- Numeric comparisons (like `pmsByMem`) require explicit `exp_type` (GT, LT, etc.)

## Supported Entity Types

- `VirtualMachine` - Virtual machines
- `PhysicalMachine` - Physical servers
- `Namespace` - Kubernetes namespaces
- `ContainerPod` - Kubernetes pods
- `WorkloadController` - Kubernetes controllers
- `ApplicationComponent` - Application components
- `VirtualVolume` - Virtual volumes
- `Storage` - Storage systems
- `DataStore` - Datastores
- `DataCenter` - Datacenters
- `Cluster` - Clusters
- `Network` - Networks

## Filter Types by Entity

### VirtualMachine Filters
- `vmsByName` - Filter by VM name (regex)
- `vmsByTag` - Filter by tag (format: "key=value")
- `vmsByPMName` - Filter by physical machine name
- `vmsByStorage` - Filter by storage name
- `vmsByNetwork` - Filter by network name
- `vmsByDC` - Filter by datacenter
- `vmsByClusterName` - Filter by cluster name
- `vmsByState` - Filter by VM state
- And many more...

### PhysicalMachine Filters
- `pmsByName` - Filter by PM name (regex)
- `pmsByStorage` - Filter by storage name
- `pmsByNetwork` - Filter by network name
- `pmsByDC` - Filter by datacenter
- `pmsByMem` - Filter by memory (numeric)
- `pmsByNumVms` - Filter by number of VMs

### Namespace Filters
- `namespacesByName` - Filter by namespace name (regex)
- `namespacesByTag` - Filter by tag (format: "key=value")
- `namespacesByCluster` - Filter by cluster name

## Expression Types

The script intelligently auto-selects the correct expression type based on filter type. You can override by specifying `exp_type`:

- `RXEQ` - Regex Equals (auto-selected for name-based filters)
- `EQ` - Exact Equals (auto-selected for tag and exact match filters)
- `NEQ` - Not Equals
- `RXNEQ` - Regex Not Equals
- `GT` - Greater Than (required for numeric comparisons)
- `LT` - Less Than (required for numeric comparisons)
- `GTE` - Greater Than or Equal (required for numeric comparisons)
- `LTE` - Less Than or Equal (required for numeric comparisons)

**Auto-Selection Rules**:
- **Tag filters** (`vmsByTag`, `namespacesByTag`, etc.) → `EQ`
- **Name filters** (`vmsByName`, `namespacesByName`, etc.) → `RXEQ`
- **Exact match filters** (`vmsByDC`, `vmsByClusterName`, `vmsByCloudProvider`, etc.) → `EQ`
- **Numeric filters** (`pmsByMem`, `vmsByCPU`, etc.) → Must specify GT/LT/GTE/LTE

**Recommendation**: Leave `exp_type` empty in CSV to use auto-selection. This prevents common errors like using RXEQ for tag filters.

## Usage Examples

### Basic Usage (Secure - Prompts for Password)
```bash
python create_groups.py https://turbo.example.com admin groups.csv
```

### With Password as Argument (Less Secure)
```bash
python create_groups.py https://turbo.example.com admin password123 groups.csv
```

### Dry Run (Preview Only)
Preview what would be created without making changes:
```bash
python create_groups.py https://turbo.example.com admin groups.csv --dry-run
```

### Update Existing Groups
Update existing groups with new criteria instead of skipping them:
```bash
python create_groups.py https://turbo.example.com admin groups.csv --update
```

### Force Creation
Skip duplicate checking and attempt to create all groups:
```bash
python create_groups.py https://turbo.example.com admin groups.csv --force
```

### Debug Mode
Enable detailed debug logging:
```bash
python create_groups.py https://turbo.example.com admin groups.csv --debug
```

### Combined Options
```bash
python create_groups.py https://turbo.example.com admin groups.csv --update --dry-run --debug
```

## Command-Line Arguments

```
positional arguments:
  turbo_url             Turbonomic instance URL
  username              Username for authentication
  password              Password for authentication (optional - will prompt if not provided)
  csv_file              Path to CSV file with group configurations

optional arguments:
  -h, --help            Show help message and exit
  --dry-run             Preview changes without creating groups
  --update              Update existing groups instead of skipping them
  --force               Skip duplicate checking (not recommended with --update)
  --debug               Enable debug logging
```

## Output

The script provides detailed output including:

- Authentication status
- Number of groups parsed from CSV
- Number of criteria across all groups
- Progress for each group creation/update
- Summary statistics:
  - Total groups in CSV
  - Successfully created
  - Successfully updated
  - Skipped (already exist)
  - Failed

### Example Output

```
2026-03-06 17:00:00 - INFO - Authenticating to https://turbo.example.com...
2026-03-06 17:00:01 - INFO - Authentication successful
2026-03-06 17:00:01 - INFO - Parsed 14 groups from CSV file
2026-03-06 17:00:01 - INFO - Backup saved to: backups/groups_backup_1709755201.json
2026-03-06 17:00:01 - INFO - Found 5 existing user groups
2026-03-06 17:00:01 - INFO - 
============================================================
2026-03-06 17:00:01 - INFO - Processing 14 groups...
2026-03-06 17:00:01 - INFO - 
============================================================

2026-03-06 17:00:01 - INFO - [1/14] Processing: Production VMs
2026-03-06 17:00:02 - INFO - ✓ Created group: Production VMs
2026-03-06 17:00:03 - INFO - [2/14] Processing: Development VMs
2026-03-06 17:00:03 - INFO - ✓ Created group: Development VMs
...

2026-03-06 17:00:20 - INFO -
============================================================
2026-03-06 17:00:20 - INFO - SUMMARY
2026-03-06 17:00:20 - INFO - ============================================================
2026-03-06 17:00:20 - INFO - Total groups in CSV:  14
2026-03-06 17:00:20 - INFO - Successfully created: 10
2026-03-06 17:00:20 - INFO - Successfully updated: 2
2026-03-06 17:00:20 - INFO - Skipped (existing):   2
2026-03-06 17:00:20 - INFO - Failed:               0
2026-03-06 17:00:20 - INFO - ============================================================
```

## Backup Files

The script automatically creates a backup of all group configurations before processing:

- Location: `backups/groups_backup_<timestamp>.json`
- Format: JSON
- Contains: All group configurations from the CSV

## Error Handling

The script handles various error scenarios:

- **Authentication failures** - Invalid credentials
- **Network errors** - Connection timeouts, DNS issues
- **Invalid CSV format** - Missing required columns
- **Duplicate groups** - Groups that already exist
- **API errors** - Rate limiting, server errors
- **Invalid configurations** - Malformed regex, invalid entity types

## Tips and Best Practices

1. **Test with Dry Run** - Always use `--dry-run` first to preview changes
2. **Secure Password Input** - Omit password from command line to be prompted securely
3. **Start Small** - Test with a few groups before creating many
4. **Use Descriptive Names** - Make group names clear and meaningful
5. **Multiple Criteria** - Use multiple rows with the same group_name for complex filtering
6. **Update Mode** - Use `--update` to modify existing groups with new criteria
7. **Document Filters** - Use the description column to explain complex filters
8. **Backup Regularly** - Keep copies of your CSV files
9. **Check Logs** - Review the output for any warnings or errors
10. **Regex Testing** - Test regex patterns before using them in production

## Regex Pattern Examples

### VM Name Patterns
- `prod.*` - Starts with "prod"
- `.*-prod` - Ends with "-prod"
- `.*test.*` - Contains "test"
- `vm-[0-9]+` - Matches "vm-" followed by numbers
- `(dev|test|qa).*` - Starts with dev, test, or qa

### Tag Patterns
- `environment=production` - Exact tag match
- `team=.*` - Any value for team tag
- `cost-center=12345` - Specific cost center

## Troubleshooting

### Authentication Fails
- Verify the Turbonomic URL is correct
- Check username and password
- Ensure the user has permissions to create groups

### Groups Not Created
- Check the CSV format matches the required columns
- Verify entity types and filter types are valid
- Review the error messages in the output

### SSL Certificate Errors
- The script disables SSL verification for self-signed certificates
- For production, consider using valid SSL certificates

### Rate Limiting
- The script includes a 0.5-second delay between requests
- If you encounter rate limiting, the script will log the error

## API Reference

This script uses the Turbonomic REST API v3:

- **Authentication**: `POST /api/v3/login`
- **Create Group**: `POST /api/v3/groups/`
- **List Groups**: `GET /api/v3/groups`

For more information, see the [Turbonomic API Documentation](https://www.ibm.com/docs/en/tarm/8.19.1?topic=documentation-api-reference).

## License

Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Turbonomic API documentation
3. Check the script logs for detailed error messages

## Version History

- **v2.0** - Enhanced functionality
  - **Secure password input** - Prompts for password instead of requiring it as argument
  - **Update existing groups** - New `--update` flag to modify existing groups
  - **Multiple criteria per group** - Support multiple filter criteria with AND/OR logic
  - Improved CSV parsing to group criteria by group name
  - Enhanced documentation with multiple criteria examples

- **v1.0** - Initial release
  - Dynamic group creation from CSV
  - Support for multiple entity types
  - Dry-run mode
  - Duplicate detection
  - Comprehensive error handling