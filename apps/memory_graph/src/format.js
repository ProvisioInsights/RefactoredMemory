export const displayName = entity => entity?.display_label || entity?.label || 'Unavailable identity';
export const human = text => String(text || '').replace(/^rm:/, '').replaceAll('-', ' ');
export function compact(value) {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return 'Not established';
  return JSON.stringify(value, null, 2);
}
