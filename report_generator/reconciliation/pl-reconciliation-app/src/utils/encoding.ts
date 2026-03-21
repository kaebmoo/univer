/**
 * File encoding utilities
 * Handles TIS-620 / cp874 / Windows-874 Thai encoding
 */

/**
 * Read a File as text with auto-detection of encoding.
 * Try UTF-8 first; if garbled (U+FFFD), fallback to windows-874.
 */
export async function readFileWithEncoding(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  return decodeBuffer(buffer);
}

/**
 * Decode an ArrayBuffer to string with encoding auto-detection.
 * Fallback chain: UTF-8 → windows-874
 */
export function decodeBuffer(buffer: ArrayBuffer): string {
  // Try UTF-8 first
  const utf8 = new TextDecoder('utf-8', { fatal: false }).decode(buffer);

  // Check for replacement characters (garbled Thai text)
  if (!utf8.includes('\uFFFD')) {
    return utf8;
  }

  // Fallback to Windows-874 (covers cp874 / TIS-620)
  return new TextDecoder('windows-874').decode(buffer);
}

/**
 * Read a File as ArrayBuffer
 */
export function readFileAsArrayBuffer(file: File): Promise<ArrayBuffer> {
  return file.arrayBuffer();
}
