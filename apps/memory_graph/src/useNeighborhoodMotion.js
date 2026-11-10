import { useLayoutEffect, useRef, useState } from 'react';
import { motionLayout, motionPlan } from './neighborhoodMotion.js';
import { sameFrontier } from './neighborhoodModel.js';

export default function useNeighborhoodMotion(model, frontier, suppressed = false) {
  const [frame, setFrame] = useState(() => motionLayout(model)), [animating, setAnimating] = useState(false);
  const current = useRef(frame), priorFrontier = useRef(frontier);
  const [reduced, setReduced] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  useLayoutEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)'), update = () => setReduced(media.matches);
    media.addEventListener('change', update); return () => media.removeEventListener('change', update);
  }, []);
  useLayoutEffect(() => {
    const target = motionLayout(model), previous = current.current;
    const allowExits = !suppressed && sameFrontier(priorFrontier.current, frontier);
    priorFrontier.current = frontier;
    if (reduced || !previous.nodes.length || !target.nodes.length) {
      current.current = target; setFrame(target); setAnimating(false); return;
    }
    const sample = motionPlan(previous, target, allowExits);
    const unchanged = previous.nodes.length === target.nodes.length && target.nodes.every(n => previous.nodes.some(p => p.id === n.id && p.x === n.x && p.y === n.y && p.radius === n.radius && p.opacity === 1));
    if (unchanged) { current.current = target; setFrame(target); setAnimating(false); return; }
    let raf, started;
    current.current = sample(0); setFrame(current.current); setAnimating(true);
    const tick = now => {
      started ??= now;
      const progress = Math.min(1, (now - started) / 620);
      current.current = sample(progress); setFrame(current.current);
      if (progress < 1) raf = requestAnimationFrame(tick); else setAnimating(false);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [model, frontier, reduced, suppressed]);
  return { model: frame, animating };
}
