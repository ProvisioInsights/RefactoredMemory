import fs from 'node:fs';
import { briefRows, selectedPath, relationshipLabel, validGraphSnapshot } from '../../apps/memory_graph/src/briefModel.js';

const graph = JSON.parse(fs.readFileSync(0, 'utf8'));
const rows = briefRows(graph).flatMap(g => g.items);
const path = selectedPath(graph, rows[0]);
const stale = {...graph, brief:{id:'stale',freshness:{state:'stale'}}};
console.log(JSON.stringify({
  names: rows.map(r => r.entity.label),
  firstRelationship: rows[0]?.relationship,
  firstContext: rows[0]?.context,
  sourceCount: rows[0]?.sourceCount,
  pathEntities: path?.entities.map(e => e.id),
  staleRows: briefRows(stale).length,
  malformedSnapshotRows: briefRows({...stale, brief:{id:'unverified',freshness:{state:'unverified'}}}).length,
  nullGroupRows: briefRows({...graph, brief:{...graph.brief, groups:[null]}}).length,
  nullItemRows: briefRows({...graph, brief:{...graph.brief, groups:[{title:'Example',items:[null]}]}}).flatMap(g=>g.items).length,
  validSnapshot: validGraphSnapshot(graph),
  nullEntityRejected: !validGraphSnapshot({...graph,entities:[null]}),
  nullEdgeRejected: !validGraphSnapshot({...graph,edges:[null]}),
  objectTitleRejected: !validGraphSnapshot({...graph,brief:{title:{unexpected:true}}}),
  objectTypeRejected: !validGraphSnapshot({...graph,entities:[{id:'example',label:'Example',entity_type:{unexpected:true}}]}),
  objectAttributionRejected: !validGraphSnapshot({...graph,brief:{...graph.brief,contribution:{reported:{application:{unexpected:true}}}}}),
  missingSourcesRejected: !validGraphSnapshot({...graph,edges:[{id:'example',subject:'example',predicate:'example',object:'example'}]}),
  legacy: relationshipLabel({predicate:'invests-in',knowledge:{qualifiers:{investment_status:'committed-contingent'}}}),
  discussed: relationshipLabel({predicate:'invests-in',knowledge:{qualifiers:{investment_status:'discussed'}}}),
  completed: relationshipLabel({predicate:'invests-in',knowledge:{qualifiers:{investment_status:'completed'}}})
}));
