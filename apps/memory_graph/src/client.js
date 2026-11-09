import { App } from '@modelcontextprotocol/ext-apps';

export function unwrap(result) {
  if (result.isError) throw new Error(result.structuredContent?.error === 'conflict'
    ? 'This record changed. Reload it before saving again.'
    : result.content?.find(x => x.type === 'text')?.text || 'This action is unavailable.');
  return result.structuredContent ?? JSON.parse(result.content.find(x => x.type === 'text').text);
}

export async function connect(onGraph) {
  if (document.documentElement.dataset.rmMode === 'local') {
    const request = async (path, body) => {
      const response = await fetch(path, { method: body ? 'POST' : 'GET', credentials: 'same-origin',
        headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not complete the request.');
      return result;
    };
    if (location.hash.startsWith('#key=')) {
      const key = decodeURIComponent(location.hash.slice(5));
      history.replaceState(null, '', location.pathname);
      await request('/api/session', { key });
    }
    const state = await request('/api/state');
    return { ...state, local: true, available: true,
      unlock: key => request('/api/session', { key }),
      call: (name, args = {}) => request('/api/tool', { name, arguments: args }) };
  }
  const app = new App({ name: 'RefactoredMemory graph', version: '1.0.0' });
  app.ontoolresult = result => { if (result.structuredContent?.entities) onGraph(result.structuredContent); };
  await app.connect();
  const available = !!app.getHostCapabilities()?.serverTools;
  return { authenticated: true, local: false, available,
    call: async (name, args = {}) => {
      if (!available) throw new Error('This host can display the graph. Additional reads and changes are unavailable here.');
      return unwrap(await app.callServerTool({ name, arguments: args }));
    } };
}

export function requestId() { return crypto.randomUUID(); }
export const human = text => String(text || '').replace(/^rm:/, '').replaceAll('-', ' ');
export function compact(value) {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return 'Not established';
  return JSON.stringify(value, null, 2);
}
