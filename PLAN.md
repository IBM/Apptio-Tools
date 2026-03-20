# Turbonomic Group Creator Script - Planning Document

## Overview
Create a Python script to automate the creation of dynamic groups in Turbonomic using CSV file input. The script will support multiple entity types and flexible filtering criteria based on the official Turbonomic API v3 documentation.

## Information Gathered from API Documentation

### 1. **API Endpoint for Creating Groups**
```
POST https://{turbo_url}/api/v3/groups/
```

### 2. **Group Creation Request Structure**

```json
{
    "isStatic": false,
    "displayName": "Group Name",
    "memberUuidList": [],
    "criteriaList": [
        {
            "expType": "EQ",
            "expVal": "regex_pattern",
            "filterType": "entityTypeByAttribute",
            "caseSensitive": false
        }
    ],
    "groupType": "EntityType"
}
```

**Key Fields:**
- `isStatic`: `false` for dynamic groups, `true` for static groups
- `displayName`: The name of the group
- `memberUuidList`: Empty array for dynamic groups (populated for static groups)
- `criteriaList`: Array of filter criteria (for dynamic groups)
- `groupType`: The entity type (e.g., "VirtualMachine", "PhysicalMachine", "Namespace")

### 3. **Criteria List Structure**

Each criterion in `criteriaList` contains:
- `expType`: Expression type for comparison
  - `EQ` - Equals
  - `NEQ` - Not Equals  
  - `GT` - Greater Than
  - `LT` - Less Than
  - `GTE` - Greater Than or Equal
  - `LTE` - Less Than or Equal
- `expVal`: The value or regex pattern to match
- `filterType`: The specific filter to apply (see Filter Types below)
- `caseSensitive`: Boolean - whether the regex is case-sensitive

### 4. **Supported Entity Types (groupType)**

Based on API documentation:
- `VirtualMachine`
- `PhysicalMachine`
- `VirtualDataCenter`
- `Namespace`
- `ContainerPod`
- `WorkloadController`
- `ApplicationComponent`
- `VirtualVolume`
- `Storage`
- `DataStore`
- `DataCenter`
- `Cluster`
- `Network`
- `Switch`

### 5. **Filter Types by Entity**

#### VirtualMachine Filters
- `vmsByName` - Filter by VM name
- `vmsByPMName` - Filter by Physical Machine name
- `vmsByStorage` - Filter by storage name
- `vmsByNetwork` - Filter by network name
- `vmsByApplication` - Filter by application name
- `vmsByDatabaseServer` - Filter by database server
- `vmsByDatabaseServerVersion` - Filter by database server version
- `vmsByDC` - Filter by datacenter
- `vmsByVDC` - Filter by virtual datacenter
- `vmsByDCnested` - Filter by nested datacenter
- `vmsByGuestName` - Filter by guest OS name
- `vmsByAltName` - Filter by alternate name
- `vmsByClusterName` - Filter by cluster name
- `vmsByDiskArrayName` - Filter by disk array name
- `vmsByLogicalPoolName` - Filter by logical pool name
- `vmsByProfileName` - Filter by profile name
- `vmsByTag` - Filter by tag (format: "key=value")
- `vmsByState` - Filter by VM state
- `vmsByBusinessAccountUuid` - Filter by business account UUID
- `vmsByResourceGroupUuid` - Filter by resource group UUID

#### PhysicalMachine Filters
- `pmsByName` - Filter by PM name
- `pmsByStorage` - Filter by storage name
- `pmsByNetwork` - Filter by network name
- `pmsBySwitch` - Filter by switch name
- `pmsByNumVms` - Filter by number of VMs
- `pmsByDC` - Filter by datacenter
- `pmsByMem` - Filter by memory

#### VirtualDataCenter Filters
- `vdcsByVDCName` - Filter by VDC name
- `vdcsByTag` - Filter by tag
- `vdcsByState` - Filter by state

#### Namespace Filters (Kubernetes)
- `namespacesByName` - Filter by namespace name
- `namespacesByTag` - Filter by tag (format: "key=value")
- `namespacesByCluster` - Filter by cluster name

### 6. **CSV File Structure**

The CSV should contain the following columns:

| Column Name | Required | Description | Example Values |
|-------------|----------|-------------|----------------|
| `group_name` | Yes | Display name for the group | "Production VMs", "Dev Namespaces" |
| `group_type` | Yes | Entity type for the group | "VirtualMachine", "Namespace", "PhysicalMachine" |
| `filter_type` | Yes | Type of filter to apply | "vmsByName", "vmsByTag", "namespacesByTag" |
| `exp_type` | No | Expression type (default: EQ) | "EQ", "NEQ", "GT", "LT", "GTE", "LTE" |
| `exp_val` | Yes | Value or regex pattern | "prod.*", "environment=production", "AJ.*" |
| `case_sensitive` | No | Case sensitivity (default: false) | "true", "false" |
| `description` | No | Optional description | "All production virtual machines" |

### 7. **Example CSV File Content**

**File: `groups_example.csv`**

```csv
group_name,group_type,filter_type,exp_type,exp_val,case_sensitive,description
Production VMs,VirtualMachine,vmsByName,EQ,prod.*,false,All VMs with names starting with prod
Development VMs,VirtualMachine,vmsByName,EQ,dev.*,false,All VMs with names starting with dev
Test VMs,VirtualMachine,vmsByName,EQ,test.*,false,All VMs with names starting with test
High Criticality VMs,VirtualMachine,vmsByTag,EQ,criticality=high,false,VMs tagged as high criticality
Production Namespaces,Namespace,namespacesByTag,EQ,environment=production,false,Production Kubernetes namespaces
Dev Namespaces,Namespace,namespacesByName,EQ,dev-.*,false,Development namespaces
High Memory PMs,PhysicalMachine,pmsByMem,GT,64,false,Physical machines with more than 64GB RAM
AWS VMs,VirtualMachine,vmsByTag,EQ,cloud=aws,false,VMs running on AWS
Azure VMs,VirtualMachine,vmsByTag,EQ,cloud=azure,false,VMs running on Azure
App Tier VMs,VirtualMachine,vmsByName,EQ,.*-app-.*,false,Application tier VMs
DB Tier VMs,VirtualMachine,vmsByName,EQ,.*-db-.*,false,Database tier VMs
Web Tier VMs,VirtualMachine,vmsByName,EQ,.*-web-.*,false,Web tier VMs
Dallas Datacenter VMs,VirtualMachine,vmsByDC,EQ,Dallas,false,All VMs in Dallas datacenter
Cluster01 VMs,VirtualMachine,vmsByClusterName,EQ,Cluster01,false,VMs in Cluster01
```

### 8. **API Example from Documentation**

**Request:**
```
POST https://10.10.10.10/api/v3/groups/
```

**Body:**
```json
{
    "isStatic": false,
    "displayName": "Dallas-Dynamic",
    "memberUuidList": [],
    "criteriaList": [
        {
            "expType": "EQ",
            "expVal": "AJ.*",
            "filterType": "vmsByName",
            "caseSensitive": false
        }
    ],
    "groupType": "VirtualMachine"
}
```

This creates a dynamic group of VMs whose names start with "AJ".

### 9. **Script Features**

#### Core Functionality
- ✅ Read CSV file with group configurations
- ✅ Authenticate to Turbonomic API (POST /api/v3/login)
- ✅ Validate entity types and filter types
- ✅ Build criteriaList based on CSV specifications
- ✅ Create groups via POST /api/v3/groups/
- ✅ Handle API errors and rate limiting
- ✅ Log success/failure for each group

#### Additional Features
- ✅ **Dry-run mode**: Preview what would be created without making changes
- ✅ **Duplicate checking**: Check if group already exists (GET /api/v3/groups)
- ✅ **Backup**: Save list of created groups for reference
- ✅ **Error handling**: Graceful handling of API errors
- ✅ **Progress tracking**: Show progress for large CSV files
- ✅ **Validation**: Pre-validate CSV before making API calls
- ✅ **Multiple criteria**: Support multiple filter criteria per group (AND logic)

### 10. **Script Usage**

```bash
# Basic usage
python create_groups.py <turbo_url> <username> <password> <csv_file>

# With dry-run mode
python create_groups.py <turbo_url> <username> <password> <csv_file> --dry-run

# With debug logging
python create_groups.py <turbo_url> <username> <password> <csv_file> --debug

# Skip duplicate checking
python create_groups.py <turbo_url> <username> <password> <csv_file> --force
```

### 11. **Authentication**

**Login Endpoint:**
```
POST https://{turbo_url}/api/v3/login
Content-Type: application/x-www-form-urlencoded

username={user}&password={pass}
```

**Response:**
- Returns JSESSIONID cookie for subsequent requests
- Session timeout: 30 minutes (default, configurable in Turbonomic)
- Must include cookie in all subsequent API calls

### 12. **Error Handling Scenarios**

- **Authentication failure**: Invalid credentials (401)
- **Invalid entity type**: Entity type not supported
- **Invalid filter type**: Filter type not valid for entity
- **Duplicate group name**: Group already exists (409)
- **API rate limiting**: Too many requests (429)
- **Network errors**: Connection timeout, DNS issues
- **Malformed CSV**: Missing required columns, invalid data
- **Invalid regex**: Malformed regular expression in expVal

### 13. **Dependencies**

```python
import requests  # For API calls
import csv  # For CSV parsing
import sys  # For command-line arguments
import json  # For API request/response handling
import time  # For rate limiting delays
import logging  # For logging
import argparse  # For command-line argument parsing
from typing import Dict, List, Optional, Tuple
```

### 14. **Advanced Features**

#### Multiple Criteria per Group
The script should support creating groups with multiple filter criteria (AND logic):

```csv
group_name,group_type,filter_type,exp_type,exp_val,case_sensitive,description
Complex Group,VirtualMachine,vmsByName|vmsByTag,EQ|EQ,prod.*|environment=production,false|false,VMs matching name AND tag
```

#### Filter Type Validation
The script should validate that the filter type is appropriate for the entity type:
- Maintain a mapping of entity types to valid filter types
- Warn user if invalid combination is detected
- Optionally fetch available filter types from API dynamically

### 15. **Implementation Plan**

1. **Phase 1: Core Functionality**
   - Implement authentication
   - Implement CSV parsing
   - Implement basic group creation
   - Add error handling

2. **Phase 2: Validation**
   - Add entity type validation
   - Add filter type validation
   - Add CSV format validation
   - Add duplicate group checking

3. **Phase 3: Enhanced Features**
   - Add dry-run mode
   - Add progress tracking
   - Add backup functionality
   - Add support for multiple criteria

4. **Phase 4: Testing & Documentation**
   - Test with various entity types
   - Test error scenarios
   - Create comprehensive README
   - Add usage examples

### 16. **File Structure**

```
turbonomic/group-creator/
├── create_groups.py          # Main script
├── groups_example.csv        # Example CSV file
├── README.md                 # Usage documentation
├── PLAN.md                   # This planning document
└── backups/                  # Directory for backup files
```

### 17. **Summary of Information Needed**

Based on the comprehensive research of the Turbonomic API documentation, here's what you need to provide to create groups:

#### Required Information:
1. **Turbonomic Instance URL** - Your Turbonomic server URL
2. **Credentials** - Username and password for API authentication
3. **CSV File** with the following columns:
   - `group_name` - Name for the group
   - `group_type` - Entity type (VirtualMachine, Namespace, PhysicalMachine, etc.)
   - `filter_type` - Filter to apply (vmsByName, vmsByTag, namespacesByTag, etc.)
   - `exp_val` - Value or regex pattern to match
   
#### Optional Information:
4. **exp_type** - Comparison operator (EQ, NEQ, GT, LT, GTE, LTE) - defaults to EQ
5. **case_sensitive** - Whether regex is case-sensitive - defaults to false
6. **description** - Optional description for the group

#### Key Capabilities:
- Create dynamic groups based on name patterns (regex)
- Create groups based on tags (key=value format)
- Create groups based on relationships (datacenter, cluster, network, etc.)
- Create groups based on numeric comparisons (memory, VM count, etc.)
- Support multiple entity types (VMs, Physical Machines, Namespaces, Pods, etc.)

### 18. **Next Steps**

1. ✅ Research complete - gathered all API information
2. ✅ CSV format designed with all necessary columns
3. ✅ Example CSV content created (to be written in Code mode)
4. Ready to switch to Code mode for implementation
5. Will create the Python script with all features
6. Will test with sample data
7. Will create comprehensive README

## References

- **Official API Documentation**: https://www.ibm.com/docs/en/tarm/8.19.1?topic=documentation-api-reference
- **Groups Endpoint**: https://www.ibm.com/docs/en/tarm/8.19.1?topic=reference-groups-endpoint
- **Groups Requests**: https://www.ibm.com/docs/en/tarm/8.19.1?topic=endpoint-groups-requests
- **Groups Endpoint Tips**: https://www.ibm.com/docs/en/tarm/8.19.1?topic=endpoint-groups-endpoint-tips
- Existing Postman Collection: [`turbonomic/postman-collection/Turbo API.postman_collection.json`](../postman-collection/Turbo%20API.postman_collection.json:401)
- Similar Script Pattern: [`cloudability/account-group-updater/update_ag_entries.py`](../../cloudability/account-group-updater/update_ag_entries.py:1)