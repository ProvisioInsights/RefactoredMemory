import { AppBridge, PostMessageTransport } from '@modelcontextprotocol/ext-apps/app-bridge';
const frame = document.querySelector('iframe');
const status = document.querySelector('#status');
const displayOnly = new URLSearchParams(location.search).has('display');
async function call(name, args = {}) {
  const response = await fetch('/rpc', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({name, arguments: args}) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Synthetic tool failed');
  return {content:[{type:'text',text:JSON.stringify(result)}],structuredContent:result};
}
const bridge = new AppBridge(null, {name:'RM synthetic reference host',version:'1.0.0'}, displayOnly ? {} : {serverTools:{}});
bridge.oncalltool = params => call(params.name, params.arguments);
bridge.oninitialized = async () => {
  status.textContent = displayOnly ? 'SDK connected · display only' : 'SDK connected · tool bridge available';
  await bridge.sendToolResult(await call('memory_graph',{start:'project',depth:2}));
};
await bridge.connect(new PostMessageTransport(frame.contentWindow, frame.contentWindow));
frame.src = '/app';
