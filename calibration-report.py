#!/usr/bin/env python3
"""
PERT Calibration Report Generator
Analyzes actual outcomes vs predicted confidence scores to calibrate PERT multiplier.

Usage:
    # Full report
    python calibration-report.py

    # Export to CSV
    python calibration-report.py --export outcomes.csv

    # Get multiplier recommendation
    python calibration-report.py --adjust-multiplier

    # Custom multiplier (default: 2.0)
    python calibration-report.py --current-multiplier 2.15
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
CALIBRATION_DIR = Path.home() / ".claude" / "plans" / ".calibration"
OUTCOMES_FILE = CALIBRATION_DIR / "outcomes.jsonl"
REPORTS_DIR = CALIBRATION_DIR / "reports"
MULTIPLIER_HISTORY = CALIBRATION_DIR / "multiplier-history.txt"

# Calibration parameters
DEFAULT_MULTIPLIER = 2.0
MIN_MULTIPLIER = 1.5
MAX_MULTIPLIER = 3.0
MIN_SAMPLE_SIZE = 5  # Minimum outcomes needed for reliable calibration


def load_outcomes() -> List[Dict]:
    """Load all outcomes from JSONL database."""
    if not OUTCOMES_FILE.exists():
        print(f"⚠️  No outcomes database found at {OUTCOMES_FILE}")
        print("   Track outcomes using: python plan-outcome-tracker.py")
        return []

    outcomes = []
    with OUTCOMES_FILE.open('r') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    outcomes.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Skipping malformed line {line_num}: {e}")

    return outcomes


def group_by_confidence_bucket(outcomes: List[Dict], bucket_size: int = 2) -> Dict[str, List[Dict]]:
    """
    Group outcomes by confidence score buckets.

    Args:
        outcomes: List of outcome records
        bucket_size: Width of each bucket in percentage points (default: 2)

    Returns:
        Dict mapping bucket labels to list of outcomes
    """
    buckets = {}

    for outcome in outcomes:
        confidence = outcome.get('predicted_confidence')
        if confidence is None:
            continue

        # Calculate bucket range (e.g., 94-96%)
        bucket_start = int(confidence // bucket_size) * bucket_size
        bucket_end = bucket_start + bucket_size
        bucket_label = f"{bucket_start}-{bucket_end}%"

        if bucket_label not in buckets:
            buckets[bucket_label] = []

        buckets[bucket_label].append(outcome)

    return buckets


def calculate_success_rate(outcomes: List[Dict]) -> float:
    """Calculate actual success rate from outcomes."""
    if not outcomes:
        return 0.0

    success_count = sum(1 for o in outcomes if o.get('actual_outcome') == 'SUCCESS')
    return (success_count / len(outcomes)) * 100


def calculate_calibration_stats(outcomes: List[Dict]) -> Dict:
    """
    Calculate comprehensive calibration statistics.

    Returns:
        Dict with overall statistics and per-bucket analysis
    """
    if not outcomes:
        return {
            'total_plans': 0,
            'mean_predicted': 0.0,
            'mean_actual': 0.0,
            'mean_error': 0.0,
            'buckets': {},
            'is_overconfident': False,
            'is_underconfident': False
        }

    # Overall statistics
    total_plans = len(outcomes)
    predicted_scores = [o['predicted_confidence'] for o in outcomes if o.get('predicted_confidence')]
    mean_predicted = sum(predicted_scores) / len(predicted_scores) if predicted_scores else 0.0

    # Calculate actual success rate
    success_count = sum(1 for o in outcomes if o.get('actual_outcome') == 'SUCCESS')
    mean_actual = (success_count / total_plans) * 100

    # Calibration error (positive = overconfident, negative = underconfident)
    mean_error = mean_predicted - mean_actual

    # Per-bucket analysis
    buckets = group_by_confidence_bucket(outcomes)
    bucket_stats = {}

    for bucket_label, bucket_outcomes in sorted(buckets.items()):
        predicted_avg = sum(o['predicted_confidence'] for o in bucket_outcomes) / len(bucket_outcomes)
        actual_rate = calculate_success_rate(bucket_outcomes)
        calibration_error = predicted_avg - actual_rate

        bucket_stats[bucket_label] = {
            'count': len(bucket_outcomes),
            'predicted_avg': predicted_avg,
            'actual_rate': actual_rate,
            'calibration_error': calibration_error
        }

    return {
        'total_plans': total_plans,
        'mean_predicted': mean_predicted,
        'mean_actual': mean_actual,
        'mean_error': mean_error,
        'buckets': bucket_stats,
        'is_overconfident': mean_error > 2.0,  # >2% overconfidence
        'is_underconfident': mean_error < -2.0  # >2% underconfidence
    }


def calculate_multiplier_adjustment(
    stats: Dict,
    current_multiplier: float = DEFAULT_MULTIPLIER
) -> Tuple[float, str]:
    """
    Calculate recommended multiplier adjustment based on calibration error.

    Algorithm:
    - If overconfident (actual < predicted): Increase multiplier (widen CI)
    - If underconfident (actual > predicted): Decrease multiplier (narrow CI)
    - Adjustment scaled by weighted calibration error
    - Bounded to [MIN_MULTIPLIER, MAX_MULTIPLIER]

    Returns:
        (new_multiplier, justification)
    """
    mean_error = stats['mean_error']
    total_plans = stats['total_plans']

    # No adjustment if sample size too small
    if total_plans < MIN_SAMPLE_SIZE:
        return current_multiplier, f"Insufficient data ({total_plans} plans, need ≥{MIN_SAMPLE_SIZE})"

    # No adjustment if error is small (<2%)
    if abs(mean_error) < 2.0:
        return current_multiplier, f"System well-calibrated (error: {mean_error:+.1f}%)"

    # Calculate weighted adjustment
    # Overconfident → increase multiplier (widen confidence interval)
    # Underconfident → decrease multiplier (narrow confidence interval)
    adjustment_factor = -mean_error / 2.5 * 0.05
    new_multiplier = current_multiplier + adjustment_factor

    # Bound to valid range
    new_multiplier = max(MIN_MULTIPLIER, min(MAX_MULTIPLIER, new_multiplier))

    # Generate justification
    direction = "overconfident" if mean_error > 0 else "underconfident"
    action = "widening" if new_multiplier > current_multiplier else "narrowing"

    justification = (
        f"System is {direction} by {abs(mean_error):.1f}%. "
        f"Recommendation: {action} confidence interval "
        f"({current_multiplier:.2f} → {new_multiplier:.2f})"
    )

    return new_multiplier, justification


def generate_markdown_report(stats: Dict, current_multiplier: float) -> str:
    """Generate human-readable markdown calibration report."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    new_multiplier, adjustment_reason = calculate_multiplier_adjustment(stats, current_multiplier)

    report = f"""# PERT Calibration Report
**Generated**: {timestamp}
**Sample Size**: {stats['total_plans']} completed plans

---

## Overall Statistics

| Metric | Value |
|--------|-------|
| Mean Predicted Confidence | {stats['mean_predicted']:.1f}% |
| Mean Actual Success Rate | {stats['mean_actual']:.1f}% |
| Mean Calibration Error | {stats['mean_error']:+.1f}% |
| System Status | {'⚠️ OVERCONFIDENT' if stats['is_overconfident'] else '⚠️ UNDERCONFIDENT' if stats['is_underconfident'] else '✅ WELL-CALIBRATED'} |

**Calibration Error Interpretation**:
- Positive error = System overconfident (predicting higher success than reality)
- Negative error = System underconfident (predicting lower success than reality)
- Well-calibrated = Error within ±2%

---

## Confidence Bucket Analysis

| Predicted Range | Count | Avg Predicted | Actual Success | Calibration Error |
|----------------|-------|---------------|----------------|-------------------|
"""

    # Add bucket rows
    for bucket_label, bucket_data in sorted(stats['buckets'].items()):
        report += (
            f"| {bucket_label:14} | {bucket_data['count']:5} | "
            f"{bucket_data['predicted_avg']:13.1f}% | "
            f"{bucket_data['actual_rate']:14.1f}% | "
            f"{bucket_data['calibration_error']:17.1f}% |\n"
        )

    report += f"""
---

## Multiplier Adjustment Recommendation

**Current Multiplier**: {current_multiplier:.2f}
**Recommended Multiplier**: {new_multiplier:.2f} ({new_multiplier - current_multiplier:+.2f} adjustment)

**Reason**: {adjustment_reason}

"""

    if new_multiplier != current_multiplier:
        report += f"""**Action Required**:

1. Update `pert-calculator.py` line ~51:
   ```python
   CONFIDENCE_MULTIPLIER = {new_multiplier:.2f}  # Updated from {current_multiplier:.2f}
   ```

2. Log this adjustment:
   ```bash
   echo "{datetime.now(timezone.utc).isoformat()}: {current_multiplier:.2f} → {new_multiplier:.2f} (calibration error: {stats['mean_error']:+.1f}%)" >> multiplier-history.txt
   ```

3. Continue tracking outcomes for next calibration cycle

"""
    else:
        report += """**No action required**: System is well-calibrated or needs more data.

"""

    report += f"""---

## Recommendations

"""

    if stats['total_plans'] < MIN_SAMPLE_SIZE:
        report += f"- ⚠️ **Insufficient data**: Need at least {MIN_SAMPLE_SIZE} outcomes for reliable calibration\n"
        report += f"- Current sample size: {stats['total_plans']}\n"
        report += f"- Track {MIN_SAMPLE_SIZE - stats['total_plans']} more plans before adjusting multiplier\n"
    elif stats['total_plans'] < 20:
        report += f"- ✅ **Minimal viable sample**: {stats['total_plans']} outcomes\n"
        report += f"- Recommend tracking 20+ plans for robust calibration\n"
    else:
        report += f"- ✅ **Good sample size**: {stats['total_plans']} outcomes\n"

    if stats['is_overconfident']:
        report += "- ⚠️ **System overconfident**: Plans failing more than predicted\n"
        report += "- Recommendation: Increase multiplier to widen confidence intervals\n"
        report += "- Alternative: Review O/M/P estimation process for optimism bias\n"
    elif stats['is_underconfident']:
        report += "- ⚠️ **System underconfident**: Plans succeeding more than predicted\n"
        report += "- Recommendation: Decrease multiplier to narrow confidence intervals\n"
        report += "- Alternative: Review if pessimistic estimates are too conservative\n"
    else:
        report += "- ✅ **System well-calibrated**: Predictions align with outcomes\n"

    report += """
---

## Data Quality Notes

- **SUCCESS**: Plan completed as expected, all phases implemented
- **PARTIAL**: Some phases completed, others failed/deferred
- **FAILURE**: Plan abandoned or completely failed

For calibration purposes:
- SUCCESS = 100% success
- PARTIAL = Not counted as full success (conservative approach)
- FAILURE = 0% success

---

## Next Steps

1. **Continue tracking**: Record outcomes for all new plans
2. **Quarterly review**: Re-run calibration report every 3 months
3. **Adjust multiplier**: Apply recommendations from this report
4. **Monitor trends**: Watch for systematic biases in specific risk factors

"""

    return report


def export_to_csv(outcomes: List[Dict], output_path: Path) -> None:
    """Export outcomes to CSV for external analysis."""
    if not outcomes:
        print("⚠️  No outcomes to export")
        return

    fieldnames = [
        'plan_file', 'plan_name', 'tracked_date',
        'predicted_confidence', 'actual_outcome',
        'implementation_duration_hours', 'notes', 'failure_phase'
    ]

    with output_path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(outcomes)

    print(f"✅ Exported {len(outcomes)} outcomes to {output_path}")


def save_report(report: str) -> Path:
    """Save markdown report to file."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_file = REPORTS_DIR / f"{timestamp}-calibration-report.md"
    latest_link = REPORTS_DIR / "latest-report.md"

    report_file.write_text(report)

    # Update symlink to latest report
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(report_file.name)

    return report_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate PERT calibration report and multiplier recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full report (display + save)
  python calibration-report.py

  # Export outcomes to CSV
  python calibration-report.py --export outcomes.csv

  # Get multiplier recommendation only
  python calibration-report.py --adjust-multiplier

  # Use custom current multiplier
  python calibration-report.py --current-multiplier 2.15
        """
    )

    parser.add_argument(
        '--export',
        type=str,
        metavar='CSV_FILE',
        help='Export outcomes to CSV file'
    )

    parser.add_argument(
        '--adjust-multiplier',
        action='store_true',
        help='Show multiplier recommendation only (no full report)'
    )

    parser.add_argument(
        '--current-multiplier',
        type=float,
        default=DEFAULT_MULTIPLIER,
        help=f'Current confidence multiplier (default: {DEFAULT_MULTIPLIER})'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save report to file (print only)'
    )

    args = parser.parse_args()

    # Load outcomes
    outcomes = load_outcomes()

    if not outcomes:
        print("📭 No outcomes found. Start tracking with:")
        print("   python plan-outcome-tracker.py --plan <plan-file.md> --outcome SUCCESS")
        sys.exit(1)

    print(f"\n📊 Loaded {len(outcomes)} plan outcomes\n")

    # Export mode
    if args.export:
        export_to_csv(outcomes, Path(args.export))
        return

    # Calculate statistics
    stats = calculate_calibration_stats(outcomes)

    # Multiplier recommendation only
    if args.adjust_multiplier:
        new_multiplier, reason = calculate_multiplier_adjustment(stats, args.current_multiplier)
        print(f"Current Multiplier: {args.current_multiplier:.2f}")
        print(f"Recommended Multiplier: {new_multiplier:.2f}")
        print(f"Adjustment: {new_multiplier - args.current_multiplier:+.2f}")
        print(f"\nReason: {reason}")
        return

    # Full report
    report = generate_markdown_report(stats, args.current_multiplier)
    print(report)

    # Save report unless --no-save
    if not args.no_save:
        report_file = save_report(report)
        print(f"\n✅ Report saved to: {report_file}")
        print(f"   Latest link: {REPORTS_DIR / 'latest-report.md'}")


if __name__ == '__main__':
    main()
