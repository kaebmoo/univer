import type { CheckResult } from '@/lib/types';

// Tolerance levels matching Python scripts
export const TOLERANCE_PRECISE = 0.001;   // floating-point rounding (most checks)
export const TOLERANCE_STANDARD = 1.0;    // net profit (small rounding across aggregation)
export const TOLERANCE_REVENUE = 10.0;    // revenue aggregated across multiple sheets

/**
 * Create a CheckResult with computed diff and pass/fail status.
 * Factory function used by all reconcilers.
 */
export function createResult(
  category: string,
  check_name: string,
  source_label: string,
  source_value: number,
  target_label: string,
  target_value: number,
  tolerance: number = TOLERANCE_PRECISE,
): CheckResult {
  const diff = source_value - target_value;
  const passed = Math.abs(diff) <= tolerance;
  return {
    category,
    check_name,
    source_label,
    source_value,
    target_label,
    target_value,
    diff,
    passed,
    status: passed ? 'PASS' : 'FAIL',
    tolerance,
  };
}
