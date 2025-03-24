#!/bin/bash

# Colors for better output readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}Setting up Git hooks for this repository...${NC}"

# Get the git root directory
GIT_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$GIT_ROOT/.git/hooks"
PRE_COMMIT="$HOOKS_DIR/pre-commit"

# Check if git hooks directory exists
if [[ ! -d "$HOOKS_DIR" ]]; then
    echo -e "${RED}${BOLD}Error:${NC} Git hooks directory not found at $HOOKS_DIR"
    echo "Make sure you're in a git repository."
    exit 1
fi

# Create pre-commit file
echo -e "${BLUE}Creating pre-commit hook...${NC}"
cp pre-commit-script "$PRE_COMMIT"

# Make the pre-commit script executable
chmod +x "$PRE_COMMIT"

# Check if the hook was created successfully
if [[ -x "$PRE_COMMIT" ]]; then
    echo -e "${GREEN}${BOLD}Success!${NC} Pre-commit hook installed at $PRE_COMMIT"
else
    echo -e "${RED}${BOLD}Error:${NC} Failed to create executable pre-commit hook"
    exit 1
fi

# Install required packages
echo -e "\n${BLUE}${BOLD}Checking required packages...${NC}"

# Function to check and install a package
check_and_install() {
    local package=$1
    if ! command -v $package >/dev/null 2>&1; then
        echo -e "${YELLOW}$package not found. Installing...${NC}"
        pip install $package
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully installed $package${NC}"
        else
            echo -e "${RED}Failed to install $package. Please install it manually with 'pip install $package'${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}$package is already installed${NC}"
    fi
    return 0
}

check_and_install "black" && check_and_install "isort" && check_and_install "flake8"

echo -e "\n${GREEN}${BOLD}Setup complete!${NC}"
echo -e "Your code will now be automatically formatted with black and isort, and checked with flake8 before each commit."
echo -e "If you want to skip the pre-commit hook, use the ${YELLOW}--no-verify${NC} flag: ${BOLD}git commit --no-verify${NC}"

exit 0