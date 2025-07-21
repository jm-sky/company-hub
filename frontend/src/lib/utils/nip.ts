/**
 * Utility functions for handling Polish NIP (Tax Identification Number)
 */

/**
 * Normalize NIP by removing spaces and dashes
 */
export function normalizeNip(nip: string): string {
  return nip.replace(/[\s-]/g, '')
}

/**
 * Format NIP as XXX-XXX-XX-XX for display
 */
export function formatNip(nip: string): string {
  const normalized = normalizeNip(nip)
  if (normalized.length === 10) {
    return `${normalized.slice(0, 3)}-${normalized.slice(3, 6)}-${normalized.slice(6, 8)}-${normalized.slice(8, 10)}`
  }
  return nip
}

/**
 * Validate NIP format (basic check for 10 digits)
 */
export function isValidNipFormat(nip: string): boolean {
  const normalized = normalizeNip(nip)
  return /^\d{10}$/.test(normalized)
}

/**
 * Validate NIP checksum (full validation)
 */
export function isValidNip(nip: string): boolean {
  const normalized = normalizeNip(nip)
  
  if (!isValidNipFormat(normalized)) {
    return false
  }

  // NIP checksum algorithm
  const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
  const digits = normalized.split('').map(Number)
  
  let sum = 0
  for (let i = 0; i < 9; i++) {
    sum += digits[i] * weights[i]
  }
  
  const checksum = sum % 11
  const lastDigit = digits[9]
  
  return checksum === lastDigit
}