"""
Copyright IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

Dependency Checker Module for Apptio-Tools

This module provides user-friendly dependency checking with clear prompts
and instructions rather than automatic installation. It focuses on guiding
users through the setup process with their explicit consent.
"""

import sys
import subprocess
import importlib.util
import os
from pathlib import Path


# Define required and optional packages
REQUIRED_PACKAGES = {
    'charset_normalizer': {
        'pip_name': 'charset-normalizer',
        'description': 'Character encoding detection for CSV files',
        'required_by': ['Account Group Updater', 'Views Updater']
    },
    'apptio_lib': {
        'pip_name': 'git+https://github.com/ibm/apptio-tools-lib.git',
        'description': 'Apptio API library (core functionality)',
        'required_by': ['All scripts']
    },
    'requests': {
        'pip_name': 'requests',
        'description': 'HTTP library for API calls',
        'required_by': ['Views Updater']
    }
}

OPTIONAL_PACKAGES = {
    'dotenv': {
        'pip_name': 'python-dotenv',
        'description': 'Load environment variables from .env files',
        'benefit': 'Easier credential management without exposing keys in command line'
    }
}


def check_package_installed(package_name):
    """
    Check if a Python package is installed.
    
    Args:
        package_name (str): The import name of the package
    
    Returns:
        bool: True if package is installed, False otherwise
    """
    return importlib.util.find_spec(package_name) is not None


def get_python_executable():
    """
    Get the current Python executable path.
    
    Returns:
        str: Path to Python executable
    """
    return sys.executable


def check_pip_available():
    """
    Check if pip is available in the current Python environment.
    
    Returns:
        bool: True if pip is available, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_windows_execution_policy():
    """
    Check Windows PowerShell execution policy (informational only).
    Does not attempt to change it.
    
    Returns:
        tuple: (is_restricted, policy_name)
    """
    if sys.platform != 'win32':
        return (False, 'N/A - Not Windows')
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-ExecutionPolicy', '-Scope', 'CurrentUser'],
            capture_output=True,
            text=True,
            timeout=5
        )
        policy = result.stdout.strip()
        is_restricted = policy in ['Restricted', 'Undefined']
        return (is_restricted, policy)
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return (False, 'Unable to determine')


def get_requirements_file_path():
    """
    Get the path to requirements.txt file.
    
    Returns:
        Path or None: Path to requirements.txt if it exists, None otherwise
    """
    # Try to find requirements.txt in the repository root
    current_file = Path(__file__).resolve()
    repo_root = current_file.parent.parent  # Go up from cloudability/ to repo root
    req_file = repo_root / 'requirements.txt'
    
    if req_file.exists():
        return req_file
    return None


def display_missing_packages(missing_required, missing_optional):
    """
    Display information about missing packages in a user-friendly format.
    
    Args:
        missing_required (list): List of tuples (import_name, package_info)
        missing_optional (list): List of tuples (import_name, package_info)
    """
    print("\n" + "="*70)
    print("⚠️  DEPENDENCY CHECK")
    print("="*70)
    
    if missing_required:
        print("\n❌ REQUIRED packages are missing:")
        print("-" * 70)
        for import_name, info in missing_required:
            print(f"\n  📦 {info['pip_name']}")
            print(f"     Purpose: {info['description']}")
            print(f"     Used by: {info['required_by']}")
    
    if missing_optional:
        print("\n💡 OPTIONAL packages are missing:")
        print("-" * 70)
        for import_name, info in missing_optional:
            print(f"\n  📦 {info['pip_name']}")
            print(f"     Purpose: {info['description']}")
            print(f"     Benefit: {info['benefit']}")
    
    print("\n" + "="*70)


def display_installation_instructions(missing_required, missing_optional, req_file_path):
    """
    Display clear installation instructions for missing packages.
    
    Args:
        missing_required (list): List of required packages
        missing_optional (list): List of optional packages
        req_file_path (Path or None): Path to requirements.txt
    """
    print("\n📝 INSTALLATION OPTIONS:")
    print("="*70)
    
    # Option 1: Install from requirements.txt (recommended)
    if req_file_path:
        print("\n✅ RECOMMENDED: Install all dependencies at once")
        print("-" * 70)
        print(f"   cd {req_file_path.parent}")
        print(f"   pip install -r requirements.txt")
        print("\n   This installs all required and optional packages.")
    
    # Option 2: Install only required packages
    if missing_required:
        print("\n✅ OPTION 2: Install only required packages")
        print("-" * 70)
        required_packages = [info['pip_name'] for _, info in missing_required]
        
        # Handle git+https URLs separately
        git_packages = [p for p in required_packages if p.startswith('git+')]
        pip_packages = [p for p in required_packages if not p.startswith('git+')]
        
        if pip_packages:
            print(f"   pip install {' '.join(pip_packages)}")
        if git_packages:
            for git_pkg in git_packages:
                print(f"   pip install {git_pkg}")
    
    # Option 3: Install optional packages
    if missing_optional:
        print("\n💡 OPTION 3: Also install optional packages (recommended)")
        print("-" * 70)
        optional_packages = [info['pip_name'] for _, info in missing_optional]
        print(f"   pip install {' '.join(optional_packages)}")
    
    print("\n" + "="*70)


def display_windows_policy_info(is_restricted, policy_name):
    """
    Display Windows PowerShell execution policy information.
    
    Args:
        is_restricted (bool): Whether the policy is restrictive
        policy_name (str): Name of the current policy
    """
    if sys.platform != 'win32':
        return
    
    print("\n🪟 WINDOWS POWERSHELL EXECUTION POLICY:")
    print("="*70)
    print(f"   Current Policy: {policy_name}")
    
    if is_restricted:
        print("\n   ⚠️  Your execution policy may prevent pip from installing packages.")
        print("\n   To update the policy (run PowerShell as Administrator):")
        print("   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
        print("\n   Or run this script in Command Prompt (cmd.exe) instead of PowerShell.")
    else:
        print("   ✓ Your execution policy should allow package installation.")
    
    print("="*70)


def prompt_user_for_installation():
    """
    Prompt the user to decide whether to install dependencies now.
    
    Returns:
        bool: True if user wants to install now, False otherwise
    """
    print("\n❓ Would you like to install the missing dependencies now?")
    print("   This will run pip install commands with your permission.")
    print()
    
    while True:
        response = input("   Install dependencies now? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("   Please enter 'yes' or 'no'")


def install_packages(packages_to_install):
    """
    Install packages with user's explicit consent.
    
    Args:
        packages_to_install (list): List of tuples (import_name, package_info)
    
    Returns:
        tuple: (success_count, failed_packages)
    """
    print("\n📦 Installing packages...")
    print("="*70)
    
    success_count = 0
    failed_packages = []
    
    for import_name, info in packages_to_install:
        pip_name = info['pip_name']
        print(f"\n   Installing {pip_name}...")
        
        try:
            # Show the command being run
            print(f"   Running: pip install {pip_name}")
            
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', pip_name],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout per package
            )
            
            if result.returncode == 0:
                print(f"   ✓ Successfully installed {pip_name}")
                success_count += 1
            else:
                print(f"   ✗ Failed to install {pip_name}")
                print(f"   Error: {result.stderr[:200]}")  # Show first 200 chars of error
                failed_packages.append(pip_name)
        
        except subprocess.TimeoutExpired:
            print(f"   ✗ Installation timed out for {pip_name}")
            failed_packages.append(pip_name)
        except Exception as e:
            print(f"   ✗ Error installing {pip_name}: {str(e)[:100]}")
            failed_packages.append(pip_name)
    
    print("\n" + "="*70)
    return (success_count, failed_packages)


def check_and_prompt_for_dependencies(include_optional=True, silent=False):
    """
    Main function to check dependencies and prompt user for installation.
    
    This function:
    1. Checks which packages are missing
    2. Displays clear information about missing packages
    3. Provides installation instructions
    4. Optionally prompts to install with user consent
    5. Does NOT automatically install without permission
    
    Args:
        include_optional (bool): Whether to check optional packages
        silent (bool): If True, skip all prompts and just return status
    
    Returns:
        bool: True if all required dependencies are available, False otherwise
    """
    # Check which packages are missing
    missing_required = []
    missing_optional = []
    
    for import_name, info in REQUIRED_PACKAGES.items():
        if not check_package_installed(import_name):
            missing_required.append((import_name, info))
    
    if include_optional:
        for import_name, info in OPTIONAL_PACKAGES.items():
            if not check_package_installed(import_name):
                missing_optional.append((import_name, info))
    
    # If nothing is missing, we're good!
    if not missing_required and not missing_optional:
        if not silent:
            print("✓ All dependencies are installed!")
        return True
    
    # If only optional packages are missing, that's okay
    if not missing_required:
        if not silent and missing_optional:
            print("✓ All required dependencies are installed!")
            print("💡 Some optional packages are missing but the script will work.")
        return True
    
    # We have missing required packages - need to inform the user
    if silent:
        return False
    
    # Display what's missing
    display_missing_packages(missing_required, missing_optional)
    
    # Get requirements.txt path
    req_file_path = get_requirements_file_path()
    
    # Display installation instructions
    display_installation_instructions(missing_required, missing_optional, req_file_path)
    
    # Check Windows execution policy (informational only)
    if sys.platform == 'win32':
        is_restricted, policy_name = check_windows_execution_policy()
        display_windows_policy_info(is_restricted, policy_name)
    
    # Check if pip is available
    if not check_pip_available():
        print("\n❌ ERROR: pip is not available in your Python environment.")
        print("   Please install pip first: https://pip.pypa.io/en/stable/installation/")
        return False
    
    # Prompt user for installation
    if prompt_user_for_installation():
        # Combine required and optional for installation
        packages_to_install = missing_required
        if include_optional and missing_optional:
            print("\n💡 Including optional packages in installation...")
            packages_to_install.extend(missing_optional)
        
        success_count, failed_packages = install_packages(packages_to_install)
        
        if failed_packages:
            print(f"\n⚠️  {len(failed_packages)} package(s) failed to install:")
            for pkg in failed_packages:
                print(f"   - {pkg}")
            print("\n   Please try installing them manually using the commands above.")
            return False
        else:
            print(f"\n✅ Successfully installed {success_count} package(s)!")
            print("   You can now run the script.")
            return True
    else:
        print("\n📝 Please install the required dependencies manually before running this script.")
        print("   Use the installation commands shown above.")
        return False


def check_dependencies_silent():
    """
    Silently check if all required dependencies are installed.
    Used for --skip-dependency-check scenarios.
    
    Returns:
        bool: True if all required dependencies are available, False otherwise
    """
    return check_and_prompt_for_dependencies(include_optional=False, silent=True)


# For backward compatibility and easy imports
check_dependencies = check_and_prompt_for_dependencies


if __name__ == '__main__':
    # Allow running this module directly to check dependencies
    print("Apptio-Tools Dependency Checker")
    print("="*70)
    result = check_and_prompt_for_dependencies(include_optional=True, silent=False)
    sys.exit(0 if result else 1)

# Made with Bob
