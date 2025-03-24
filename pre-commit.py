#!/usr/bin/env python
"""
Pre-commit hook script for formatting Python code using Black, isort, and Flake8.
This script is designed to work on Windows systems.
"""

import os
import subprocess
import sys

# Define directories to exclude
EXCLUDED_DIRS = ["migrations", "some_other_dir"]

# ANSI color codes for Windows (using colorama)
try:
    from colorama import Fore, Style, init

    init()  # Initialize colorama for Windows
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    BOLD = Style.BRIGHT
    NC = Style.RESET_ALL  # No Color
except ImportError:
    # If colorama is not installed, use empty strings
    RED = GREEN = YELLOW = BLUE = BOLD = NC = ""

print(f"{BLUE}{BOLD}Running pre-commit hooks...{NC}")

# Get list of staged Python files
try:
    staged_files_output = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        universal_newlines=True,
    )
    # Filter Python files
    staged_files = [
        file
        for file in staged_files_output.splitlines()
        if file.endswith(".py")
        and not any(
            f"/{excluded}/" in file.replace("\\", "/") or f"\\{excluded}\\" in file
            for excluded in EXCLUDED_DIRS
        )
    ]
except subprocess.CalledProcessError:
    print(f"{RED}Failed to get staged files{NC}")
    sys.exit(1)

# If no Python files are staged, exit
if not staged_files:
    print(f"{YELLOW}No Python files to format.{NC}")
    sys.exit(0)

# Check if our tools are installed
tools_missing = False
for tool in ["black", "isort", "flake8"]:
    try:
        subprocess.check_call(
            [tool, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            f"{RED}{BOLD}Error:{NC} {tool} is not installed. Run 'pip install {tool}'"
        )
        tools_missing = True

if tools_missing:
    sys.exit(1)

print(f"{BLUE}Formatting Python files:{NC}")

# Initialize counter for failed files
failed = 0

# Format each staged Python file with black and isort
for file in staged_files:
    # Check if file exists
    if not os.path.isfile(file):
        continue

    print(f"  Processing {BOLD}{file}{NC}")

    # Format with Black
    print(f"    {BLUE}→{NC} Running black...")
    try:
        subprocess.check_call(
            ["black", file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"    {GREEN}✓{NC} Black formatting done")
    except subprocess.CalledProcessError:
        print(f"    {RED}✘ Black failed on {file}{NC}")
        failed = 1

    # Sort imports with isort
    print(f"    {BLUE}→{NC} Running isort...")
    try:
        subprocess.check_call(
            ["isort", file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"    {GREEN}✓{NC} Imports sorted")
    except subprocess.CalledProcessError:
        print(f"    {RED}✘ isort failed on {file}{NC}")
        failed = 1

    # Check with flake8
    print(f"    {BLUE}→{NC} Running flake8...")
    try:
        flake8_output = subprocess.check_output(
            ["flake8", file], stderr=subprocess.STDOUT, universal_newlines=True
        )
        print(f"    {GREEN}✓{NC} No flake8 issues found")
    except subprocess.CalledProcessError as e:
        flake8_output = e.output
        print(f"    {RED}✘ Flake8 found issues in {file}:{NC}")
        # Indent output
        for line in flake8_output.splitlines():
            print(f"      {line}")
        print(f"    {YELLOW}→ Flake8 issues will not prevent commit{NC}")

    # Add the formatted file back to the staging area
    try:
        subprocess.check_call(["git", "add", file])
    except subprocess.CalledProcessError:
        print(f"    {RED}✘ Failed to stage changes for {file}{NC}")
        failed = 1

if failed:
    print(f"\n{RED}{BOLD}Some files could not be formatted.{NC}")
    print("Please check the errors above and fix them manually.")
    sys.exit(1)

print(f"\n{GREEN}{BOLD}All files formatted successfully!{NC} Changes have been staged.")
sys.exit(0)
