# Changelog

All notable changes to the PERT Calibration System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2025-12-28 15:57 UTC
- **Batch Processing**: Process multiple phases in single JSON file with automatic plan generation
  - New `batch_mode()` function handles phase arrays
  - Auto-detects batch vs single-phase via 'phases' key
  - Generates summary table with confidence scores for all phases
  - Exit code 0 if all pass, 1 if any fail
  - Example file: `examples/batch-assessment-example.json`

- **Summary Table Validation**: Enforce summary section in plan files
  - New `_validate_summary_section()` method checks for summary headers
  - Validates table structure (Phase | Confidence | Status)
  - Warning-level severity (doesn't fail validation)
  - Suggests batch mode for consistency

### Changed - 2025-12-28 15:57 UTC
- **Confidence Threshold**: Reduced from 95% to 85% globally
  - Updated `CONFIDENCE_THRESHOLD` constant
  - Modified `IMPACT_THRESHOLDS` for all levels except Throwaway (Impact 1 = 75%)
  - Updated display strings ("95% Confident Success" → "85% Confident Success")
  - Updated regex patterns for confidence extraction
  - Documentation updated in README.md and CLAUDE.md

- **Research Iterations**: Reduced maximum from 2 to 1
  - Updated `MAX_ITERATIONS` constant
  - Reflects diminishing returns research findings
  - Documentation updated to reflect new limit

### Technical Details - 2025-12-28 15:57 UTC
- Files modified:
  - `pert-calculator.py`: Batch mode, threshold updates, display strings (lines 28-29, 52, 207-219, 316-444, 523-529)
  - `validate-pert-plan.py`: Thresholds, iterations, summary validation (lines 24-30, 33, 104, 135, 326-359, 456, 459)
  - `README.md`: All threshold references updated
  - `CLAUDE.md`: Developer guide updated with new thresholds and limits
  - `examples/batch-assessment-example.json`: Created comprehensive example

- Backward compatibility maintained:
  - Single-phase JSON files still work
  - Interactive mode unchanged
  - All existing PERT formulas preserved

## [1.0.0] - Initial Release

### Added
- Pure PERT calculation engine with beta distribution
- Three-point estimation (O, M, P)
- Five risk factors: Complexity, Dependencies, Stack Compatibility, Knowledge, Testing
- Plan outcome tracking system
- Calibration report with multiplier recommendations
- Impact-based threshold validation (5 levels)
- Risk acceptance workflow
- Command-line, interactive, and JSON modes
