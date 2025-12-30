---
name: Feature Request
about: Suggest an enhancement or new feature
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description

A clear and concise description of the feature you'd like to see.

## Use Case

Describe the problem this feature would solve or the workflow it would improve.

**Example Scenario**:
> "As a project manager estimating multiple similar projects, I want to save risk factor templates so that I can quickly estimate similar phases without re-entering values each time."

## Proposed Solution

How would you like this feature to work?

**Example**:
```bash
# Save risk factor template
python pert-calculator.py --save-template database-migration.json \
  --complexity 10,20,40 --dependencies 5,15,30 ...

# Use saved template
python pert-calculator.py --template database-migration.json
```

## Alternatives Considered

Describe any alternative solutions or workarounds you've considered.

## Benefits

- **Time savings**: How much time would this save?
- **Accuracy improvement**: Would this improve estimation quality?
- **User experience**: How would this improve usability?

## Statistical Impact

(If applicable) Does this feature affect:
- [ ] PERT formulas or calculations
- [ ] Risk factor weights
- [ ] Confidence intervals
- [ ] Calibration algorithm
- [ ] None of the above (UI/UX only)

**If statistical impact**: Please provide justification or research supporting the change.

## Implementation Complexity

(Optional) Your assessment of implementation difficulty:
- [ ] Low (cosmetic/UI change)
- [ ] Medium (new functionality, no formula changes)
- [ ] High (requires statistical validation)
- [ ] Unknown

## Additional Context

Add any other context, mockups, or examples about the feature request.
