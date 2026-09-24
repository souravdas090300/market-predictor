#!/bin/bash

# Setup script for creating GitHub Pages legal repository
# This script will help you create the legal repository and push the files

echo "=== GitHub Pages Legal Repository Setup ==="
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed or not in PATH"
    exit 1
fi

# Create temporary directory for the legal repo
LEGAL_DIR="../market-predictor-legal"
echo "Creating directory: $LEGAL_DIR"
mkdir -p "$LEGAL_DIR"
cd "$LEGAL_DIR"

# Initialize git repository
echo "Initializing git repository..."
git init

# Copy the legal files from parent directory
echo "Copying legal files..."
cp ../privacy.md .
cp ../terms.md .

# Create a simple README
echo "Creating README.md..."
cat > README.md << 'EOF'
# Market Predictor Legal Documents

This repository contains the legal documents for Market Predictor application:

- [Privacy Policy](privacy.md)
- [Terms of Service](terms.md)

## Links
- Privacy Policy: https://YOUR-USERNAME.github.io/market-predictor-legal/privacy
- Terms of Service: https://YOUR-USERNAME.github.io/market-predictor-legal/terms
EOF

# Add all files
echo "Adding files to git..."
git add .

# Commit
echo "Creating initial commit..."
git commit -m "Initial commit - Add legal documents"

echo ""
echo "=== Repository prepared successfully! ==="
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named 'market-predictor-legal'"
echo "3. Make it Public"
echo "4. Check 'Add a README file' and click Create"
echo "5. Run these commands to push to GitHub:"
echo ""
echo "   cd $LEGAL_DIR"
echo "   git remote add origin https://github.com/YOUR-USERNAME/market-predictor-legal.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "6. Then enable GitHub Pages:"
echo "   - Go to repository Settings → Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main, Folder: / (root)"
echo "   - Click Save"
echo ""
echo "Your site will be available at: https://YOUR-USERNAME.github.io/market-predictor-legal/"
