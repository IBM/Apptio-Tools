# Dependency Setup Guide

This guide provides detailed instructions for setting up dependencies for Apptio-Tools scripts.

## Table of Contents

- [Quick Start](#quick-start)
- [Automatic Dependency Checking](#automatic-dependency-checking)
- [Manual Installation](#manual-installation)
- [Troubleshooting](#troubleshooting)
- [Windows-Specific Issues](#windows-specific-issues)
- [Virtual Environments](#virtual-environments)

---

## Quick Start

### Recommended: Install All Dependencies at Once

```bash
# Navigate to the repository root
cd Apptio-Tools

# Install all dependencies from requirements.txt
pip install -r requirements.txt
```

This installs:
- `apptio-lib` - Core Apptio/Cloudability API library
- `charset-normalizer` - Character encoding detection for CSV files
- `requests` - HTTP library for API calls
- `python-dotenv` - Optional: Load credentials from .env files

---

## Automatic Dependency Checking

All scripts now include automatic dependency checking that runs when you start them.

### How It Works

1. **When you run a script**, it checks for missing dependencies
2. **If dependencies are missing**, you'll see a clear report:
   ```
   ⚠️  DEPENDENCY CHECK
   ======================================================================
   ❌ REQUIRED packages are missing:
   
     📦 charset-normalizer
        Purpose: Character encoding detection for CSV files
        Used by: Account Group Updater, Views Updater
   ```

3. **You'll be prompted** with installation options:
   ```
   📝 INSTALLATION OPTIONS:
   ======================================================================
   
   ✅ RECOMMENDED: Install all dependencies at once
      cd c:/Apptio-Tools-Local/Apptio-Tools
      pip install -r requirements.txt
   ```

4. **You can choose** to install now or manually later:
   ```
   ❓ Would you like to install the missing dependencies now?
      This will run pip install commands with your permission.
   
      Install dependencies now? (yes/no):
   ```

### Skipping Dependency Check

If you want to skip the automatic check (not recommended):

```bash
python script_name.py --skip-dependency-check [other arguments]
```

---

## Manual Installation

### Option 1: Install from requirements.txt (Recommended)

```bash
pip install -r requirements.txt
```

### Option 2: Install Individual Packages

**Required packages:**
```bash
pip install charset-normalizer requests
pip install git+https://github.com/ibm/apptio-tools-lib.git
```

**Optional but recommended:**
```bash
pip install python-dotenv
```

### Option 3: Install Only What You Need

Different scripts require different packages:

**Account Group Updater:**
```bash
pip install charset-normalizer
pip install git+https://github.com/ibm/apptio-tools-lib.git
```

**Business Mapping Updater:**
```bash
pip install git+https://github.com/ibm/apptio-tools-lib.git
```

**Hierarchical Business Mapping Updater:**
```bash
pip install git+https://github.com/ibm/apptio-tools-lib.git
```

**Views Updater:**
```bash
pip install charset-normalizer requests
pip install git+https://github.com/ibm/apptio-tools-lib.git
```

---

## Troubleshooting

### "pip: command not found" or "pip is not recognized"

**Problem:** pip is not installed or not in your PATH.

**Solution:**

1. **Check if pip is installed:**
   ```bash
   python -m pip --version
   ```

2. **If not installed, install pip:**
   - **Windows:** Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and run:
     ```bash
     python get-pip.py
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m ensurepip --upgrade
     ```

3. **Use python -m pip instead:**
   ```bash
   python -m pip install -r requirements.txt
   ```

### "Permission denied" or "Access is denied"

**Problem:** You don't have permission to install packages system-wide.

**Solutions:**

1. **Install for current user only:**
   ```bash
   pip install --user -r requirements.txt
   ```

2. **Use a virtual environment** (recommended - see below)

3. **Run as administrator** (Windows) or with sudo (macOS/Linux):
   ```bash
   # Windows (PowerShell as Administrator)
   pip install -r requirements.txt
   
   # macOS/Linux
   sudo pip install -r requirements.txt
   ```

### "Could not find a version that satisfies the requirement"

**Problem:** Package not available for your Python version or platform.

**Solution:**

1. **Check your Python version:**
   ```bash
   python --version
   ```
   Ensure you're using Python 3.7 or higher.

2. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Try installing packages individually** to identify which one is problematic.

### SSL Certificate Errors

**Problem:** SSL certificate verification fails during installation.

**Solution:**

1. **Update certificates:**
   ```bash
   pip install --upgrade certifi
   ```

2. **Temporary workaround** (not recommended for production):
   ```bash
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
   ```

### "No module named 'apptio_lib'" After Installation

**Problem:** The apptio-lib package installed but Python can't find it.

**Solutions:**

1. **Verify installation:**
   ```bash
   pip list | grep apptio
   ```

2. **Check if you're using the right Python:**
   ```bash
   which python  # macOS/Linux
   where python  # Windows
   ```

3. **Reinstall the package:**
   ```bash
   pip uninstall apptio-lib
   pip install git+https://github.com/ibm/apptio-tools-lib.git
   ```

---

## Windows-Specific Issues

### PowerShell Execution Policy

**Problem:** PowerShell may block pip from running scripts.

**Symptoms:**
```
⚠️  Your execution policy may prevent pip from installing packages.
Current Policy: Restricted
```

**Solutions:**

1. **Check current policy:**
   ```powershell
   Get-ExecutionPolicy -Scope CurrentUser
   ```

2. **Update policy (run PowerShell as Administrator):**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Alternative: Use Command Prompt instead:**
   - Open Command Prompt (cmd.exe) instead of PowerShell
   - Run your pip commands there

4. **Temporary bypass for single command:**
   ```powershell
   powershell -ExecutionPolicy Bypass -Command "pip install -r requirements.txt"
   ```

### Long Path Issues

**Problem:** Windows has a 260-character path limit.

**Solution:**

1. **Enable long paths in Windows 10/11:**
   - Run as Administrator:
     ```powershell
     New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
     ```

2. **Or move your project to a shorter path:**
   ```bash
   # Instead of: C:\Users\YourName\Documents\Projects\Apptio-Tools-Local\Apptio-Tools
   # Use: C:\Apptio-Tools
   ```

---

## Virtual Environments

Using virtual environments is **highly recommended** to avoid conflicts with other Python projects.

### Why Use Virtual Environments?

- Isolates project dependencies
- Prevents version conflicts
- Makes it easy to reproduce environments
- Doesn't require administrator privileges

### Creating a Virtual Environment

**Windows:**
```bash
# Navigate to project directory
cd Apptio-Tools

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Navigate to project directory
cd Apptio-Tools

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Using the Virtual Environment

**Every time you work on the project:**

1. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Your prompt will change to show (venv)**

3. **Run your scripts normally:**
   ```bash
   cd cloudability/account-group-updater
   python update_ag_entries.py --api-key YOUR_KEY
   ```

4. **Deactivate when done:**
   ```bash
   deactivate
   ```

### Virtual Environment with VS Code

1. **Open Command Palette:** `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. **Type:** "Python: Select Interpreter"
3. **Choose:** The interpreter from your `venv` folder
4. **VS Code will automatically activate** the virtual environment in its terminal

---

## Verifying Installation

After installing dependencies, verify everything works:

```bash
# Test the dependency checker directly
python cloudability/dependency_checker.py

# Or run any script - it will check dependencies automatically
cd cloudability/account-group-updater
python update_ag_entries.py --help
```

You should see:
```
✓ All dependencies are installed!
```

---

## Getting Help

If you continue to have issues:

1. **Check the main README.md** for general troubleshooting
2. **Review error messages carefully** - they often contain the solution
3. **Search for the specific error message** online
4. **Open an issue** on the [GitHub repository](https://github.com/IBM/Apptio-Tools/issues)

Include in your issue:
- Your operating system and version
- Python version (`python --version`)
- Full error message
- Steps you've already tried

---

## Quick Reference

### Common Commands

```bash
# Install all dependencies
pip install -r requirements.txt

# Install for current user only
pip install --user -r requirements.txt

# Upgrade pip
python -m pip install --upgrade pip

# List installed packages
pip list

# Check for missing dependencies
python cloudability/dependency_checker.py

# Skip dependency check in scripts
python script_name.py --skip-dependency-check
```

### Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
# Then scripts will load automatically (requires python-dotenv)
```

---

**Last Updated:** 2026-03-07