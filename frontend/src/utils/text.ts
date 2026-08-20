/** Truncate text to maxLen chars, appending ellipsis if truncated. */
export function truncate(text: string, maxLen: number = 50): string {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '…' : text
}
