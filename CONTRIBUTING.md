# Contributing to PERT Calibration System

Thank you for your interest in contributing to the PERT Calibration System! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Guidelines](#development-guidelines)
- [Pull Request Process](#pull-request-process)
- [Statistical Integrity Guidelines](#statistical-integrity-guidelines)

## Code of Conduct

This project adheres to a code of professional conduct. By participating, you are expected to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Sample input** that triggers the bug
- **Error messages or output** (full stack traces)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear use case** describing why this enhancement would be useful
- **Detailed description** of the proposed functionality
- **Examples** of how it would work
- **Potential impact** on existing functionality

### Documentation Improvements

Documentation improvements are always appreciated:

- Fix typos or clarify confusing sections
- Add examples or usage patterns
- Improve code comments and docstrings
- Translate documentation (if multilingual support added)

## Development Guidelines

### Prerequisites

- Python 3.8 or higher
- Git for version control
- Familiarity with PERT methodology (see README)

### Setting Up Development Environment

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pert-calibration-system.git
cd pert-calibration-system

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Test your changes thoroughly

# Commit with descriptive messages
git commit -m "Add feature: brief description"

# Push to your fork
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

### Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and return values
- Add **docstrings** to all functions, classes, and modules
- Keep functions **focused and small** (<50 lines when possible)
- Use **descriptive variable names** (avoid single letters except for loops)

**Example**:
```python
def calculate_pert_score(optimistic: float, most_likely: float,
                        pessimistic: float) -> tuple[float, float]:
    """
    Calculate PERT score and standard deviation.

    Args:
        optimistic: Best-case estimate (O)
        most_likely: Most likely estimate (M)
        pessimistic: Worst-case estimate (P)

    Returns:
        Tuple of (score, standard_deviation)

    Formula:
        Score = (O + 4×M + P) / 6
        SD = (P - O) / 6
    """
    score = (optimistic + 4 * most_likely + pessimistic) / 6
    sd = (pessimistic - optimistic) / 6
    return score, sd
```

### Testing

- Test all code paths manually before submitting
- Include **usage examples** in commit messages
- Test with both **valid and invalid inputs**
- Verify behavior matches documentation

**Testing Checklist**:
```bash
# Test PERT calculator
python pert-calculator.py --complexity 5,15,30 --dependencies 0,10,40 \
  --stack 10,20,50 --knowledge 5,10,25 --testing 5,15,35

# Test batch processing
python pert-calculator.py --json-file examples/batch-assessment-example.json

# Test outcome tracker
python plan-outcome-tracker.py --list

# Test calibration report
python calibration-report.py --adjust-multiplier
```

### Commit Messages

Use clear, descriptive commit messages:

```
Add feature: JWT authentication risk factors

- Add authentication-specific risk factors
- Update weights to account for security complexity
- Include examples in documentation

Resolves #42
```

**Format**:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed explanation with bullet points
- Reference issue numbers if applicable

## Pull Request Process

### Before Submitting

1. **Update documentation** if you've changed functionality
2. **Test thoroughly** with various inputs
3. **Follow code style** guidelines
4. **Update CHANGELOG.md** with your changes
5. **Ensure zero external dependencies** (stdlib only)

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Motivation and Context
Why is this change needed? What problem does it solve?

## Testing
How has this been tested? Include test commands and outputs.

## Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Zero external dependencies maintained
- [ ] All tests pass
```

### Review Process

1. Maintainers will review your PR within 1-2 weeks
2. Address any feedback or requested changes
3. Once approved, maintainers will merge your PR
4. Your contribution will be included in the next release!

## Statistical Integrity Guidelines

**CRITICAL**: This project prioritizes statistical rigor. The following changes require **strong justification**:

### ❌ DO NOT Change Without Justification

1. **PERT Formulas** (`pert-calculator.py` lines ~81-82, ~147-148)
   - Pure beta distribution formulas
   - No weighted averages, heuristics, or curves
   - Changes must cite peer-reviewed statistical literature

2. **Risk Factor Weights** (`pert-calculator.py` lines ~32-38)
   - Based on project management research
   - Must sum to 1.0
   - Changes require empirical validation across 50+ projects

3. **Confidence Threshold** (85%)
   - Established through empirical testing
   - Changes affect all users' calibration
   - Requires strong statistical justification

### ✅ OK to Modify (With Calibration)

1. **CONFIDENCE_MULTIPLIER** (`pert-calculator.py` line ~48)
   - Adjustable based on empirical calibration
   - Document changes in `multiplier-history.txt`
   - Include calibration data supporting the change

2. **User Interface Improvements**
   - Output formatting
   - CLI argument parsing
   - Error messages
   - Documentation

3. **Data Storage Formats**
   - As long as backward compatibility maintained
   - Provide migration scripts for existing users

### Statistical Contributions Welcome

- **Calibration algorithm improvements** (with validation data)
- **Bucket analysis enhancements** (statistical soundness required)
- **Additional risk factors** (with weight derivation explanation)
- **Alternative confidence interval methods** (with comparative analysis)

**Example of Good Statistical Contribution**:
```python
# Proposed: Add correlation analysis between risk factors
# Justification: Detected systematic correlation between Complexity
# and Testing (r=0.78) across 100 tracked outcomes
# Impact: May improve confidence accuracy by 3-5%
# Validation: Tested on holdout set of 30 plans
# Trade-offs: Adds computational complexity, requires NumPy dependency
```

## Questions?

- **Issues**: GitHub Issues tracker
- **Discussions**: GitHub Discussions
- **Documentation**: README.md and inline docstrings

Thank you for contributing to PERT Calibration System!
