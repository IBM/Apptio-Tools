# Dependency Checker Implementation Summary

## Overview

Successfully implemented a hybrid dependency checking system for Apptio-Tools that prioritizes user prompts and clear instructions over automatic actions.

## What Was Implemented

### 1. Core Files Created

#### `requirements.txt`
- Comprehensive list of all project dependencies
- Includes required packages: `apptio-lib`, `charset-normalizer`, `requests`
- Includes optional package: `python-dotenv`
- Single command installation: `pip install -r requirements.txt`

#### `cloudability/dependency_checker.py` (408 lines)
A robust dependency checking module with:
- **Package detection**: Uses `importlib.util.find_spec()` to detect missing packages
- **User-friendly prompts**: Clear, informative messages about what's missing and why
- **Installation options**: Shows multiple ways to install (requirements.txt, individual packages, etc.)
- **Windows PowerShell policy checker**: Informational only, never modifies without permission
- **Consent-based installation**: Always asks before installing anything
- **Detailed error handling**: Graceful failures with helpful messages
- **Silent mode**: For programmatic checks without user interaction

Key functions:
- `check_and_prompt_for_dependencies()` - Main entry point
- `display_missing_packages()` - Shows what's missing in a clear format
- `display_installation_instructions()` - Provides multiple installation options
- `prompt_user_for_installation()` - Gets explicit user consent
- `install_packages()` - Installs with user permission
- `check_windows_execution_policy()` - Informational Windows policy check

#### `.env.example`
- Template for environment variable configuration
- Clear instructions for both authentication methods
- Ready to copy and customize

#### `DEPENDENCY_SETUP.md` (424 lines)
Comprehensive troubleshooting guide covering:
- Quick start instructions
- Automatic dependency checking explanation
- Manual installation options
- Common issues and solutions
- Windows-specific problems (PowerShell policies, long paths)
- Virtual environment setup
- Verification steps

### 2. Script Integration

Modified all 4 Python scripts to include dependency checking:

#### Changes Made to Each Script:
1. **Added `--skip-dependency-check` flag** to argument parser
2. **Added dependency check** after argument parsing, before authentication
3. **Minimal code changes** - only 7-8 lines added per script

Scripts updated:
- `cloudability/account-group-updater/update_ag_entries.py`
- `cloudability/business-mapping-update/update_mappings_from_csv.py`
- `cloudability/update-hierarchical-bm/update_hbm.py`
- `cloudability/views-updater/views_updater.py`

Integration pattern:
```python
# Check dependencies unless explicitly skipped
if not args.skip_dependency_check:
    from dependency_checker import check_dependencies
    if not check_dependencies(include_optional=True, silent=False):
        print('\n❌ Cannot proceed without required dependencies.')
        print('   Run with --skip-dependency-check to bypass this check (not recommended).')
        sys.exit(1)
```

### 3. Documentation Updates

#### `README.md`
Added new sections:
- **Quick Start** with automatic dependency installation
- **Automatic Dependency Checking** feature explanation
- **Dependency Issues** troubleshooting section
- Links to detailed `DEPENDENCY_SETUP.md`

## Key Design Principles

### 1. User Control
- ✅ Always ask for permission before installing
- ✅ Never modify system settings automatically
- ✅ Provide clear opt-out mechanism (`--skip-dependency-check`)
- ✅ Show exactly what will be installed

### 2. Clear Communication
- ✅ Use emojis and formatting for readability
- ✅ Explain WHY each package is needed
- ✅ Provide multiple installation options
- ✅ Show the actual commands that will run

### 3. Graceful Degradation
- ✅ Scripts can still run with `--skip-dependency-check`
- ✅ Optional packages don't block execution
- ✅ Clear error messages with next steps
- ✅ Fallback to manual instructions if auto-install fails

### 4. Platform Awareness
- ✅ Detects Windows vs macOS/Linux
- ✅ Checks PowerShell execution policy (informational)
- ✅ Provides platform-specific instructions
- ✅ Handles path differences

## User Experience Flow

### Scenario 1: All Dependencies Present
```
✓ All dependencies are installed!
[Script continues normally]
```

### Scenario 2: Missing Dependencies
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

❓ Would you like to install the missing dependencies now? (yes/no): yes

📦 Installing packages...
======================================================================

   Installing charset-normalizer...
   Running: pip install charset-normalizer
   ✓ Successfully installed charset-normalizer

✅ Successfully installed 1 package(s)!
   You can now run the script.
```

### Scenario 3: User Declines Installation
```
❓ Would you like to install the missing dependencies now? (yes/no): no

📝 Please install the required dependencies manually before running this script.
   Use the installation commands shown above.
```

### Scenario 4: Windows PowerShell Policy Warning
```
🪟 WINDOWS POWERSHELL EXECUTION POLICY:
======================================================================
   Current Policy: Restricted

   ⚠️  Your execution policy may prevent pip from installing packages.

   To update the policy (run PowerShell as Administrator):
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

   Or run this script in Command Prompt (cmd.exe) instead of PowerShell.
======================================================================
```

## Testing Recommendations

The implementation is ready for testing on:

### Windows
- [ ] Test with PowerShell (various execution policies)
- [ ] Test with Command Prompt
- [ ] Test with Git Bash
- [ ] Verify long path handling
- [ ] Test virtual environment creation

### macOS
- [ ] Test with system Python
- [ ] Test with Homebrew Python
- [ ] Test with pyenv
- [ ] Test virtual environment creation

### Linux
- [ ] Test with system Python
- [ ] Test with pyenv
- [ ] Test with different distributions (Ubuntu, CentOS, etc.)
- [ ] Test virtual environment creation

### Cross-Platform
- [ ] Test with missing dependencies
- [ ] Test with all dependencies present
- [ ] Test `--skip-dependency-check` flag
- [ ] Test installation acceptance (yes)
- [ ] Test installation decline (no)
- [ ] Test with no pip available
- [ ] Test with restricted permissions
- [ ] Test requirements.txt installation
- [ ] Test individual package installation

## Benefits

### For Users
1. **Easier onboarding** - One command to install everything
2. **Clear guidance** - Know exactly what's needed and why
3. **No surprises** - Always asked before changes
4. **Better troubleshooting** - Comprehensive documentation

### For Maintainers
1. **Fewer support requests** - Self-service dependency resolution
2. **Consistent environments** - Everyone uses requirements.txt
3. **Better documentation** - Centralized troubleshooting guide
4. **Easier updates** - Single file to update dependencies

### For the Project
1. **Professional appearance** - Modern dependency management
2. **Lower barrier to entry** - Easier for new contributors
3. **Better reliability** - Catches issues before they cause errors
4. **Cross-platform support** - Works on Windows, macOS, Linux

## Files Modified/Created

### Created (5 files):
1. `requirements.txt` - Dependency list
2. `cloudability/dependency_checker.py` - Core checking module
3. `.env.example` - Environment variable template
4. `DEPENDENCY_SETUP.md` - Detailed troubleshooting guide
5. `IMPLEMENTATION_SUMMARY.md` - This file

### Modified (5 files):
1. `cloudability/account-group-updater/update_ag_entries.py`
2. `cloudability/business-mapping-update/update_mappings_from_csv.py`
3. `cloudability/update-hierarchical-bm/update_hbm.py`
4. `cloudability/views-updater/views_updater.py`
5. `README.md`

## Next Steps

1. **Test the implementation** across different platforms
2. **Gather user feedback** on the prompts and flow
3. **Refine error messages** based on real-world usage
4. **Consider adding** a `--auto-install` flag for CI/CD environments
5. **Monitor** for any edge cases or issues

## Conclusion

The hybrid dependency checking approach successfully balances automation with user control. It provides a smooth experience for new users while respecting the preferences of advanced users who may want to manage dependencies manually.

The implementation prioritizes:
- ✅ Clear communication over silent automation
- ✅ User consent over forced changes
- ✅ Helpful guidance over cryptic errors
- ✅ Multiple options over single solutions

This approach aligns with modern best practices for Python project dependency management while maintaining the flexibility needed for diverse user environments.