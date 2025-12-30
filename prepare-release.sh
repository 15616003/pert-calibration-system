#!/bin/bash
# prepare-release.sh
# Prepares the sanitized PERT Calibration System for GitHub release

set -e  # Exit on any error

echo "======================================================================"
echo "PERT Calibration System - Release Preparation"
echo "======================================================================"
echo ""

# Step 1: Verify we're in the sanitized directory
echo "📁 Step 1: Verifying directory..."
if [[ ! -f "pert-calculator.py" ]] || [[ ! -f "LICENSE" ]]; then
    echo "❌ Error: Must run this script from the sanitized directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi
echo "✅ In sanitized directory"
echo ""

# Step 2: Test core functionality
echo "🧪 Step 2: Testing core functionality..."

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "   ❌ Python not found. Install Python 3.8+ and try again."
    exit 1
fi

# Test PERT calculator syntax
echo "   Testing PERT calculator..."
if $PYTHON_CMD -m py_compile pert-calculator.py 2>/dev/null; then
    echo "   ✅ PERT calculator syntax valid"
else
    echo "   ❌ PERT calculator syntax error"
fi

# Test plan outcome tracker syntax
echo "   Testing outcome tracker..."
if $PYTHON_CMD -m py_compile plan-outcome-tracker.py 2>/dev/null; then
    echo "   ✅ Outcome tracker syntax valid"
else
    echo "   ❌ Outcome tracker syntax error"
fi

# Test calibration report syntax
echo "   Testing calibration report..."
if $PYTHON_CMD -m py_compile calibration-report.py 2>/dev/null; then
    echo "   ✅ Calibration report syntax valid"
else
    echo "   ❌ Calibration report syntax error"
fi

# Test plan validation syntax
echo "   Testing plan validation..."
if $PYTHON_CMD -m py_compile validate-pert-plan.py 2>/dev/null; then
    echo "   ✅ Plan validation syntax valid"
else
    echo "   ❌ Plan validation syntax error"
fi

echo ""

# Step 3: Check for sensitive information
echo "🔍 Step 3: Checking for sensitive information..."
if grep -r "/home/rebelsts" . --exclude-dir=.git 2>/dev/null; then
    echo "⚠️  Warning: Found personal paths. Review before publishing."
else
    echo "✅ No personal paths found"
fi

if grep -r "rebelsts" . --exclude-dir=.git --exclude="prepare-release.sh" 2>/dev/null; then
    echo "⚠️  Warning: Found username references. Review before publishing."
else
    echo "✅ No username references found"
fi
echo ""

# Step 4: Verify required files
echo "📋 Step 4: Verifying required files..."
REQUIRED_FILES=(
    "pert-calculator.py"
    "plan-outcome-tracker.py"
    "calibration-report.py"
    "validate-pert-plan.py"
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
    "QUICKSTART.md"
    ".gitignore"
)

all_present=true
for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
        all_present=false
    fi
done

if [[ "$all_present" = true ]]; then
    echo "✅ All required files present"
else
    echo "❌ Some files missing"
    exit 1
fi
echo ""

# Step 5: Initialize git if not already done
echo "🔧 Step 5: Git initialization..."
if [[ -d ".git" ]]; then
    echo "⚠️  Git repository already initialized"
    echo "   Current branch: $(git branch --show-current)"
    echo "   Commits: $(git rev-list --count HEAD 2>/dev/null || echo '0')"
else
    echo "   Initializing git repository..."
    git init
    echo "✅ Git initialized"
fi
echo ""

# Step 6: Check git status
echo "📊 Step 6: Git status..."
git status --short
echo ""

# Step 7: Offer to create initial commit
echo "======================================================================"
echo "Pre-Release Checklist:"
echo "======================================================================"
echo ""
echo "Before publishing to GitHub, verify:"
echo ""
echo "  [ ] All tests passed above"
echo "  [ ] No sensitive information found"
echo "  [ ] All required files present"
echo "  [ ] README.md reviewed for clarity"
echo "  [ ] LICENSE is MIT (as stated in README)"
echo "  [ ] Examples work correctly"
echo ""
echo "Next steps:"
echo ""
echo "  1. Review RELEASE_NOTES.md for detailed instructions"
echo "  2. Create GitHub repository"
echo "  3. Add files: git add ."
echo "  4. Commit: git commit -m 'Initial release: PERT Calibration System v1.0'"
echo "  5. Push: git push -u origin main"
echo ""
echo "Ready to proceed? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Great! Run these commands when ready:"
    echo ""
    echo "  git add ."
    echo "  git commit -m 'Initial release: PERT Calibration System v1.0"
    echo ""
    echo "- Core PERT calculator with 5 risk factors"
    echo "- Outcome tracking and calibration reports"
    echo "- Plan validation with impact-based thresholds"
    echo "- Comprehensive documentation and examples"
    echo "- MIT License, zero external dependencies'"
    echo ""
    echo "  git remote add origin https://github.com/YOUR_USERNAME/pert-calibration-system.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
else
    echo ""
    echo "No problem! Review the files and run this script again when ready."
    echo ""
fi

echo "======================================================================"
echo "For detailed release instructions, see RELEASE_NOTES.md"
echo "======================================================================"
