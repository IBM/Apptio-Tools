# Troubleshooting Guide - Turbonomic Group Creator

## Issue: Groups Created But No Members Found

### Problem
Groups are created successfully via the script, but they show 0 members even though manually created groups with the same filters work correctly.

### Root Cause
The script was missing required fields and using incorrect expression types that Turbonomic needs to properly evaluate group membership.

### Solution (Fixed in Latest Version)
The script now includes all required fields that match Turbonomic's internal group structure:

#### Required Fields Added:
1. **`className: "Group"`** - Identifies the object type
2. **`logicalOperator: "AND"`** - How multiple criteria are combined
3. **`entityType: null`** - Entity type filter (null for default)
4. **`singleLine: false`** - Display format flag

#### Expression Type Fix:
- **Changed default from `EQ` to `RXEQ`** (Regex Equals)
- `RXEQ` is required for pattern matching (e.g., `prod.*`, `.*test.*`)
- `EQ` should only be used for exact string matches

#### Field Order Fix:
The criteriaList fields are now ordered to match Turbonomic's format:
```json
{
  "expVal": "pattern",
  "expType": "RXEQ",
  "filterType": "vmsByName",
  "caseSensitive": false,
  "entityType": null,
  "singleLine": false
}
```

### How to Verify the Fix

1. **Check a working group's structure:**
```bash
curl -k -X GET "https://your-turbo-instance/api/v3/groups/{groupId}" \
  -H "Cookie: JSESSIONID=your-session-id"
```

2. **Compare with script output:**
   - Use `--dry-run` mode to see what will be created
   - Check the backup JSON files in `backups/` directory

3. **Test with a single group:**
```bash
python create_groups.py https://your-turbo-instance user pass test.csv --dry-run --debug
```

### Expression Types Reference

| Type | Use Case | Example |
|------|----------|---------|
| `RXEQ` | Regex pattern matching (default) | `prod.*`, `.*test.*` |
| `EQ` | Exact string match | `Dallas`, `Cluster01` |
| `RXNEQ` | Regex not equals | `^(?!test).*` |
| `NEQ` | Not equals | `!production` |
| `GT` | Greater than (numeric) | `64` (for memory) |
| `LT` | Less than (numeric) | `100` |
| `GTE` | Greater than or equal | `32` |
| `LTE` | Less than or equal | `128` |

### Common Mistakes

#### ❌ Wrong: Using EQ for patterns
```csv
group_name,group_type,filter_type,exp_type,exp_val
Prod VMs,VirtualMachine,vmsByName,EQ,prod.*
```

#### ✅ Correct: Using RXEQ for patterns
```csv
group_name,group_type,filter_type,exp_type,exp_val
Prod VMs,VirtualMachine,vmsByName,RXEQ,prod.*
```

#### ❌ Wrong: Using RXEQ for exact matches
```csv
group_name,group_type,filter_type,exp_type,exp_val
Dallas VMs,VirtualMachine,vmsByDC,RXEQ,Dallas
```

#### ✅ Correct: Using EQ for exact matches
```csv
group_name,group_type,filter_type,exp_type,exp_val
Dallas VMs,VirtualMachine,vmsByDC,EQ,Dallas
```

## Other Common Issues

### Authentication Fails

**Symptoms:**
```
ERROR - Authentication failed: 401
```

**Solutions:**
1. Verify username and password are correct
2. Check if user has permissions to create groups
3. Ensure Turbonomic URL is correct (no trailing slash)
4. Check if account is locked or expired

### SSL Certificate Errors

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
The script disables SSL verification by default for self-signed certificates. If you need to enable it:
```python
self.session.verify = True  # In create_groups.py
```

### Groups Created But Wrong Members

**Symptoms:**
- Group has members but not the expected ones
- Too many or too few members

**Possible Causes:**
1. **Regex pattern is too broad or too narrow**
   - Test your regex pattern separately
   - Use online regex testers with sample VM names

2. **Wrong filter type**
   - Verify the filter type matches your entity type
   - Check available filters in the documentation

3. **Case sensitivity**
   - Set `case_sensitive` to `true` if needed
   - Default is `false` (case-insensitive)

**Solution:**
```csv
# Test with a more specific pattern
group_name,group_type,filter_type,exp_type,exp_val,case_sensitive
Test Group,VirtualMachine,vmsByName,RXEQ,^prod-web-[0-9]+$,false
```

### Rate Limiting (429 Errors)

**Symptoms:**
```
ERROR - Failed to create group: 429 Too Many Requests
```

**Solution:**
The script includes a 0.5-second delay between requests. If you still hit rate limits:

1. Increase the delay in `create_groups.py`:
```python
# Line ~300
time.sleep(1.0)  # Increase from 0.5 to 1.0 seconds
```

2. Process groups in smaller batches

### Duplicate Group Names

**Symptoms:**
```
WARNING - Group already exists: Production VMs
```

**Solutions:**
1. Use `--force` flag to skip duplicate checking (not recommended)
2. Delete existing groups first
3. Use unique names in your CSV

### CSV Parsing Errors

**Symptoms:**
```
ERROR - Row 5: Missing required field 'group_name'
```

**Solutions:**
1. Verify CSV has all required columns:
   - `group_name`
   - `group_type`
   - `filter_type`
   - `exp_val`

2. Check for:
   - Empty cells in required columns
   - Extra commas
   - Incorrect column names
   - Wrong file encoding (use UTF-8)

## Debugging Tips

### 1. Use Dry-Run Mode
Always test with `--dry-run` first:
```bash
python create_groups.py https://turbo user pass groups.csv --dry-run --debug
```

### 2. Check Backup Files
Review the JSON in `backups/` directory to see exactly what was sent to the API.

### 3. Compare with Working Groups
Export a working group and compare its structure:
```bash
# Get working group
curl -k "https://turbo/api/v3/groups/{id}" > working_group.json

# Compare with backup
diff working_group.json backups/groups_backup_*.json
```

### 4. Test Individual Groups
Create a test CSV with just one group to isolate issues.

### 5. Enable Debug Logging
Use `--debug` flag for detailed output:
```bash
python create_groups.py https://turbo user pass groups.csv --debug
```

## Getting Help

If issues persist:

1. **Check the logs** - Look for specific error messages
2. **Review the API documentation** - https://www.ibm.com/docs/en/tarm/8.19.1
3. **Test manually** - Try creating the group via Postman or UI
4. **Compare structures** - Export working vs non-working groups
5. **Check Turbonomic version** - Some features may vary by version

## Version History

### v1.1 (Current)
- ✅ Fixed: Groups now populate with members correctly
- ✅ Added: Required fields (className, logicalOperator, entityType, singleLine)
- ✅ Changed: Default expression type from EQ to RXEQ
- ✅ Fixed: Field ordering in criteriaList
- ✅ Updated: Documentation with correct expression types

### v1.0 (Initial)
- ❌ Issue: Groups created but no members found
- ❌ Missing: Required API fields
- ❌ Wrong: Expression type defaults