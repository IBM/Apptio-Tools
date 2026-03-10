# Cloudability Scripts Authentication Upgrade Plan

## Executive Summary

This plan outlines the steps to upgrade all Cloudability scripts to support **frontdoor public/private key authentication** in addition to the existing Cloudability API key authentication. Users will be able to choose their preferred authentication method.

## Current State Analysis

### Existing Authentication Architecture

1. **Current Method**: Simple Cloudability API key authentication
   - API key passed as `auth=(api_key, '')` in HTTP basic auth
   - Used directly in all 4 scripts

2. **Scripts to Update**:
   - [`update_ag_entries.py`](cloudability/account-group-updater/update_ag_entries.py) - Account Group updater
   - [`update_mappings_from_csv.py`](cloudability/business-mapping-update/update_mappings_from_csv.py) - Business Mapping updater
   - [`update_hbm.py`](cloudability/update-hierarchical-bm/update_hbm.py) - Hierarchical Business Mapping updater
   - [`views_updater.py`](cloudability/views-updater/views_updater.py) - Views updater

3. **Shared Library**: `apptio_lib` (located in `../apptio-tools-lib/`)
   - [`cloudability.py`](../apptio-tools-lib/apptio_lib/cloudability.py) - HTTP request wrapper
   - [`apptio.py`](../apptio-tools-lib/apptio_lib/apptio.py) - Frontdoor auth functions (already exists!)

### Key Findings

✅ **Good News**: The `apptio_lib.apptio` module already has frontdoor authentication functions:
- [`get_auth()`](../apptio-tools-lib/apptio_lib/apptio.py:16-27) - Gets token from public/private keys
- [`token_getter()`](../apptio-tools-lib/apptio_lib/apptio.py:30-57) - Posts to frontdoor API
- [`make_opentoken_headers()`](../apptio-tools-lib/apptio_lib/apptio.py:60-80) - Creates headers with token

✅ **Good News**: The `cloudability.request()` function already supports `opentoken_headers` parameter

⚠️ **Gap**: Missing function to retrieve environment ID from domain name (needed for frontdoor auth)

## Frontdoor Authentication Flow

Based on the [IBM documentation](https://www.ibm.com/docs/en/apptio-platform/access-administration/saas?topic=apis-authentication-via-api-keys) and code example:

```python
# Step 1: Obtain token from frontdoor
POST https://frontdoor[-region].apptio.com/service/apikeylogin
Body: {"keyAccess": public_key, "keySecret": private_key}
Response: apptio-opentoken in headers

# Step 2: Get environment ID
GET https://frontdoor[-region].apptio.com/api/environment/{domain}/main
Headers: {"apptio-opentoken": token}
Response: {"id": environment_id}

# Step 3: Use token + env_id for Cloudability API calls
Headers: {
    "apptio-opentoken": token,
    "apptio-current-environment": env_id
}
```

## Implementation Plan

### Phase 1: Library Updates

#### 1.1 Update `apptio_lib/apptio.py`
- ✅ Already has `get_auth()` and `token_getter()`
- ✅ Already has `make_opentoken_headers()`
- ➕ **ADD**: `get_environment_id(domain, token, region, environment_name='main')` function
- ➕ **ADD**: `setup_frontdoor_auth(public_key, private_key, domain, region='', environment_name='main')` - convenience function

#### 1.2 Update `apptio_lib/cloudability.py`
- ✅ Already supports `opentoken_headers` parameter
- ✅ Already merges opentoken_headers with request headers
- ✅ Already skips basic auth when opentoken_headers provided
- ✅ Already supports region parameter
- **No changes needed!**

### Phase 2: Script Updates

All 4 scripts need similar updates:

#### 2.1 Command-line Interface Changes

**Current**:
```bash
python script.py <api_key> [options]
```

**New (backward compatible)**:
```bash
# Option 1: Cloudability API key (existing)
python script.py --api-key <key> [options]

# Option 2: Frontdoor authentication (new)
python script.py --frontdoor-public <pub> --frontdoor-private <priv> --domain <domain> [--environment-name <env_name>] [--region <region>] [options]

# Option 3: Environment variables (new)
export APPTIO_PUBLIC_KEY=<pub>
export APPTIO_PRIVATE_KEY=<priv>
export APPTIO_DOMAIN=<domain>
export APPTIO_ENVIRONMENT_NAME=<env_name>  # optional, defaults to "main"
export APPTIO_REGION=<region>  # optional
python script.py [options]
```

#### 2.2 Authentication Setup Pattern

Each script will follow this pattern:

```python
def setup_authentication(args):
    """
    Setup authentication based on provided arguments.
    Returns: (api_key, opentoken_headers) tuple
    """
    # Priority 1: Frontdoor keys from command line
    if args.frontdoor_public and args.frontdoor_private:
        return setup_frontdoor_auth_from_args(args)
    
    # Priority 2: Cloudability API key from command line
    if args.api_key:
        return (args.api_key, {})
    
    # Priority 3: Environment variables
    if os.getenv('APPTIO_PUBLIC_KEY') and os.getenv('APPTIO_PRIVATE_KEY'):
        return setup_frontdoor_auth_from_env()
    
    # Priority 4: Cloudability API key from environment
    if os.getenv('CLOUDABILITY_API_KEY'):
        return (os.getenv('CLOUDABILITY_API_KEY'), {})
    
    print('Error: No authentication credentials provided')
    sys.exit(1)
```

#### 2.3 Script-Specific Updates

**update_ag_entries.py**:
- Update argument parsing to support both auth methods
- Replace `api_key` parameter with auth setup function
- Update all `cldy.get()`, `cldy.put()`, `cldy.post()`, `cldy.delete()` calls to pass `opentoken_headers`
- Update usage documentation

**update_mappings_from_csv.py**:
- Same pattern as above
- Update all API calls

**update_hbm.py**:
- Same pattern as above
- Update all API calls

**views_updater.py**:
- Same pattern as above
- Update all API calls

### Phase 3: Documentation & Examples

#### 3.1 Create Authentication Guide
- Document both authentication methods
- Provide examples for each method
- Explain when to use each method
- Document environment variable setup

#### 3.2 Update README Files
- Update main README with authentication options
- Update each script's usage documentation
- Add troubleshooting section

#### 3.3 Create Example Configuration
- Create `.env.example` file showing environment variables
- Create example scripts showing both auth methods

## Implementation Details

### New Functions to Add

#### In `apptio_lib/apptio.py`:

```python
def get_environment_id(domain, token, region='', environment_name='main'):
    """
    Get environment ID from domain name using frontdoor API.
    
    Args:
        domain: The domain name (e.g., 'customer-name')
        token: The apptio-opentoken
        region: Region suffix ('', 'eu', 'au', etc.)
        environment_name: Environment name (default: 'main')
    
    Returns:
        str: Environment ID
    """
    if region and region[0] != '-':
        region = f'-{region}'
    
    url = f'https://frontdoor{region}.apptio.com/api/environment/{domain}/{environment_name}'
    headers = {
        'Content-Type': 'application/json',
        'apptio-opentoken': token
    }
    
    response = requests.get(url, headers=headers)
    
    if not response.ok:
        print(f'Failed to get environment ID: {response.status_code}')
        print(response.content)
        return None
    
    return response.json()['id']


def setup_frontdoor_auth(public_key, private_key, domain, region='', environment_name='main'):
    """
    Complete frontdoor authentication setup.
    
    Args:
        public_key: Frontdoor public key
        private_key: Frontdoor private key
        domain: Domain name
        region: Region suffix (optional)
        environment_name: Environment name (default: 'main')
    
    Returns:
        dict: Headers with apptio-opentoken and apptio-current-environment
    """
    # Get token
    token = get_auth(region=region, public=public_key, private=private_key)
    if not token:
        return None
    
    # Get environment ID
    env_id = get_environment_id(domain, token, region, environment_name)
    if not env_id:
        return None
    
    # Create headers
    headers = {
        'apptio-opentoken': token,
        'apptio-current-environment': env_id,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    return headers
```

### Argument Parsing Pattern

```python
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Script description',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Authentication Options:
  1. Cloudability API Key:
     --api-key YOUR_KEY
     
  2. Frontdoor Public/Private Keys:
     --frontdoor-public YOUR_PUBLIC_KEY
     --frontdoor-private YOUR_PRIVATE_KEY
     --domain YOUR_DOMAIN
     [--region REGION]
     
  3. Environment Variables:
     CLOUDABILITY_API_KEY or
     APPTIO_PUBLIC_KEY + APPTIO_PRIVATE_KEY + APPTIO_DOMAIN [+ APPTIO_REGION]
        '''
    )
    
    # Authentication group
    auth_group = parser.add_argument_group('authentication')
    auth_group.add_argument('--api-key', help='Cloudability API key')
    auth_group.add_argument('--frontdoor-public', help='Frontdoor public key')
    auth_group.add_argument('--frontdoor-private', help='Frontdoor private key')
    auth_group.add_argument('--domain', help='Domain name (required for frontdoor auth)')
    auth_group.add_argument('--region', default='', help='Region (e.g., eu, au)')
    
    # Script-specific arguments
    # ... add other arguments ...
    
    return parser.parse_args()
```

## Testing Strategy

### Test Cases

1. **Backward Compatibility**:
   - ✅ Existing scripts with API key should work unchanged
   - ✅ Old command-line format should still work

2. **Frontdoor Authentication**:
   - ✅ Command-line frontdoor auth works
   - ✅ Environment variable frontdoor auth works
   - ✅ Region parameter works correctly
   - ✅ Error handling for invalid credentials

3. **API Calls**:
   - ✅ GET requests work with both auth methods
   - ✅ POST requests work with both auth methods
   - ✅ PUT requests work with both auth methods
   - ✅ DELETE requests work with both auth methods

4. **Edge Cases**:
   - ✅ Missing credentials handled gracefully
   - ✅ Invalid credentials show clear error messages
   - ✅ Network errors handled properly

## Migration Guide for Users

### For Existing Users (API Key)

No changes required! Your existing scripts will continue to work:

```bash
# This still works
python update_ag_entries.py YOUR_API_KEY
```

### For New Users (Frontdoor Auth)

```bash
# Option 1: Command line
python update_ag_entries.py \
  --frontdoor-public YOUR_PUBLIC_KEY \
  --frontdoor-private YOUR_PRIVATE_KEY \
  --domain your-domain \
  --region eu

# Option 2: Environment variables
export APPTIO_PUBLIC_KEY=YOUR_PUBLIC_KEY
export APPTIO_PRIVATE_KEY=YOUR_PRIVATE_KEY
export APPTIO_DOMAIN=your-domain
export APPTIO_REGION=eu
python update_ag_entries.py
```

## Benefits

1. **Flexibility**: Users can choose their preferred authentication method
2. **Security**: Frontdoor keys can be rotated and managed centrally
3. **Backward Compatibility**: Existing scripts continue to work
4. **Consistency**: All scripts use the same authentication pattern
5. **Future-Proof**: Easy to add new authentication methods

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing scripts | High | Maintain backward compatibility with old CLI format |
| Complex argument parsing | Medium | Use argparse with clear help text |
| Authentication failures | Medium | Clear error messages and troubleshooting guide |
| Region configuration errors | Low | Default to empty region, document regional URLs |

## Timeline Estimate

- **Phase 1** (Library Updates): 2-3 hours
- **Phase 2** (Script Updates): 4-6 hours (1-1.5 hours per script)
- **Phase 3** (Documentation): 2-3 hours
- **Testing**: 2-3 hours
- **Total**: 10-15 hours

## Success Criteria

- ✅ All 4 scripts support both authentication methods
- ✅ Backward compatibility maintained
- ✅ Clear documentation for both methods
- ✅ All tests pass
- ✅ Example configurations provided
- ✅ Error messages are clear and helpful

## Next Steps

1. Review and approve this plan
2. Switch to Code mode to implement changes
3. Test each script with both authentication methods
4. Update documentation
5. Create pull request for review