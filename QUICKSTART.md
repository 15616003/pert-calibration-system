# Quick Start Guide

Get started with PERT Calibration System in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pert-calibration-system.git
cd pert-calibration-system

# No dependencies to install - uses Python stdlib only!
# Verify Python version (3.8+ required)
python --version
```

## Your First Estimation

### Step 1: Run Interactive Calculator

```bash
python pert-calculator.py
```

You'll be prompted to enter three-point estimates (Optimistic, Most Likely, Pessimistic) for each risk factor:

```
Enter risk factor estimates (Optimistic, Most Likely, Pessimistic)

COMPLEXITY (algorithm difficulty, edge cases)
  Optimistic (best case): 5
  Most Likely: 15
  Pessimistic (worst case): 30

DEPENDENCIES (external libraries, APIs)
  Optimistic: 0
  Most Likely: 10
  Pessimistic: 40

[... continues for all 5 factors ...]
```

### Step 2: Interpret Results

```
======================================================================
PERT Analysis: My First Phase
======================================================================

📊 OVERALL METRICS:
  Phase Risk:              16.7%
  Phase Success:           83.3%
  Total Standard Deviation: 26.7
  Confidence Width (±2σ):   53.4%

  85% Confident Success:   29.9%
  Verdict:                 ❌ FAIL <85%

⚠️  MITIGATION REQUIRED
```

**What this means**:
- Your phase has a **29.9% confident success rate** (below 85% threshold)
- You need to **research mitigation strategies** to reduce risk
- Focus on **high-variance factors** (marked with ⚠️ in breakdown)

### Step 3: Mitigation Research

The tool identifies high-risk factors:

```
DEPENDENCIES:
  O=0, M=10, P=40
  Score: 13.3 | SD: 6.7 | Weight: 0.20
  Weighted Risk: 2.7%
  ⚠️  HIGH VARIANCE - Priority for mitigation research
```

**Action**: Research dependency compatibility, test in dev environment, reduce P estimate based on findings.

### Step 4: Re-estimate After Mitigation

```bash
python pert-calculator.py \
  --complexity 5,15,30 \
  --dependencies 0,5,15 \    # Reduced P from 40 to 15
  --stack 10,20,50 \
  --knowledge 5,10,25 \
  --testing 5,15,35
```

New result:
```
  85% Confident Success:   96.2%
  Verdict:                 ✅ PASS ≥85%
```

**Success!** Your phase now meets the confidence threshold.

## Command-Line Shortcuts

### Quick Single-Phase Estimation

```bash
python pert-calculator.py \
  --complexity 5,15,30 \
  --dependencies 0,10,40 \
  --stack 10,20,50 \
  --knowledge 5,10,25 \
  --testing 5,15,35 \
  --phase "Phase 1: Setup"
```

### Batch Processing (Multiple Phases)

```bash
python pert-calculator.py --json-file examples/batch-assessment-example.json
```

Generates analysis for all phases plus summary table.

### Quick Mode (3 Factors for Impact 1-2)

```bash
python pert-calculator.py --quick-mode \
  --complexity 5,15,30 \
  --dependencies 0,10,40 \
  --testing 5,15,35
```

Uses only Complexity, Dependencies, and Testing factors.

## Tracking Outcomes

After implementing a plan, record the outcome for calibration:

```bash
# Interactive mode
python plan-outcome-tracker.py

# Quick mode
python plan-outcome-tracker.py \
  --plan my-plan.md \
  --outcome SUCCESS \
  --duration 6.5 \
  --notes "All phases completed as expected"
```

**Outcome types**:
- `SUCCESS` - All phases completed
- `PARTIAL` - Some phases completed
- `FAILURE` - Plan abandoned

## Calibration Reports

After tracking 20+ plans, generate a calibration report:

```bash
python calibration-report.py
```

Sample output:
```markdown
## Overall Statistics

| Metric | Value |
|--------|-------|
| Mean Predicted Confidence | 94.2% |
| Mean Actual Success Rate | 91.5% |
| Mean Calibration Error | +2.7% |
| System Status | ⚠️ OVERCONFIDENT |

## Multiplier Adjustment Recommendation

**Current Multiplier**: 2.00
**Recommended Multiplier**: 2.15 (+0.15 adjustment)
```

Follow the report's instructions to update the confidence multiplier in `pert-calculator.py`.

## Example Workflows

### Workflow 1: New Feature Estimation

```bash
# Step 1: Estimate phase
python pert-calculator.py --phase "Auth Implementation"

# Step 2: If fails, research mitigation
# Step 3: Re-estimate with reduced risk
# Step 4: Implement plan
# Step 5: Record outcome
python plan-outcome-tracker.py --plan auth-plan.md --outcome SUCCESS
```

### Workflow 2: Multi-Phase Project

```bash
# Create batch JSON file with all phases
# Run batch assessment
python pert-calculator.py --json-file my-project.json

# Review which phases need mitigation
# Research and update estimates
# Re-run until all phases ≥85%
```

### Workflow 3: Quarterly Calibration

```bash
# After 20+ tracked outcomes
python calibration-report.py

# Review calibration error
# Adjust multiplier if needed
# Continue tracking for next cycle
```

## Tips for Accurate Estimates

### Optimistic (O) - Best Case
- Everything goes perfectly
- No unexpected issues
- All assumptions prove correct

### Most Likely (M) - Realistic Case
- Normal development with typical minor issues
- Some research/debugging required
- Most assumptions hold

### Pessimistic (P) - Worst Case
- Major complications arise
- Significant unknowns discovered
- Multiple assumptions wrong

**Common Mistake**: Making P too extreme (catastrophizing). P should be "worst case within reason", not "meteor strikes datacenter".

## Impact Levels Guide

| Impact | Threshold | When to Use |
|--------|-----------|-------------|
| 1 | 75% | Learning, prototypes, throwaway code |
| 2 | 85% | Isolated features, cosmetic changes |
| 3 | 85% | User-facing non-critical features |
| 4 | 85% | Critical path, revenue-affecting |
| 5 | 85% | Security, compliance, PII handling |

Higher impact levels require **more rigorous mitigation research**.

## Common Issues

### "All my estimates fail the threshold"

**Causes**:
- Genuinely risky plans (too ambitious)
- Pessimistic P values (too extreme)
- Missing mitigation research

**Solutions**:
- Review P estimates for realism
- Conduct thorough mitigation research
- Consider de-scoping into smaller phases
- Use risk acceptance for prototypes (Impact 1)

### "Calibration shows large error"

**Causes**:
- Inconsistent outcome recording
- Selection bias (only tracking easy/hard plans)
- Estimation drift over time

**Solutions**:
- Define clear SUCCESS criteria
- Track ALL plans, not just successful ones
- Review estimation process for biases

## Next Steps

1. **Read the README**: Comprehensive documentation of methodology
2. **Review Examples**: Check `examples/` directory for sample files
3. **Join Discussions**: Ask questions on GitHub Discussions
4. **Contribute**: See CONTRIBUTING.md for guidelines

## Quick Reference

```bash
# Calculate confidence
python pert-calculator.py [--quick-mode] [--json-file FILE] [--phase NAME]

# Track outcome
python plan-outcome-tracker.py [--plan FILE] [--outcome SUCCESS|PARTIAL|FAILURE]

# Generate report
python calibration-report.py [--export CSV] [--adjust-multiplier]

# Validate plan file
python validate-pert-plan.py PLAN_FILE [--verbose]
```

## Support

- **Documentation**: README.md (comprehensive guide)
- **Examples**: `examples/` directory
- **Issues**: GitHub Issues tracker
- **Discussions**: GitHub Discussions

Happy estimating! 🎯
