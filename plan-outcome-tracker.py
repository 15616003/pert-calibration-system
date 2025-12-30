#!/usr/bin/env python3
"""
PERT Plan Outcome Tracker
Records actual implementation outcomes for calibration analysis.

Usage:
    # Interactive mode
    python plan-outcome-tracker.py

    # Quick mode
    python plan-outcome-tracker.py --plan my-plan.md --outcome SUCCESS --notes "Completed"

    # List tracked plans
    python plan-outcome-tracker.py --list
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


# Configuration
CALIBRATION_DIR = Path.home() / ".claude" / "plans" / ".calibration"
OUTCOMES_FILE = CALIBRATION_DIR / "outcomes.jsonl"


def extract_plan_metadata(plan_path: Path) -> Dict:
    """Extract predicted confidence scores and metadata from plan file."""
    if not plan_path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")

    content = plan_path.read_text()

    # Extract plan name from title
    title_match = re.search(r'^#\s+(?:Implementation Plan:\s*)?(.+?)$', content, re.MULTILINE)
    plan_name = title_match.group(1).strip() if title_match else plan_path.stem

    # Extract all confidence scores
    confidence_pattern = r'95%\s+Confident\s+Success:\s*([-]?\d+\.?\d*)%'
    confidence_scores = re.findall(confidence_pattern, content, re.IGNORECASE)

    if not confidence_scores:
        print(f"⚠️  Warning: No confidence scores found in {plan_path.name}")
        return {
            'plan_name': plan_name,
            'phases': [],
            'overall_confidence': None
        }

    # Extract phase names and their confidence scores
    phases = []
    phase_pattern = r'##\s+Phase\s+(\d+):\s*(.+?)$'
    phase_matches = re.finditer(phase_pattern, content, re.MULTILINE)

    phase_confidences = [float(score) for score in confidence_scores]

    for idx, phase_match in enumerate(phase_matches):
        if idx < len(phase_confidences):
            phases.append({
                'name': f"Phase {phase_match.group(1)}: {phase_match.group(2).strip()}",
                'predicted_confidence': phase_confidences[idx]
            })

    # If no phases found but we have confidence scores, create generic phases
    if not phases and phase_confidences:
        for idx, confidence in enumerate(phase_confidences):
            phases.append({
                'name': f"Phase {idx}",
                'predicted_confidence': confidence
            })

    # Overall confidence is typically the minimum of all phases
    overall_confidence = min(phase_confidences) if phase_confidences else None

    return {
        'plan_name': plan_name,
        'phases': phases,
        'overall_confidence': overall_confidence
    }


def record_outcome(
    plan_path: Path,
    outcome: str,
    duration_hours: Optional[float] = None,
    notes: str = "",
    failure_phase: Optional[str] = None
) -> None:
    """Record plan outcome to JSONL database."""

    # Extract metadata from plan file
    metadata = extract_plan_metadata(plan_path)

    # Build outcome record
    record = {
        'plan_file': plan_path.name,
        'plan_name': metadata['plan_name'],
        'tracked_date': datetime.now(timezone.utc).isoformat(),
        'predicted_confidence': metadata['overall_confidence'],
        'phases': metadata['phases'],
        'actual_outcome': outcome.upper(),
        'implementation_duration_hours': duration_hours,
        'notes': notes,
        'failure_phase': failure_phase
    }

    # Ensure calibration directory exists
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

    # Append to JSONL file
    with OUTCOMES_FILE.open('a') as f:
        f.write(json.dumps(record) + '\n')

    print(f"✅ Outcome recorded for '{metadata['plan_name']}'")
    print(f"   Predicted: {metadata['overall_confidence']}% | Actual: {outcome}")
    print(f"   Database: {OUTCOMES_FILE}")


def list_tracked_plans() -> None:
    """List all tracked plan outcomes."""
    if not OUTCOMES_FILE.exists():
        print("📭 No outcomes tracked yet.")
        print(f"   Database will be created at: {OUTCOMES_FILE}")
        return

    outcomes = []
    with OUTCOMES_FILE.open('r') as f:
        for line in f:
            if line.strip():
                outcomes.append(json.loads(line))

    if not outcomes:
        print("📭 No outcomes tracked yet.")
        return

    print(f"\n📊 Tracked Plans ({len(outcomes)} total)\n")
    print(f"{'Plan Name':<40} {'Predicted':<12} {'Actual':<12} {'Date':<12}")
    print("=" * 80)

    for outcome in outcomes:
        plan_name = outcome['plan_name'][:38]
        predicted = f"{outcome['predicted_confidence']:.1f}%" if outcome['predicted_confidence'] else "N/A"
        actual = outcome['actual_outcome']
        date = outcome['tracked_date'][:10]

        print(f"{plan_name:<40} {predicted:<12} {actual:<12} {date:<12}")

    print("\n")


def interactive_mode() -> None:
    """Interactive CLI for recording plan outcomes."""
    print("\n" + "="*60)
    print("  PERT Plan Outcome Tracker (Interactive Mode)")
    print("="*60 + "\n")

    # Get plan file
    plans_dir = Path.home() / ".claude" / "plans"
    print(f"Plans directory: {plans_dir}\n")

    plan_file = input("Enter plan filename (e.g., my-plan.md): ").strip()
    plan_path = plans_dir / plan_file if not plan_file.startswith('/') else Path(plan_file)

    if not plan_path.exists():
        print(f"❌ Error: Plan file not found: {plan_path}")
        sys.exit(1)

    # Extract and display metadata
    print("\n📄 Extracting plan metadata...")
    metadata = extract_plan_metadata(plan_path)

    print(f"\nPlan: {metadata['plan_name']}")
    print(f"Phases: {len(metadata['phases'])}")
    if metadata['overall_confidence']:
        print(f"Predicted Confidence: {metadata['overall_confidence']:.1f}%")
    print()

    # Get outcome
    print("Actual Outcome:")
    print("  1. SUCCESS - All phases completed as expected")
    print("  2. PARTIAL - Some phases completed, others failed/deferred")
    print("  3. FAILURE - Plan abandoned or completely failed")

    outcome_choice = input("\nSelect outcome (1-3): ").strip()
    outcome_map = {'1': 'SUCCESS', '2': 'PARTIAL', '3': 'FAILURE'}
    outcome = outcome_map.get(outcome_choice, 'UNKNOWN')

    # Get duration
    duration_input = input("\nImplementation duration in hours (optional, press Enter to skip): ").strip()
    duration_hours = float(duration_input) if duration_input else None

    # Get failure phase (if applicable)
    failure_phase = None
    if outcome in ['PARTIAL', 'FAILURE']:
        failure_input = input("Which phase failed? (e.g., 'Phase 2', press Enter to skip): ").strip()
        failure_phase = failure_input if failure_input else None

    # Get notes
    notes = input("\nAdditional notes (optional): ").strip()

    # Confirm and record
    print("\n" + "-"*60)
    print("Summary:")
    print(f"  Plan: {metadata['plan_name']}")
    print(f"  Predicted: {metadata['overall_confidence']}%")
    print(f"  Actual: {outcome}")
    if duration_hours:
        print(f"  Duration: {duration_hours} hours")
    if failure_phase:
        print(f"  Failed at: {failure_phase}")
    if notes:
        print(f"  Notes: {notes}")
    print("-"*60)

    confirm = input("\nRecord this outcome? (y/n): ").strip().lower()
    if confirm == 'y':
        record_outcome(plan_path, outcome, duration_hours, notes, failure_phase)
        print("\n✅ Outcome successfully recorded!")
    else:
        print("\n❌ Recording cancelled.")


def main():
    parser = argparse.ArgumentParser(
        description="Track PERT plan implementation outcomes for calibration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python plan-outcome-tracker.py

  # Quick mode
  python plan-outcome-tracker.py --plan my-plan.md --outcome SUCCESS

  # With details
  python plan-outcome-tracker.py --plan my-plan.md --outcome PARTIAL \\
      --duration 6.5 --notes "Phase 3 deferred"

  # List all tracked plans
  python plan-outcome-tracker.py --list
        """
    )

    parser.add_argument(
        '--plan',
        type=str,
        help='Plan file path (relative to ~/.claude/plans/ or absolute)'
    )

    parser.add_argument(
        '--outcome',
        type=str,
        choices=['SUCCESS', 'PARTIAL', 'FAILURE'],
        help='Actual implementation outcome'
    )

    parser.add_argument(
        '--duration',
        type=float,
        help='Implementation duration in hours'
    )

    parser.add_argument(
        '--notes',
        type=str,
        default='',
        help='Additional notes about the implementation'
    )

    parser.add_argument(
        '--failure-phase',
        type=str,
        help='Phase where failure occurred (for PARTIAL/FAILURE outcomes)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all tracked plan outcomes'
    )

    args = parser.parse_args()

    # List mode
    if args.list:
        list_tracked_plans()
        return

    # Quick mode
    if args.plan and args.outcome:
        plans_dir = Path.home() / ".claude" / "plans"
        plan_path = plans_dir / args.plan if not args.plan.startswith('/') else Path(args.plan)

        record_outcome(
            plan_path,
            args.outcome,
            args.duration,
            args.notes,
            args.failure_phase
        )
        return

    # Interactive mode
    if not args.plan and not args.outcome:
        interactive_mode()
        return

    # Invalid usage
    parser.error("Either use --list, provide both --plan and --outcome, or run without arguments for interactive mode")


if __name__ == '__main__':
    main()
