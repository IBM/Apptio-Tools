# Changelog - Turbonomic Group Creator

## [2.0.0] - 2026-03-16

### 🚀 Major Feature Release

**Three Major Enhancements**: Secure password input, group updates, and multiple criteria support.

#### New Features

1. **Secure Password Input**
   - Password is now optional as command-line argument
   - Script prompts securely using `getpass` if password not provided
   - Prevents password exposure in command history or process lists
   - Supports special characters and non-alphanumeric passwords

2. **Update Existing Groups**
   - New `--update` flag to modify existing groups
   - Uses PUT API to update group criteria
   - Allows changing filters without recreating groups
   - Maintains group UUID and other properties

3. **Multiple Criteria Per Group**
   - Support multiple filter criteria per group
   - Use multiple CSV rows with same `group_name`
   - New `logical_operator` column (AND/OR)
   - Enables complex filtering scenarios

#### Changes Made

**Script Changes:**
```python
# Added imports
import getpass
from collections import defaultdict

# New parameters
update_mode: bool = False  # Enable group updates

# New methods
update_group()  # PUT existing group
parse_csv()     # Enhanced to group criteria by name

# Enhanced statistics
'updated': 0    # Track updated groups
```

**CSV Format Changes:**
- Added `logical_operator` column (optional, defaults to AND)
- Multiple rows with same `group_name` create multi-criteria groups
- Each row adds one criterion to the group

**API Changes:**
- Added PUT `/api/v3/groups/{uuid}` for updates
- Enhanced group configuration with multiple criteria support

#### Files Modified
- `create_groups.py` - Core script with all three enhancements
- `groups_example.csv` - Added multiple criteria examples
- `README.md` - Comprehensive documentation updates
- `CHANGELOG.md` - This entry

#### Migration Guide

**Old Usage (v1.x):**
```bash
python create_groups.py https://turbo user password123 groups.csv
```

**New Usage (v2.0 - Recommended):**
```bash
# Secure - prompts for password
python create_groups.py https://turbo user groups.csv

# Update existing groups
python create_groups.py https://turbo user groups.csv --update
```

**CSV Format - Single Criterion (Compatible with v1.x):**
```csv
group_name,group_type,filter_type,exp_type,exp_val,case_sensitive,logical_operator
Production VMs,VirtualMachine,vmsByName,RXEQ,prod.*,false,AND
```

**CSV Format - Multiple Criteria (New in v2.0):**
```csv
group_name,group_type,filter_type,exp_type,exp_val,case_sensitive,logical_operator
Production AWS VMs,VirtualMachine,vmsByName,RXEQ,prod.*,false,AND
Production AWS VMs,VirtualMachine,vmsByTag,RXEQ,cloud=aws,false,AND
Dev or Test VMs,VirtualMachine,vmsByName,RXEQ,dev.*,false,OR
Dev or Test VMs,VirtualMachine,vmsByName,RXEQ,test.*,false,OR
```

#### Use Cases

**Use Case 1: Secure Password Input**
```bash
# Password not exposed in history
python create_groups.py https://turbo.example.com admin groups.csv
Password for admin: ********
```


### 🔧 Critical Fix - Intelligent Expression Type Selection

**Issue Discovered**: Not all filter types use regex (RXEQ). Tag-based filters and exact match filters require EQ instead.

**Root Cause Analysis**:
From production testing and API documentation:
- Tag filters (`vmsByTag`, `namespacesByTag`, `businessAccountByTag`) use `EQ` for exact tag matching
- Name filters (`vmsByName`, `namespacesByName`) use `RXEQ` for regex pattern matching
- Exact match filters (`vmsByDC`, `vmsByClusterName`, `vmsByCloudProvider`) use `EQ`
- Using RXEQ for tag filters causes groups to be created but with zero members

**Solution Implemented**:
Added intelligent auto-selection of `exp_type` based on `filter_type`:

```python
# Filter types that use EQ (exact match) instead of RXEQ (regex)
EQ_FILTER_TYPES = {
    # Tag-based filters
    'vmsByTag', 'namespacesByTag', 'podsByTag', 'businessAccountByTag',
    # Exact match filters
    'vmsByCloudProvider', 'vmsByState', 'vmsByDC', 'vmsByClusterName',
    # And more...
}
```

**Usage**:
- Leave `exp_type` column empty in CSV → Script auto-selects correct type
- Specify `exp_type` explicitly → Script uses your value (for overrides)

**Example**:
```csv
# Auto-selection (recommended)
Azure VMs,VirtualMachine,vmsByCloudProvider,,AZURE,false,AND
Dev VMs,VirtualMachine,vmsByTag,,environment=dev,false,AND
Prod VMs,VirtualMachine,vmsByName,,prod.*,false,AND

# Results in:
# Azure VMs → EQ (auto-selected)
# Dev VMs → EQ (auto-selected)  
# Prod VMs → RXEQ (auto-selected)
```

**Impact**:
- ✅ Tag-based groups now populate with members correctly
- ✅ No need to remember which filters use EQ vs RXEQ
- ✅ Backward compatible - explicit exp_type still works
- ✅ Reduces user error and improves success rate

**Use Case 2: Update Existing Groups**
```bash
# Modify criteria for existing groups
python create_groups.py https://turbo.example.com admin groups.csv --update
```

**Use Case 3: Complex Filtering**
```csv
# VMs that are BOTH production AND in AWS
Prod AWS VMs,VirtualMachine,vmsByName,RXEQ,prod.*,false,AND
Prod AWS VMs,VirtualMachine,vmsByTag,RXEQ,cloud=aws,false,AND

# VMs that are EITHER dev OR test
Dev/Test VMs,VirtualMachine,vmsByName,RXEQ,dev.*,false,OR
Dev/Test VMs,VirtualMachine,vmsByName,RXEQ,test.*,false,OR
```

#### Testing

Tested with production Turbonomic instance:
- ✅ Password prompting works with special characters
- ✅ Groups update successfully with new criteria
- ✅ Multiple criteria groups populate correctly
- ✅ AND logic requires all criteria to match
- ✅ OR logic matches any criterion
- ✅ Backward compatible with v1.x CSV format

#### Breaking Changes

None - fully backward compatible with v1.x:
- Old CSV format still works (single criterion per group)
- Password can still be provided as argument
- Existing groups are skipped by default (use --update to modify)

---

## [1.1.0] - 2026-03-16

### 🐛 Fixed - Groups Now Populate with Members

**Critical Fix**: Groups created by the script now correctly populate with members.

#### Root Cause
The script was missing required API fields that Turbonomic uses to evaluate group membership criteria. While groups were created successfully, they appeared empty because the API couldn't properly process the filter criteria.

#### Changes Made

1. **Added Required Fields to Group Configuration**
   ```python
   'className': 'Group',           # NEW: Identifies object type
   'logicalOperator': 'AND',       # NEW: Criteria combination logic
   ```

2. **Added Required Fields to Criteria List**
   ```python
   'entityType': None,             # NEW: Entity type filter
   'singleLine': False             # NEW: Display format flag
   ```

3. **Changed Default Expression Type**
   - **Before**: `EQ` (Equals)
   - **After**: `RXEQ` (Regex Equals)
   - **Reason**: Pattern matching requires RXEQ, not EQ

4. **Fixed Field Ordering in criteriaList**
   - **Before**: filterType, expType, expVal, caseSensitive
   - **After**: expVal, expType, filterType, caseSensitive, entityType, singleLine
   - **Reason**: Matches Turbonomic's internal structure

5. **Removed Description Field**
   - Removed from root level of group config
   - Not used by Turbonomic API

#### Files Modified
- `create_groups.py` - Core script with fixes
- `groups_example.csv` - Updated to use RXEQ for patterns
- `README.md` - Updated expression types documentation
- `TROUBLESHOOTING.md` - NEW: Comprehensive troubleshooting guide
- `CHANGELOG.md` - NEW: This file

#### Migration Guide

If you have existing CSV files, update them:

**Old CSV (won't populate members):**
```csv
group_name,group_type,filter_type,exp_type,exp_val
Prod VMs,VirtualMachine,vmsByName,EQ,prod.*
```

**New CSV (will populate members):**
```csv
group_name,group_type,filter_type,exp_type,exp_val
Prod VMs,VirtualMachine,vmsByName,RXEQ,prod.*
```

**Key Changes:**
- Use `RXEQ` for pattern matching (regex)
- Use `EQ` only for exact string matches
- Leave `exp_type` empty to default to `RXEQ`

#### Testing

Tested with production Turbonomic instance:
- ✅ Groups created successfully
- ✅ Members populated correctly
- ✅ Filters working as expected
- ✅ Regex patterns matching properly

#### Expression Type Reference

| Type | Use For | Example |
|------|---------|---------|
| `RXEQ` | Regex patterns (default) | `prod.*`, `.*test.*` |
| `EQ` | Exact matches | `Dallas`, `Cluster01` |
| `GT` | Greater than (numeric) | `64` (memory) |
| `LT` | Less than (numeric) | `100` |

---

## [1.0.0] - 2026-03-06

### 🎉 Initial Release

#### Features
- ✅ CSV-based group creation
- ✅ Multiple entity type support
- ✅ Dynamic group creation with filters
- ✅ Authentication with Turbonomic API
- ✅ Dry-run mode for testing
- ✅ Duplicate detection
- ✅ Automatic backups
- ✅ Progress tracking
- ✅ Comprehensive error handling
- ✅ Debug logging

#### Known Issues
- ❌ Groups created but no members found (Fixed in v1.1.0)

#### Files Included
- `create_groups.py` - Main script
- `groups_example.csv` - Example CSV
- `README.md` - Documentation
- `PLAN.md` - Planning document
- `test_csv_parsing.py` - Test utility

---

## Upgrade Instructions

### From v1.0.0 to v1.1.0

1. **Backup your current CSV files**
   ```bash
   cp groups.csv groups.csv.backup
   ```

2. **Update the script**
   ```bash
   # Pull latest version or replace create_groups.py
   ```

3. **Update your CSV files**
   - Change `EQ` to `RXEQ` for pattern-based filters
   - Keep `EQ` for exact matches only
   - Or leave `exp_type` column empty to use default `RXEQ`

4. **Test with dry-run**
   ```bash
   python create_groups.py https://turbo user pass groups.csv --dry-run
   ```

5. **Delete old empty groups** (optional)
   - Remove groups created with v1.0.0 that have no members
   - Or let the script skip them with duplicate detection

6. **Create new groups**
   ```bash
   python create_groups.py https://turbo user pass groups.csv
   ```

### Verification

After upgrade, verify groups have members:
1. Check group member count in Turbonomic UI
2. Or use API: `GET /api/v3/groups/{groupId}`
3. Look for `membersCount` > 0

---

## Support

For issues or questions:
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [README.md](README.md)
- Check Turbonomic API docs: https://www.ibm.com/docs/en/tarm/8.19.1

## Contributing

Found a bug or have a feature request? Please document:
1. Turbonomic version
2. Script version
3. CSV example (sanitized)
4. Error messages
5. Expected vs actual behavior