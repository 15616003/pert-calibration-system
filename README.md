# PERT Calibration System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/kt2saint-sec/pert-calibration-system)](https://github.com/kt2saint-sec/pert-calibration-system/releases)
[![Issues](https://img.shields.io/github/issues/kt2saint-sec/pert-calibration-system)](https://github.com/kt2saint-sec/pert-calibration-system/issues)
[![Stars](https://img.shields.io/github/stars/kt2saint-sec/pert-calibration-system?style=social)](https://github.com/kt2saint-sec/pert-calibration-system/stargazers)
[![Discussions](https://img.shields.io/github/discussions/kt2saint-sec/pert-calibration-system)](https://github.com/kt2saint-sec/pert-calibration-system/discussions)

A statistically rigorous PERT (Program Evaluation and Review Technique) calculator with empirical calibration for estimating plan success probability without historical data.

## Overview

This system provides a **no-shortcuts** approach to project planning confidence estimation:
- ❌ NO weighted averages
- ❌ NO arbitrary heuristics
- ❌ NO curves or data skewing
- ✅ Pure PERT formulas (beta distribution)
- ✅ 95% confidence intervals
- ✅ Self-calibrating through outcome tracking

### Key Features

1. **PERT Calculator** (`pert-calculator.py`)
   - Three-point estimation (Optimistic, Most Likely, Pessimistic)
   - 5 risk factors: Complexity, Dependencies, Stack Compatibility, Knowledge, Testing
   - Statistical confidence intervals (±2σ for 95% CI)
   - Command-line, interactive, and JSON modes

2. **Outcome Tracker** (`plan-outcome-tracker.py`)
   - Record actual plan implementation outcomes
   - Extract predicted confidence from plan files
   - JSONL database for crash-safe append-only tracking
   - Interactive and quick CLI modes

3. **Calibration Report** (`calibration-report.py`)
   - Analyze predicted vs actual success rates
   - Bucket analysis by confidence score ranges
   - Automatic multiplier adjustment recommendations
   - Markdown reports with actionable insights

## Methodology

### PERT Formulas

For each risk factor with estimates O (Optimistic), M (Most Likely), P (Pessimistic):

```
Score = (O + 4×M + P) / 6
Standard Deviation (SD) = (P - O) / 6
```

### Confidence Calculation

```
Phase Risk = Σ(Score × Weight)
Phase Success = 100 - Phase Risk
Confidence Width = MULTIPLIER × Total_SD
85% Confident Success = Phase Success - Confidence Width
```

### Risk Factor Weights

| Factor | Weight | Description |
|--------|--------|-------------|
| Complexity | 0.25 | Algorithm difficulty, edge cases |
| Dependencies | 0.20 | External libraries, APIs, version compatibility |
| Stack Compatibility | 0.25 | Tested vs untested on current system |
| Knowledge | 0.15 | Familiar vs novel territory |
| Testing | 0.15 | Verification feasibility |

### Calibration Loop

The system self-improves through empirical validation:

1. **Predict**: Use PERT to estimate plan confidence (e.g., 85%)
2. **Implement**: Execute the plan
3. **Record**: Track actual outcome (SUCCESS/PARTIAL/FAILURE)
4. **Analyze**: Compare predicted vs actual across multiple plans
5. **Adjust**: If systematic bias detected, update confidence multiplier
6. **Repeat**: Continue calibration cycle

**Example**: If plans predicted at 95% confidence actually succeed only 87% of the time, the system recommends increasing the multiplier from 2.0 to 2.15 (widening confidence intervals to be more conservative).

## Installation

### Prerequisites

- Python 3.8+
- No external dependencies (uses only Python stdlib)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pert-calibration-system.git
cd pert-calibration-system

# Make scripts executable (optional)
chmod +x pert-calculator.py plan-outcome-tracker.py calibration-report.py

# Test installation
python pert-calculator.py --help
```

### Directory Structure

The calibration system uses the following directory structure (created automatically):

```
~/.claude/plans/.calibration/
├── outcomes.jsonl              # Main outcomes database
├── outcomes-backup.jsonl       # Weekly backup
├── reports/
│   ├── YYYY-MM-DD-calibration-report.md
│   └── latest-report.md → [latest report symlink]
└── multiplier-history.txt      # Adjustment changelog
```

## Usage

### 1. PERT Calculator

#### Interactive Mode

```bash
python pert-calculator.py
```

You'll be prompted to enter three-point estimates for each of the 5 risk factors.

#### Command-Line Mode

```bash
python pert-calculator.py \
  --complexity 5,15,30 \
  --dependencies 0,10,40 \
  --stack 10,20,50 \
  --knowledge 5,10,25 \
  --testing 5,15,35 \
  --phase "Phase 1: JWT Authentication"
```

#### JSON Input Mode

```bash
python pert-calculator.py --json '{
  "complexity": {"O": 5, "M": 15, "P": 30},
  "dependencies": {"O": 0, "M": 10, "P": 40},
  "stack_compat": {"O": 10, "M": 20, "P": 50},
  "knowledge": {"O": 5, "M": 10, "P": 25},
  "testing": {"O": 5, "M": 15, "P": 35}
}'
```

#### JSON File Input

```bash
python pert-calculator.py --json-file risk-assessment.json
```

**Example `risk-assessment.json`**:
```json
{
  "phase_name": "JWT Authentication Implementation",
  "risk_factors": {
    "complexity": {"O": 5, "M": 15, "P": 30},
    "dependencies": {"O": 0, "M": 10, "P": 40},
    "stack_compat": {"O": 10, "M": 20, "P": 50},
    "knowledge": {"O": 5, "M": 10, "P": 25},
    "testing": {"O": 5, "M": 15, "P": 35}
  }
}
```

#### Example Output

```
======================================================================
PERT Analysis: JWT Authentication Implementation
======================================================================

📊 OVERALL METRICS:
  Phase Risk:              16.7%
  Phase Success:           83.3%
  Total Standard Deviation: 26.7
  Confidence Width (±2σ):   53.4%

  85% Confident Success:   29.9%
  Verdict:                 ❌ FAIL <85%

⚠️  MITIGATION REQUIRED:
  1. Identify highest-variance risk factors
  2. Research mitigation strategies
  3. Re-estimate with mitigation
  4. Repeat until ≥85% or declare infeasible

──────────────────────────────────────────────────────────────────────
📋 RISK FACTOR BREAKDOWN:

  DEPENDENCIES:
    O=0, M=10, P=40
    Score: 13.3 | SD: 6.7 | Weight: 0.20
    Weighted Risk: 2.7%
    ⚠️  HIGH VARIANCE - Priority for mitigation research

  STACK COMPAT:
    O=10, M=20, P=50
    Score: 23.3 | SD: 6.7 | Weight: 0.25
    Weighted Risk: 5.8%
    ⚠️  HIGH VARIANCE - Priority for mitigation research

  [... other factors ...]
======================================================================
```

### 2. Plan Outcome Tracker

After implementing a plan, record the actual outcome for calibration.

#### Interactive Mode

```bash
python plan-outcome-tracker.py
```

#### Quick Mode

```bash
python plan-outcome-tracker.py \
  --plan my-implementation-plan.md \
  --outcome SUCCESS \
  --duration 6.5 \
  --notes "All phases completed as expected"
```

**Outcome Types**:
- `SUCCESS`: All phases completed as expected
- `PARTIAL`: Some phases completed, others failed/deferred
- `FAILURE`: Plan abandoned or completely failed

#### List Tracked Plans

```bash
python plan-outcome-tracker.py --list
```

**Example Output**:
```
📊 Tracked Plans (15 total)

Plan Name                                Predicted    Actual       Date
================================================================================
JWT Authentication Implementation        95.2%        SUCCESS      2025-12-20
Redis Cache Integration                  88.5%        PARTIAL      2025-12-22
API Rate Limiting                        96.8%        SUCCESS      2025-12-23
```

### 3. Calibration Report

Generate calibration analysis and multiplier recommendations.

#### Full Report

```bash
python calibration-report.py
```

#### Export to CSV

```bash
python calibration-report.py --export outcomes.csv
```

#### Multiplier Recommendation Only

```bash
python calibration-report.py --adjust-multiplier
```

#### Custom Current Multiplier

```bash
python calibration-report.py --current-multiplier 2.15
```

**Example Report Output**:

```markdown
# PERT Calibration Report
**Generated**: 2025-12-27 19:14 UTC
**Sample Size**: 25 completed plans

## Overall Statistics

| Metric | Value |
|--------|-------|
| Mean Predicted Confidence | 94.2% |
| Mean Actual Success Rate | 91.5% |
| Mean Calibration Error | +2.7% |
| System Status | ⚠️ OVERCONFIDENT |

## Confidence Bucket Analysis

| Predicted Range | Count | Avg Predicted | Actual Success | Calibration Error |
|----------------|-------|---------------|----------------|-------------------|
| 94-96%         |    12 |          95.1% |          91.7% |             +3.4% |
| 96-98%         |     8 |          97.2% |          93.8% |             +3.4% |
| 98-100%        |     5 |          98.6% |          96.0% |             +2.6% |

## Multiplier Adjustment Recommendation

**Current Multiplier**: 2.00
**Recommended Multiplier**: 2.15 (+0.15 adjustment)

**Reason**: System is overconfident by 2.7%. Recommendation: widening confidence interval (2.00 → 2.15)

**Action Required**:

1. Update `pert-calculator.py` line ~48:
   ```python
   CONFIDENCE_MULTIPLIER = 2.15  # Updated from 2.00
   ```

2. Log this adjustment:
   ```bash
   echo "2025-12-27: 2.00 → 2.15 (calibration error: +2.7%)" >> multiplier-history.txt
   ```

3. Continue tracking outcomes for next calibration cycle
```

## Workflow Example

### Step 1: Estimate Plan Confidence

```bash
python pert-calculator.py --phase "JWT Auth" \
  --complexity 5,15,30 \
  --dependencies 0,10,40 \
  --stack 10,20,50 \
  --knowledge 5,10,25 \
  --testing 5,15,35
```

**Output**: `85% Confident Success: 29.9%` ❌

### Step 2: Mitigation Research

Identify high-variance factors (Dependencies, Stack Compat) and research:
- Dependencies: Find well-tested JWT library for your stack
- Stack Compat: Test library in dev environment first

### Step 3: Re-estimate with Mitigation

```bash
python pert-calculator.py --phase "JWT Auth (mitigated)" \
  --complexity 5,15,30 \
  --dependencies 0,5,15 \    # Reduced after confirming library
  --stack 15,20,30 \          # Reduced after dev testing
  --knowledge 5,10,25 \
  --testing 5,15,35
```

**Output**: `85% Confident Success: 96.2%` ✅

### Step 4: Implement Plan

Proceed with implementation based on mitigated estimates.

### Step 5: Record Outcome

```bash
python plan-outcome-tracker.py \
  --plan jwt-auth-plan.md \
  --outcome SUCCESS \
  --duration 6.5 \
  --notes "Completed all phases, minor CORS issue resolved"
```

### Step 6: Quarterly Calibration

After tracking 20+ plans:

```bash
python calibration-report.py
```

Review calibration error and adjust multiplier if needed.

## Configuration

### Confidence Multiplier

Default: `2.0` (±2 standard deviations for 95% CI)

To adjust based on calibration report recommendations:

1. Edit `pert-calculator.py` line ~48:
   ```python
   CONFIDENCE_MULTIPLIER = 2.15  # Range: [1.5, 3.0]
   ```

2. Log the change:
   ```bash
   echo "$(date -I): 2.00 → 2.15 (reason: calibration error +2.7%)" \
     >> ~/.claude/plans/.calibration/multiplier-history.txt
   ```

### Risk Factor Weights

**DO NOT MODIFY** unless you have strong statistical justification.

Current weights in `pert-calculator.py` line ~32-38:
```python
WEIGHTS = {
    'complexity': 0.25,
    'dependencies': 0.20,
    'stack_compat': 0.25,
    'knowledge': 0.15,
    'testing': 0.15
}
```

## Calibration Guidelines

### Minimum Sample Size

- **5 plans**: Minimal viable calibration (unreliable)
- **20 plans**: Recommended minimum for meaningful adjustments
- **50+ plans**: Robust calibration

### Calibration Frequency

- **After 20 plans**: First calibration check
- **Quarterly**: Re-run calibration every 3 months
- **After major changes**: If you change methodology, project types, or team composition

### Interpretation

**Calibration Error**:
- `+X%`: Overconfident (predictions higher than reality) → Increase multiplier
- `-X%`: Underconfident (predictions lower than reality) → Decrease multiplier
- `±2%`: Well-calibrated → No adjustment needed

**Adjustment Algorithm**:
```
adjustment_factor = -mean_error / 2.5 × 0.05
new_multiplier = current_multiplier + adjustment_factor
new_multiplier = clamp(new_multiplier, 1.5, 3.0)
```

## Troubleshooting

### Plans Always Failing Threshold

**Symptom**: Every plan shows `<85%` confidence even after mitigation research.

**Causes**:
1. **Genuinely risky plans**: Plans may actually be too ambitious
2. **Pessimistic estimates**: P (Pessimistic) values may be too high
3. **Risk accumulation**: Multiple moderate risks compound

**Solutions**:
- Review P estimates for realism (not worst-case catastrophizing)
- Consider de-scoping plan into smaller, lower-risk phases
- Accept documented risk for prototype/learning projects

### Calibration Shows Large Error

**Symptom**: Calibration error >10% after 20+ plans.

**Causes**:
1. **Inconsistent outcome recording**: Mixing SUCCESS criteria across plans
2. **Selection bias**: Only tracking easy or hard plans, not representative sample
3. **Estimation drift**: Estimation quality varying over time

**Solutions**:
- Define clear SUCCESS criteria before tracking
- Track ALL plans, not just successful or failed ones
- Review estimation process for systematic biases

### Multiplier Adjustment Not Improving

**Symptom**: After adjusting multiplier, calibration error persists.

**Causes**:
1. **Insufficient new data**: Need 10+ plans after adjustment for measurement
2. **Systematic estimation bias**: Issue isn't confidence width, but estimate accuracy
3. **Plan heterogeneity**: Mixing very different project types

**Solutions**:
- Track 15-20 plans before re-calibrating
- Review O/M/P estimation process, not just multiplier
- Consider separate calibration for different project types

## Contributing

Contributions are welcome! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Maintain zero external dependencies (Python stdlib only)
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include usage examples in commit messages
- **NO shortcuts**: Preserve pure PERT formulas, no heuristics

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- PERT methodology based on classic project management literature
- Beta distribution formulas from statistical estimation theory
- Calibration approach inspired by Brier score evaluation

## FAQ

### Q: Why no machine learning or historical data?

**A**: This system is designed to work **out-of-the-box** without training data. ML models require large datasets and can overfit to past projects. PERT uses expert judgment calibrated through outcome tracking, making it suitable for novel projects and small teams.

### Q: Can I use this for non-software projects?

**A**: Yes! The 5 risk factors are generic enough for any project type. Adjust factor interpretations:
- **Complexity** → Task difficulty
- **Dependencies** → External constraints
- **Stack Compat** → Tool/resource familiarity
- **Knowledge** → Domain expertise
- **Testing** → Verification method

### Q: What if my confidence is <85% after research?

**A**: You have three options:
1. **Accept documented risk**: Use risk acceptance workflow for prototypes/learning
2. **De-scope plan**: Remove high-risk phases, implement incrementally
3. **Abort plan**: Declare infeasible, propose alternatives

### Q: How do I handle multi-phase plans?

**A**: Run PERT for each phase independently. Overall plan confidence = minimum of all phase confidences (weakest link). This identifies which phases need mitigation research.

### Q: Can I customize risk factor weights?

**A**: Only with strong statistical justification. Current weights are derived from project management research. If you customize, track calibration separately and document your reasoning.

## Support

- **Issues**: GitHub Issues tracker
- **Discussions**: GitHub Discussions
- **Documentation**: This README + inline code docstrings

## Changelog

See `CHANGELOG.md` for version history.

## Roadmap

- [ ] Web UI for easier interaction
- [ ] Export to PDF/Excel
- [ ] Multi-project calibration tracking
- [ ] Risk factor correlation analysis
- [ ] Integrations with project management tools
