import fs from 'node:fs';
import assert from 'node:assert/strict';
import { topology } from '../../apps/memory_graph/src/neighborhoodModel.js';
import { motionLayout, motionPlan, mapLabelLines } from '../../apps/memory_graph/src/neighborhoodMotion.js';
const { before, after, third } = JSON.parse(fs.readFileSync(0, 'utf8'));
const a = motionLayout(topology(before)), b = motionLayout(topology(after)), c = motionLayout(topology(third));
const saved = JSON.stringify([a.nodes, b.nodes, before, after]);
const sample = motionPlan(a, b), first = sample(0), middle = sample(.5), last = sample(1);
const get = (frame, id) => frame.nodes.find(n => n.id === id);
const oldFocus = get(a, after.start), newFocus = get(b, after.start), movingFocus = get(middle, after.start);
assert.deepEqual([get(first, after.start).x, get(first, after.start).y], [oldFocus.x, oldFocus.y]);
assert.deepEqual([get(last, after.start).x, get(last, after.start).y], [450, 345]);
assert.equal(get(last, after.start).radius, 54);
assert.deepEqual(mapLabelLines(get(last, after.start)), ['Avery', 'Rivera']);
assert.equal(get(last, after.start).labelY, -5);
const distance = (x, y) => Math.hypot(x.x - y.x, x.y - y.y);
assert.ok(distance(movingFocus, oldFocus) > 0 && distance(movingFocus, newFocus) > 0);
assert.ok(distance(movingFocus, oldFocus) < distance(newFocus, oldFocus));
assert.equal(get(first, 'place').opacity, 0);
assert.ok(get(middle, 'place').opacity > 0 && get(middle, 'place').opacity < 1);
assert.equal(get(first, 'taylor').exiting, true);
assert.equal(get(last, 'taylor'), undefined);
assert.deepEqual(last.nodes.map(n => n.id), b.nodes.map(n => n.id));
assert.equal(get(motionPlan(a, b, false)(0), 'taylor'), undefined);
const interrupted = motionPlan(middle, c)(0);
assert.deepEqual([get(interrupted, after.start).x, get(interrupted, after.start).y, get(interrupted, after.start).radius], [movingFocus.x, movingFocus.y, movingFocus.radius]);
const allowedEdges = new Map([...a.edges, ...b.edges].map(e => [e.id, e]));
for (const frame of [first, middle, last]) {
  const ids = new Set(frame.nodes.map(n => n.id));
  assert.ok(frame.nodes.every(n => [n.x, n.y, n.radius, n.labelY, n.opacity].every(Number.isFinite) && n.opacity >= 0 && n.opacity <= 1));
  for (const edge of frame.edges) {
    assert.ok(ids.has(edge.subject) && ids.has(edge.object));
    assert.equal(edge.subject, allowedEdges.get(edge.id).subject);
    assert.equal(edge.object, allowedEdges.get(edge.id).object);
  }
}
assert.equal(JSON.stringify([a.nodes, b.nodes, before, after]), saved);
console.log(JSON.stringify({ result: 'passed' }));
