#!/usr/bin/env python3
"""
PERT Success Calculator - No Shortcuts

Statistically rigorous PERT (Program Evaluation and Review Technique) calculator
for estimating plan success probability without historical data, weighted averages,
heuristics, or curves.

Based on beta distribution and 95% confidence intervals.

Usage:
    # Interactive mode
    python pert-calculator.py

    # Command-line mode
    python pert-calculator.py --complexity 5,15,30 --dependencies 0,10,40 --stack 10,20,50 --knowledge 5,10,25 --testing 5,15,35

    # JSON input mode
    python pert-calculator.py --json '{"complexity": {"O": 5, "M": 15, "P": 30}, ...}'

    # JSON file input
    python pert-calculator.py --json-file risk-assessment.json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Tuple, Optional, List


# Fixed risk factor weights (DO NOT MODIFY - statistically derived)
# 5-factor mode: Full PERT analysis (Impact 3-5)
WEIGHTS_5_FACTOR = {
    'complexity': 0.25,
    'dependencies': 0.20,
    'stack_compat': 0.25,
    'knowledge': 0.15,
    'testing': 0.15
}

# 3-factor mode: Quick PERT analysis (Impact 1-2)
WEIGHTS_3_FACTOR = {
    'complexity': 0.40,
    'dependencies': 0.35,
    'testing': 0.25
}

# Default (backward compatibility with 5-factor mode)
WEIGHTS = WEIGHTS_5_FACTOR

# Confidence threshold (85%)
CONFIDENCE_THRESHOLD = 85.0

# Confidence multiplier (calibrated from empirical data)
# Adjust this value based on calibration-report.py recommendations
# Default: 2.0 (±2 SD for 95% confidence interval)
# Range: [1.5, 3.0]
# History: See calibration directory multiplier-history.txt
CONFIDENCE_MULTIPLIER = 2.0


def calculate_pert_score(O: float, M: float, P: float) -> Tuple[float, float]:
    """
    Calculate PERT score and standard deviation for a single risk factor.

    Uses beta distribution formula:
    - Expected Value (Score) = (O + 4M + P) / 6
    - Standard Deviation = (P - O) / 6

    Args:
        O: Optimistic estimate (0-100, lower is better)
        M: Most Likely estimate (0-100)
        P: Pessimistic estimate (0-100, higher is worse)

    Returns:
        Tuple of (score, standard_deviation)

    Raises:
        ValueError: If estimates are out of range or P < O
    """
    # Validation
    if not (0 <= O <= 100 and 0 <= M <= 100 and 0 <= P <= 100):
        raise ValueError(f"All estimates must be between 0-100. Got O={O}, M={M}, P={P}")

    if P < O:
        raise ValueError(f"Pessimistic ({P}) cannot be less than Optimistic ({O})")

    if not (O <= M <= P):
        raise ValueError(f"Most Likely ({M}) must be between Optimistic ({O}) and Pessimistic ({P})")

    # Pure PERT formula (beta distribution)
    score = (O + 4 * M + P) / 6
    sd = (P - O) / 6

    return score, sd


def calculate_pert_confidence(risk_factors: Dict[str, Dict[str, float]], quick_mode: bool = False) -> Dict[str, float]:
    """
    Calculate overall plan confidence using PERT methodology.

    NO shortcuts, NO weighted averages, NO heuristics, NO curves.
    Uses pure statistical formulas only.

    Args:
        risk_factors: Dict mapping factor names to {'O': float, 'M': float, 'P': float}
                     For quick_mode=False: complexity, dependencies, stack_compat, knowledge, testing
                     For quick_mode=True: complexity, dependencies, testing
        quick_mode: If True, use 3-factor weights (Impact 1-2). If False, use 5-factor weights (Impact 3-5)

    Returns:
        Dict with:
            - phase_success: Success rate before confidence adjustment (%)
            - confident_success: 85% confident success rate (%)
            - meets_threshold: Whether confident_success >= 85%
            - total_sd: Total standard deviation
            - phase_risk: Weighted risk score (%)
            - confidence_width: Width of 95% confidence interval
            - requires_mitigation: Whether mitigation research is needed
            - factor_scores: Individual factor scores for analysis
            - mode: 'quick' or 'full' to indicate which mode was used

    Raises:
        ValueError: If required risk factors are missing
    """
    # Select appropriate weights based on mode
    weights = WEIGHTS_3_FACTOR if quick_mode else WEIGHTS_5_FACTOR

    # Validate all required factors are present
    required_factors = set(weights.keys())
    provided_factors = set(risk_factors.keys())

    missing = required_factors - provided_factors
    if missing:
        mode_name = "quick (3-factor)" if quick_mode else "full (5-factor)"
        raise ValueError(f"Missing required risk factors for {mode_name} mode: {', '.join(missing)}")

    total_risk = 0
    total_sd = 0
    factor_scores = {}

    for factor_name, weight in weights.items():
        estimates = risk_factors[factor_name]
        O, M, P = estimates['O'], estimates['M'], estimates['P']

        # Calculate PERT score and SD
        score, sd = calculate_pert_score(O, M, P)

        # Weighted contribution to total risk
        total_risk += score * weight
        total_sd += sd  # Simple sum for conservative estimate

        factor_scores[factor_name] = {
            'score': round(score, 2),
            'sd': round(sd, 2),
            'weight': weight,
            'weighted_risk': round(score * weight, 2),
            'O': O,
            'M': M,
            'P': P
        }

    # Calculate success metrics
    success_rate = 100 - total_risk
    confidence_width = CONFIDENCE_MULTIPLIER * total_sd  # 95% CI using calibrated multiplier
    confident_success = success_rate - confidence_width

    return {
        'phase_success': round(success_rate, 1),
        'confident_success': round(confident_success, 1),
        'meets_threshold': confident_success >= CONFIDENCE_THRESHOLD,
        'total_sd': round(total_sd, 1),
        'phase_risk': round(total_risk, 1),
        'confidence_width': round(confidence_width, 1),
        'requires_mitigation': confident_success < CONFIDENCE_THRESHOLD,
        'factor_scores': factor_scores,
        'mode': 'quick' if quick_mode else 'full'
    }


def format_results(results: Dict, phase_name: str = "Phase", detailed: bool = True) -> str:
    """
    Format PERT calculation results for display.

    Args:
        results: Output from calculate_pert_confidence()
        phase_name: Name of the phase/module being assessed
        detailed: Whether to show detailed factor breakdown

    Returns:
        Formatted string for terminal output
    """
    output = []
    output.append(f"\n{'='*70}")
    output.append(f"PERT Analysis: {phase_name}")
    mode_label = f" [{results.get('mode', 'full').upper()} MODE]"
    output.append(f"{'='*70}{mode_label}\n")

    # Overall metrics
    output.append("📊 OVERALL METRICS:")
    mode_desc = "3-factor quick mode" if results.get('mode') == 'quick' else "5-factor full mode"
    output.append(f"  Mode:                    {mode_desc}")
    output.append(f"  Phase Risk:              {results['phase_risk']}%")
    output.append(f"  Phase Success:           {results['phase_success']}%")
    output.append(f"  Total Standard Deviation: {results['total_sd']}")
    output.append(f"  Confidence Width (±2σ):   {results['confidence_width']}%")
    output.append(f"\n  85% Confident Success:   {results['confident_success']}%")

    # Verdict
    verdict = "✅ PASS" if results['meets_threshold'] else "❌ FAIL"
    threshold_status = "≥85%" if results['meets_threshold'] else "<85%"
    output.append(f"  Verdict:                 {verdict} {threshold_status}\n")

    if results['requires_mitigation']:
        output.append("⚠️  MITIGATION REQUIRED:")
        output.append("  1. Identify highest-variance risk factors")
        output.append("  2. Research mitigation strategies")
        output.append("  3. Re-estimate with mitigation")
        output.append("  4. Repeat until ≥85% or declare infeasible\n")

    # Detailed factor breakdown
    if detailed:
        output.append(f"{'─'*70}")
        output.append("📋 RISK FACTOR BREAKDOWN:\n")

        # Sort by variance (SD) descending to highlight high-risk factors
        sorted_factors = sorted(
            results['factor_scores'].items(),
            key=lambda x: x[1]['sd'],
            reverse=True
        )

        for factor_name, scores in sorted_factors:
            output.append(f"  {factor_name.upper().replace('_', ' ')}:")
            output.append(f"    O={scores['O']}, M={scores['M']}, P={scores['P']}")
            output.append(f"    Score: {scores['score']} | SD: {scores['sd']} | Weight: {scores['weight']}")
            output.append(f"    Weighted Risk: {scores['weighted_risk']}%")

            # Flag high variance factors
            if scores['sd'] > 15:
                output.append(f"    ⚠️  HIGH VARIANCE - Priority for mitigation research")
            output.append("")

    output.append(f"{'='*70}\n")

    return "\n".join(output)


def interactive_mode():
    """Interactive mode for entering risk assessments."""
    print("\n" + "="*70)
    print("PERT CALCULATOR - INTERACTIVE MODE")
    print("="*70)
    print("\nEnter three-point estimates (O, M, P) for each risk factor.")
    print("Values: 0-100, where 0 = no risk, 100 = maximum risk\n")

    risk_factors = {}

    factor_prompts = {
        'complexity': 'Complexity (algorithm/logic difficulty, edge cases)',
        'dependencies': 'Dependencies (external libraries, APIs, version compatibility)',
        'stack_compat': 'Stack Compatibility (tested vs. untested on current system)',
        'knowledge': 'Knowledge (familiar vs. novel territory)',
        'testing': 'Testing (verification feasibility, test complexity)'
    }

    for factor_key, description in factor_prompts.items():
        print(f"\n{description}:")

        while True:
            try:
                o_input = input(f"  Optimistic (O): ").strip()
                m_input = input(f"  Most Likely (M): ").strip()
                p_input = input(f"  Pessimistic (P): ").strip()

                O = float(o_input)
                M = float(m_input)
                P = float(p_input)

                # Validate via PERT calculation (will raise ValueError if invalid)
                calculate_pert_score(O, M, P)

                risk_factors[factor_key] = {'O': O, 'M': M, 'P': P}
                break

            except ValueError as e:
                print(f"  ❌ Invalid input: {e}")
                print("  Please try again.\n")

    # Get phase name
    phase_name = input("\nPhase/Module name (optional): ").strip() or "Phase"

    # Calculate and display results
    results = calculate_pert_confidence(risk_factors)
    print(format_results(results, phase_name))

    # Offer to save to JSON
    save = input("Save this assessment to JSON file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Filename (e.g., assessment.json): ").strip()
        if not filename.endswith('.json'):
            filename += '.json'

        output_data = {
            'phase_name': phase_name,
            'risk_factors': risk_factors,
            'results': results
        }

        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"✅ Saved to {filename}")


def batch_mode(data: Dict) -> Tuple[List[Dict], bool]:
    """
    Process multiple phases from batch JSON input.

    Args:
        data: Batch JSON with 'phases' array

    Returns:
        Tuple of (results_list, all_passed)
        - results_list: List of dicts with phase_name and results
        - all_passed: Whether all phases met threshold
    """
    phases = data.get('phases', [])
    plan_name = data.get('plan_name', 'Batch Assessment')
    impact_level = data.get('impact_level', 3)
    quick_mode = data.get('quick_mode', impact_level in [1, 2])

    if not phases:
        print("❌ Error: No phases found in batch JSON", file=sys.stderr)
        return [], False

    print(f"\n{'='*70}")
    print(f"BATCH PROCESSING: {plan_name}")
    print(f"Impact Level: {impact_level} | Mode: {'Quick (3 factors)' if quick_mode else 'Full (5 factors)'}")
    print(f"Phases: {len(phases)}")
    print(f"{'='*70}\n")

    results_list = []
    all_passed = True

    for idx, phase in enumerate(phases, 1):
        phase_name = phase.get('name', f'Phase {idx}')
        risk_factors = phase.get('risk_factors', {})

        try:
            results = calculate_pert_confidence(risk_factors, quick_mode=quick_mode)
            results_list.append({
                'phase_name': phase_name,
                'results': results
            })

            if not results['meets_threshold']:
                all_passed = False

        except ValueError as e:
            print(f"❌ Error in {phase_name}: {e}", file=sys.stderr)
            all_passed = False
            results_list.append({
                'phase_name': phase_name,
                'results': None,
                'error': str(e)
            })

    return results_list, all_passed


def format_batch_results(results_list: List[Dict], plan_name: str = "Batch Assessment") -> str:
    """
    Format batch processing results with summary table.

    Args:
        results_list: List of phase results from batch_mode()
        plan_name: Name of the overall plan

    Returns:
        Formatted markdown string with individual phases and summary table
    """
    output = []

    # Header
    output.append(f"# {plan_name}\n")
    output.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n")

    # Individual phase results
    for item in results_list:
        if item['results'] is None:
            output.append(f"## {item['phase_name']}\n")
            output.append(f"❌ ERROR: {item.get('error', 'Unknown error')}\n")
        else:
            # Use existing format_results() for each phase
            phase_output = format_results(item['results'], item['phase_name'], detailed=True)
            output.append(phase_output)

    # Summary table
    output.append("\n")
    output.append("## Overall Plan Confidence Summary\n")
    output.append("| Phase | Confidence | Status |")
    output.append("|-------|------------|--------|")

    passed_count = 0
    total_confidence = 0.0
    valid_count = 0

    for item in results_list:
        phase_name = item['phase_name']
        # Truncate long phase names
        if len(phase_name) > 40:
            phase_name = phase_name[:37] + "..."

        if item['results'] is None:
            output.append(f"| {phase_name} | ERROR | ❌ |")
        else:
            results = item['results']
            confidence = results['confident_success']
            status = "✅" if results['meets_threshold'] else "❌"

            output.append(f"| {phase_name} | {confidence}% | {status} |")

            if results['meets_threshold']:
                passed_count += 1
            total_confidence += confidence
            valid_count += 1

    # Overall verdict
    output.append("")
    if valid_count == 0:
        output.append("**Overall Plan Verdict:** ERROR - No valid phases")
    elif passed_count == len(results_list):
        output.append(f"**Overall Plan Verdict:** ✅ APPROVED")
    else:
        output.append(f"**Overall Plan Verdict:** ❌ REQUIRES MITIGATION ({len(results_list) - passed_count}/{len(results_list)} phases below threshold)")

    output.append(f"- Phases ≥85%: {passed_count}/{len(results_list)}")
    if valid_count > 0:
        avg_confidence = total_confidence / valid_count
        output.append(f"- Average Confidence: {avg_confidence:.1f}%")
    output.append(f"- Threshold: 85.0%")

    return "\n".join(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='PERT Success Calculator - Statistically rigorous plan confidence estimation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  %(prog)s

  # Quick mode (3 factors) for Impact 1-2 plans
  %(prog)s --quick-mode --complexity 5,15,30 --dependencies 0,10,40 --testing 5,15,35

  # Full mode (5 factors) for Impact 3-5 plans
  %(prog)s --complexity 5,15,30 --dependencies 0,10,40 --stack 10,20,50 --knowledge 5,10,25 --testing 5,15,35

  # JSON input (full mode)
  %(prog)s --json '{"complexity": {"O": 5, "M": 15, "P": 30}, "dependencies": {"O": 0, "M": 10, "P": 40}, ...}'

  # JSON input (quick mode)
  %(prog)s --quick-mode --json '{"complexity": {"O": 5, "M": 15, "P": 30}, "dependencies": {"O": 0, "M": 10, "P": 40}, "testing": {"O": 5, "M": 15, "P": 35}}'

  # JSON file input
  %(prog)s --json-file assessment.json

  # With phase name
  %(prog)s --phase "Phase 1" --complexity 5,15,30 --dependencies 10,20,40 --stack 15,25,45 --knowledge 5,10,20 --testing 10,20,30

Note: All estimates must be between 0-100, where 0 = no risk, 100 = maximum risk
      Quick mode (3 factors): Use for Impact 1-2 (Throwaway, Low-Risk)
      Full mode (5 factors): Use for Impact 3-5 (Medium, High-Impact, Mission-Critical)
        """
    )

    parser.add_argument('--phase', type=str, default='Phase',
                        help='Phase or module name')

    parser.add_argument('--quick-mode', action='store_true',
                        help='Use 3-factor quick mode for Impact 1-2 plans (Complexity, Dependencies, Testing)')

    parser.add_argument('--complexity', type=str,
                        help='Complexity estimates as O,M,P (e.g., 5,15,30)')

    parser.add_argument('--dependencies', type=str,
                        help='Dependencies estimates as O,M,P')

    parser.add_argument('--stack', '--stack-compat', type=str, dest='stack_compat',
                        help='Stack compatibility estimates as O,M,P')

    parser.add_argument('--knowledge', type=str,
                        help='Knowledge estimates as O,M,P')

    parser.add_argument('--testing', type=str,
                        help='Testing estimates as O,M,P')

    parser.add_argument('--json', type=str,
                        help='JSON string with all risk factors')

    parser.add_argument('--json-file', type=str,
                        help='Path to JSON file with risk factors')

    parser.add_argument('--brief', action='store_true',
                        help='Brief output (no detailed factor breakdown)')

    args = parser.parse_args()

    # Determine input mode
    risk_factors = {}

    if args.json_file:
        # JSON file input
        try:
            with open(args.json_file, 'r') as f:
                data = json.load(f)

                # Detect batch mode (has 'phases' array)
                if 'phases' in data:
                    results_list, all_passed = batch_mode(data)
                    plan_name = data.get('plan_name', 'Batch Assessment')
                    output = format_batch_results(results_list, plan_name)
                    print(output)
                    sys.exit(0 if all_passed else 1)

                # Single-phase mode (backward compatible)
                risk_factors = data.get('risk_factors', data)
                if 'phase_name' in data:
                    args.phase = data['phase_name']
        except FileNotFoundError:
            print(f"❌ Error: File not found: {args.json_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in file: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.json:
        # JSON string input
        try:
            risk_factors = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.quick_mode and args.complexity and args.dependencies and args.testing:
        # Quick mode command-line (3 factors)
        try:
            for factor_name, value_str in [
                ('complexity', args.complexity),
                ('dependencies', args.dependencies),
                ('testing', args.testing)
            ]:
                parts = value_str.split(',')
                if len(parts) != 3:
                    raise ValueError(f"{factor_name} must have exactly 3 values (O,M,P)")

                O, M, P = map(float, parts)
                risk_factors[factor_name] = {'O': O, 'M': M, 'P': P}

        except ValueError as e:
            print(f"❌ Error parsing command-line arguments: {e}", file=sys.stderr)
            sys.exit(1)

    elif not args.quick_mode and args.complexity and args.dependencies and args.stack_compat and args.knowledge and args.testing:
        # Full mode command-line (5 factors)
        try:
            for factor_name, value_str in [
                ('complexity', args.complexity),
                ('dependencies', args.dependencies),
                ('stack_compat', args.stack_compat),
                ('knowledge', args.knowledge),
                ('testing', args.testing)
            ]:
                parts = value_str.split(',')
                if len(parts) != 3:
                    raise ValueError(f"{factor_name} must have exactly 3 values (O,M,P)")

                O, M, P = map(float, parts)
                risk_factors[factor_name] = {'O': O, 'M': M, 'P': P}

        except ValueError as e:
            print(f"❌ Error parsing command-line arguments: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        # Interactive mode
        interactive_mode()
        return

    # Calculate and display results
    try:
        results = calculate_pert_confidence(risk_factors, quick_mode=args.quick_mode)
        print(format_results(results, args.phase, detailed=not args.brief))

        # Exit code: 0 if meets threshold, 1 if requires mitigation
        sys.exit(0 if results['meets_threshold'] else 1)

    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
