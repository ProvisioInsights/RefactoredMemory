import fs from 'node:fs';
import { checkedContext, topology, pathTo, sameFrontier, travelTrace } from '../../apps/memory_graph/src/neighborhoodModel.js';
const graph = JSON.parse(fs.readFileSync(0, 'utf8'));
const model = topology(graph, 2), direct = topology(graph, 1);
const path = pathTo(model, 'riverbend');
const fresh = {...graph,brief:{id:'brief',freshness:{state:'current'}}};
const rejects = (brief, context) => { try { checkedContext(brief,context,graph.start,'brief'); return false; } catch { return true; } };
console.log(JSON.stringify({
  direct: direct.nodes.map(n => n.id),
  hops: Object.fromEntries(model.nodes.map(n => [n.id, n.hop])),
  path,
  tracedEdges: [...travelTrace(graph, [{id:'riverbend'},{id:'avery'}]).edges].sort(),
  previousFocus: travelTrace(graph, [{id:'riverbend'},{id:'avery'}]).previous,
  noInventedTrailEdge: [...travelTrace(graph, [{id:'robin'},{id:'jordan'}]).edges].every(id => id === 'jordan-round'),
  emptyTrace: travelTrace(graph, []).edges.size === 0,
  retainedDirection: model.edges.find(e => e.id === 'avery-round'),
  onlyRecordedEdges: model.edges.every(e => graph.edges.some(original => original.id === e.id)),
  equalFrontier: sameFrontier({a:1,b:2}, {b:2,a:1}),
  changedFrontier: !sameFrontier({a:1}, {a:2}),
  currentContext: checkedContext(fresh, graph, graph.start, 'brief').data === graph,
  staleWithheld: !!checkedContext({...fresh,brief:{id:'brief',freshness:{state:'stale'}}},graph,graph.start,'brief').stale,
  changedContextRejected: rejects({...fresh,frontier:{different:1}},graph),
  wrongBriefRejected: rejects({...fresh,start:'other'},graph),
  wrongRevisionRejected: rejects({...fresh,brief:{...fresh.brief,id:'other'}},graph),
  wrongContextRejected: rejects(fresh,{...graph,start:'other'}),
  overBudgetRejected: rejects(fresh,{...graph,entities:Array(17).fill(graph.entities[0])}),
  bounded: topology({...graph,entities:[...graph.entities,{id:'disconnected',label:'Not connected'}]}, 2).nodes.every(n => n.id !== 'disconnected')
}));
