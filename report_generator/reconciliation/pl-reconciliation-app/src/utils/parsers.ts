/**
 * Number parsing utilities
 * Port of Python's parse_thai_number() and parse_number()
 */

/**
 * Parse Thai-formatted number strings to float.
 * Handles: parentheses as negative, commas, dashes, empty values.
 *
 * Examples:
 *   '(1,234.56)' → -1234.56
 *   '1,000'      → 1000
 *   '-'          → 0
 *   ''           → 0
 *   null         → 0
 */
export function parseThaiNumber(text: unknown): number {
  if (text === null || text === undefined) return 0;

  let s = String(text).trim();
  if (s === '' || s === '-') return 0;

  // Parentheses mean negative: (1,234.56) → -1234.56
  if (s.startsWith('(') && s.endsWith(')')) {
    s = '-' + s.slice(1, -1);
  }

  // Remove commas
  s = s.replace(/,/g, '');

  const val = parseFloat(s);
  return isNaN(val) ? 0 : val;
}

/**
 * Simple float conversion with NaN → 0 fallback.
 * Equivalent to pandas' safe float conversion.
 */
export function parseNumber(value: unknown): number {
  if (value === null || value === undefined) return 0;
  const val = typeof value === 'number' ? value : parseFloat(String(value));
  return isNaN(val) ? 0 : val;
}

/**
 * Safely parse a CSV VALUE field to number.
 * CSV values are always strings; this handles empty/null/NaN like pandas .sum().
 */
export function parseCsvValue(value: unknown): number {
  if (value === null || value === undefined || value === '') return 0;
  const val = parseFloat(String(value));
  return isNaN(val) ? 0 : val;
}
