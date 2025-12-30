#!/usr/bin/env python3
"""
PERT Plan Validation Script
Validates implementation plan files for PERT methodology compliance.

Usage:
    # Validate single plan
    python validate-pert-plan.py my-plan.md

    # Validate all plans in directory
    python validate-pert-plan.py --dir ~/.claude/plans/

    # Show validation report
    python validate-pert-plan.py my-plan.md --verbose
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Impact-based thresholds (85% standard, 75% for throwaway)
IMPACT_THRESHOLDS = {
    1: 75.0,   # Throwaway (experimental work)
    2: 85.0,   # Low-Risk
    3: 85.0,   # Medium-Impact
    4: 85.0,   # High-Impact
    5: 85.0    # Mission-Critical
}

# Maximum research iterations
MAX_ITERATIONS = 1

# Required risk factors by mode
REQUIRED_FACTORS_QUICK = {'complexity', 'dependencies', 'testing'}
REQUIRED_FACTORS_FULL = {'complexity', 'dependencies', 'stack_compat', 'knowledge', 'testing'}

# Weight configurations
WEIGHTS_3_FACTOR = {
    'complexity': 0.40,
    'dependencies': 0.35,
    'testing': 0.25
}

WEIGHTS_5_FACTOR = {
    'complexity': 0.25,
    'dependencies': 0.20,
    'stack_compat': 0.25,
    'knowledge': 0.15,
    'testing': 0.15
}


class ValidationError:
    """Represents a validation error with severity."""
    def __init__(self, severity: str, message: str, line_num: Optional[int] = None):
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message
        self.line_num = line_num

    def __str__(self):
        prefix = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }.get(self.severity, '•')

        location = f" (line {self.line_num})" if self.line_num else ""
        return f"{prefix} {self.severity.upper()}{location}: {self.message}"


class PlanValidator:
    """Validates PERT plan files for methodology compliance."""

    def __init__(self, plan_path: Path):
        self.plan_path = plan_path
        self.content = plan_path.read_text()
        self.lines = self.content.split('\n')
        self.errors: List[ValidationError] = []

        # Extracted metadata
        self.impact_level: Optional[int] = None
        self.phases: List[Dict] = []
        self.has_risk_acceptance = False
        self.research_iterations = 0

    def validate(self) -> Tuple[bool, List[ValidationError]]:
        """Run all validation checks. Returns (is_valid, errors)."""

        # Extract metadata first
        self._extract_impact_level()
        self._extract_phases()
        self._check_risk_acceptance()
        self._check_research_iterations()

        # Run validation checks
        self._validate_impact_level()
        self._validate_phase_structure()
        self._validate_confidence_scores()
        self._validate_risk_factors()
        self._validate_approval_gate()
        self._validate_research_iterations()
        self._validate_summary_section()

        # Determine overall validity
        has_errors = any(e.severity == 'error' for e in self.errors)
        return (not has_errors, self.errors)

    def _extract_impact_level(self):
        """Extract impact level from plan frontmatter or content."""
        # Try frontmatter first (YAML format)
        frontmatter_match = re.search(r'---\s*\n(.*?)\n---', self.content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            impact_match = re.search(r'impact[_-]?level:\s*(\d)', frontmatter, re.IGNORECASE)
            if impact_match:
                self.impact_level = int(impact_match.group(1))
                return

        # Try inline format
        impact_match = re.search(r'\*\*Impact Level\*\*:\s*(\d)', self.content, re.IGNORECASE)
        if impact_match:
            self.impact_level = int(impact_match.group(1))
            return

        # Try header format
        impact_match = re.search(r'Impact:\s*Level\s*(\d)', self.content, re.IGNORECASE)
        if impact_match:
            self.impact_level = int(impact_match.group(1))

    def _extract_phases(self):
        """Extract all phases and their confidence scores from plan."""
        # Match only actual phase headers like "## Phase 1:", "## Phase 2:", etc.
        phase_pattern = r'^##\s+Phase\s+\d+:.*?$'
        confidence_pattern = r'85%\s+Confident\s+Success:\s*([-]?\d+\.?\d*)%'

        phase_matches = list(re.finditer(phase_pattern, self.content, re.MULTILINE))

        # Extract confidence scores and map them to phases
        # Find confidence scores that appear after each phase header
        for phase_match in phase_matches:
            phase_name = phase_match.group(0).strip()
            phase_start = phase_match.end()

            # Find the next phase or end of document
            next_phase_match = re.search(phase_pattern, self.content[phase_start:], re.MULTILINE)
            phase_end = phase_start + next_phase_match.start() if next_phase_match else len(self.content)

            # Look for confidence score in this phase section
            phase_content = self.content[phase_start:phase_end]
            confidence_match = re.search(confidence_pattern, phase_content, re.IGNORECASE)
            confidence = float(confidence_match.group(1)) if confidence_match else None

            self.phases.append({
                'name': phase_name,
                'confidence': confidence,
                'line_num': self.content[:phase_match.start()].count('\n') + 1
            })

    def _check_risk_acceptance(self):
        """Check if plan has risk acceptance section."""
        self.has_risk_acceptance = bool(re.search(
            r'##\s+Risk\s+Acceptance|##\s+Manual\s+Risk\s+Acceptance',
            self.content,
            re.IGNORECASE
        ))

    def _check_research_iterations(self):
        """Count research iterations in plan."""
        # Check frontmatter for iterations
        frontmatter_match = re.search(r'---\s*\n(.*?)\n---', self.content, re.DOTALL)
        if frontmatter_match:
            iterations_match = re.search(r'iterations:\s*(\d+)', frontmatter_match.group(1))
            if iterations_match:
                self.research_iterations = int(iterations_match.group(1))
                return

        # Count mitigation research sections
        research_sections = len(re.findall(
            r'###\s+(?:Mitigation\s+Research|Research\s+Iteration)',
            self.content,
            re.IGNORECASE
        ))
        self.research_iterations = research_sections

    def _validate_impact_level(self):
        """Validate impact level is present and valid."""
        if self.impact_level is None:
            self.errors.append(ValidationError(
                'error',
                'Impact level not found. Plan must specify impact level (1-5)'
            ))
        elif self.impact_level not in range(1, 6):
            self.errors.append(ValidationError(
                'error',
                f'Invalid impact level: {self.impact_level}. Must be 1-5'
            ))

    def _validate_phase_structure(self):
        """Validate phase structure and naming."""
        if not self.phases:
            self.errors.append(ValidationError(
                'warning',
                'No phases found in plan. Expected "## Phase N:" headers'
            ))

    def _validate_confidence_scores(self):
        """Validate confidence scores meet impact-based thresholds."""
        if self.impact_level is None:
            return

        threshold = IMPACT_THRESHOLDS.get(self.impact_level, 95.0)

        for phase in self.phases:
            if phase['confidence'] is None:
                self.errors.append(ValidationError(
                    'error',
                    f"Phase '{phase['name']}' missing confidence score",
                    phase['line_num']
                ))
                continue

            if phase['confidence'] < threshold:
                # Check if risk acceptance workflow is used
                if not self.has_risk_acceptance:
                    if self.impact_level in [1, 2]:
                        # Impact 1-2: Warning only
                        self.errors.append(ValidationError(
                            'warning',
                            f"Phase '{phase['name']}' confidence {phase['confidence']:.1f}% < {threshold}% threshold. "
                            f"Consider risk acceptance or research for Impact {self.impact_level}",
                            phase['line_num']
                        ))
                    else:
                        # Impact 3-5: Error unless risk acceptance present
                        self.errors.append(ValidationError(
                            'error',
                            f"Phase '{phase['name']}' confidence {phase['confidence']:.1f}% < {threshold}% threshold. "
                            f"Required for Impact {self.impact_level}. Use risk acceptance workflow or research.",
                            phase['line_num']
                        ))

    def _validate_risk_factors(self):
        """Validate correct number of risk factors based on impact level."""
        if self.impact_level is None:
            return

        # Determine expected mode
        if self.impact_level in [1, 2]:
            expected_factors = REQUIRED_FACTORS_QUICK
            mode_name = "quick mode (3 factors)"
        else:
            expected_factors = REQUIRED_FACTORS_FULL
            mode_name = "full mode (5 factors)"

        # Check for risk assessment tables
        table_pattern = r'\|\s*Factor\s*\|\s*Weight\s*\|.*?\n\|[-\s|]+\n((?:\|.*?\n)+)'
        tables = re.findall(table_pattern, self.content, re.MULTILINE)

        if not tables:
            self.errors.append(ValidationError(
                'warning',
                f'No risk assessment tables found. Expected {mode_name} for Impact {self.impact_level}'
            ))
            return

        # Validate factors in tables
        for table_idx, table in enumerate(tables):
            found_factors = set()

            for factor in ['Complexity', 'Dependencies', 'Stack Compat', 'Knowledge', 'Testing']:
                if re.search(factor, table, re.IGNORECASE):
                    # Normalize to lowercase key format
                    factor_key = factor.lower().replace(' ', '_')
                    if factor_key == 'stack_compat':
                        factor_key = 'stack_compat'
                    found_factors.add(factor_key)

            # Check for missing required factors
            missing = expected_factors - found_factors
            if missing:
                self.errors.append(ValidationError(
                    'error',
                    f'Risk table {table_idx + 1}: Missing required factors for {mode_name}: {", ".join(missing)}'
                ))

            # Check for unexpected factors (5 factors in Impact 1-2)
            if self.impact_level in [1, 2]:
                extra = found_factors - expected_factors
                if extra:
                    self.errors.append(ValidationError(
                        'warning',
                        f'Risk table {table_idx + 1}: Found {len(found_factors)} factors but Impact {self.impact_level} should use 3-factor quick mode. '
                        f'Extra factors: {", ".join(extra)}'
                    ))

    def _validate_approval_gate(self):
        """Validate plan approval gate requirements."""
        if not self.phases:
            return

        # Check if all phases meet threshold OR risk acceptance is documented
        if self.impact_level is None:
            return

        threshold = IMPACT_THRESHOLDS.get(self.impact_level, 95.0)
        below_threshold = [p for p in self.phases if p['confidence'] and p['confidence'] < threshold]

        if below_threshold and not self.has_risk_acceptance:
            if self.impact_level in [3, 4, 5]:
                self.errors.append(ValidationError(
                    'error',
                    f'{len(below_threshold)} phase(s) below {threshold}% threshold without risk acceptance documentation. '
                    f'Required for Impact {self.impact_level}. Add Risk Acceptance section or achieve threshold.'
                ))

    def _validate_research_iterations(self):
        """Validate research iteration count doesn't exceed maximum."""
        if self.research_iterations > MAX_ITERATIONS:
            self.errors.append(ValidationError(
                'warning',
                f'Found {self.research_iterations} research iterations. Recommended maximum is {MAX_ITERATIONS} '
                f'(diminishing returns beyond 2-3 cycles)'
            ))

    def _validate_summary_section(self):
        """Validate presence of Overall Plan Confidence Summary section."""
        # Check for summary header (various formats)
        summary_header_patterns = [
            r'##\s+Overall\s+Plan\s+(?:Confidence\s+)?Summary',
            r'##\s+Plan\s+Summary',
            r'##\s+Summary'
        ]

        has_summary_header = False
        for pattern in summary_header_patterns:
            if re.search(pattern, self.content, re.IGNORECASE):
                has_summary_header = True
                break

        if not has_summary_header:
            self.errors.append(ValidationError(
                'warning',
                'No "Overall Plan Confidence Summary" section found. '
                'Batch processing generates this automatically. '
                'Consider using batch mode for consistency.'
            ))
            return

        # Check for table structure (Phase | Confidence | Status)
        table_pattern = r'\|\s*Phase\s*\|.*Confidence.*\|.*Status.*\|'
        has_table = bool(re.search(table_pattern, self.content, re.IGNORECASE))

        if not has_table:
            self.errors.append(ValidationError(
                'warning',
                'Summary section found but table structure missing. '
                'Expected: "| Phase | Confidence | Status |"'
            ))


def validate_plan(plan_path: Path, verbose: bool = False) -> bool:
    """Validate a single plan file."""
    if not plan_path.exists():
        print(f"❌ Error: Plan file not found: {plan_path}")
        return False

    print(f"\n{'='*70}")
    print(f"Validating: {plan_path.name}")
    print(f"{'='*70}\n")

    validator = PlanValidator(plan_path)
    is_valid, errors = validator.validate()

    # Display metadata
    if verbose or validator.impact_level:
        print("📋 Plan Metadata:")
        print(f"  Impact Level: {validator.impact_level or 'Not specified'}")
        if validator.impact_level:
            threshold = IMPACT_THRESHOLDS[validator.impact_level]
            print(f"  Required Threshold: {threshold}%")
            mode = "Quick (3 factors)" if validator.impact_level in [1, 2] else "Full (5 factors)"
            print(f"  Expected Mode: {mode}")
        print(f"  Phases Found: {len(validator.phases)}")
        print(f"  Research Iterations: {validator.research_iterations}")
        print(f"  Risk Acceptance: {'Yes' if validator.has_risk_acceptance else 'No'}")
        print()

    # Display errors by severity
    if errors:
        error_count = sum(1 for e in errors if e.severity == 'error')
        warning_count = sum(1 for e in errors if e.severity == 'warning')
        info_count = sum(1 for e in errors if e.severity == 'info')

        print(f"📊 Validation Results: {error_count} errors, {warning_count} warnings, {info_count} info\n")

        for error in errors:
            print(str(error))
        print()

    # Summary
    if is_valid:
        print("✅ Plan is valid")
    else:
        print("❌ Plan has validation errors")

    return is_valid


def validate_directory(directory: Path, verbose: bool = False) -> Tuple[int, int]:
    """Validate all .md files in directory. Returns (valid_count, total_count)."""
    plan_files = list(directory.glob('*.md'))

    if not plan_files:
        print(f"⚠️  No .md files found in {directory}")
        return 0, 0

    print(f"\n📁 Validating {len(plan_files)} plan files in {directory}\n")

    valid_count = 0
    for plan_file in plan_files:
        if validate_plan(plan_file, verbose):
            valid_count += 1
        print()

    print(f"\n{'='*70}")
    print(f"Summary: {valid_count}/{len(plan_files)} plans valid")
    print(f"{'='*70}\n")

    return valid_count, len(plan_files)


def main():
    parser = argparse.ArgumentParser(
        description="Validate PERT implementation plan files for methodology compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single plan
  python validate-pert-plan.py my-implementation-plan.md

  # Validate with verbose output
  python validate-pert-plan.py my-plan.md --verbose

  # Validate all plans in directory
  python validate-pert-plan.py --dir ~/.claude/plans/

  # Validate directory with verbose output
  python validate-pert-plan.py --dir ~/.claude/plans/ --verbose

Validation Checks:
  - Impact level present and valid (1-5)
  - Correct number of risk factors (3 for Impact 1-2, 5 for Impact 3-5)
  - Confidence scores meet impact-based thresholds
  - Research iterations ≤ 1 (recommended)
  - Risk acceptance documented for <threshold phases (Impact 3-5)
  - Phase structure and formatting
  - Summary table present at plan end (warning)
        """
    )

    parser.add_argument(
        'plan',
        nargs='?',
        type=str,
        help='Path to plan file to validate'
    )

    parser.add_argument(
        '--dir',
        type=str,
        help='Validate all .md files in directory'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation output'
    )

    args = parser.parse_args()

    # Directory mode
    if args.dir:
        directory = Path(args.dir).expanduser()
        valid_count, total_count = validate_directory(directory, args.verbose)
        sys.exit(0 if valid_count == total_count else 1)

    # Single file mode
    if args.plan:
        plan_path = Path(args.plan).expanduser()
        is_valid = validate_plan(plan_path, args.verbose)
        sys.exit(0 if is_valid else 1)

    # No arguments
    parser.error("Either provide a plan file or use --dir to validate a directory")


if __name__ == '__main__':
    main()
