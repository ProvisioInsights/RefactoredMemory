import { AppBridge, PostMessageTransport } from '@modelcontextprotocol/ext-apps/app-bridge';
const frame = document.querySelector('iframe');
const status = document.querySelector('#status');
const displayOnly = new URLSearchParams(location.search).has('display');
const readOnly = new URLSearchParams(location.search).has('readonly');
let initialResult;
async function call(name, args = {}) {
  const response = await fetch('/rpc', { method: 'POST', headers: {'Content-Type':'application/json', ...(readOnly ? {'X-RM-Synthetic-Read-Only':'1'} : {})}, body: JSON.stringify({name, arguments: args}) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Synthetic tool failed');
  return {content:[{type:'text',text:JSON.stringify(result)}],structuredContent:result};
}
const bridge = new AppBridge(null, {name:'RM synthetic reference host',version:'1.0.0'}, displayOnly ? {} : {serverTools:{}}, {hostContext:{theme:'light'}});
document.querySelector('#theme').addEventListener('change', event => bridge.setHostContext({theme:event.target.value}));
document.querySelector('#replay').addEventListener('click', () => initialResult && bridge.sendToolResult(initialResult));
bridge.oncalltool = params => call(params.name, params.arguments);
bridge.oninitialized = async () => {
  status.textContent = displayOnly ? 'SDK connected · display only' : 'SDK connected · tool bridge available';
  const artifacts = (await call('memory_artifacts', {subject:'project'})).structuredContent;
  const brief = artifacts.find(a => a.value.view?.schema === 'refactoredmemory.relationship-brief:v1');
  const result = await call('memory_graph',{start:'project',...(brief ? {brief_id:brief.id} : {depth:1})});
  result.structuredContent.example_data = true;
  initialResult = result;
  await bridge.sendToolResult(result);
};
await bridge.connect(new PostMessageTransport(frame.contentWindow, frame.contentWindow));
frame.src = '/app';
