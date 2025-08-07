#!/bin/bash

# Log Whisperer Package Build Script
echo "🔍 Building Log Whisperer package..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/ log_whisperer.egg-info/

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade build tools
echo "Upgrading build tools..."
pip install --upgrade pip build twine

# Build the package
echo "Building package..."
python -m build

# Check the package
echo "Checking package..."
twine check dist/*

echo "✅ Package built successfully!"
echo ""
echo "Files created:"
ls -la dist/

echo ""
echo "To upload to PyPI:"
echo "1. Test upload: twine upload --repository testpypi dist/*"
echo "2. Production upload: twine upload dist/*"
echo ""
echo "To install locally:"
echo "pip install dist/log_whisperer-0.1.0-py3-none-any.whl"