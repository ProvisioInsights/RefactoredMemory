import React from 'react';
const shapes = {
  Graph: <><path d="M5 17 11 5 19 17M6 17h12"/><circle cx="11" cy="4" r="2.5"/><circle cx="4" cy="18" r="2.5"/><circle cx="20" cy="18" r="2.5"/></>,
  Review: <><path d="m3 5 2 2 3-4m-5 9 2 2 3-4m-5 9 2 2 3-4M12 5h9M12 12h9M12 19h9"/></>,
  Work: <><rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V4h8v3M3 12h18"/></>,
  Activity: <><circle cx="12" cy="12" r="9"/><path d="M12 6v7l4 2"/></>,
  Search: <><circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/></>,
  Fit: <path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>,
  Expand: <><path d="m4 20 7-7m2-2 7-7M4 14v6h6M14 4h6v6"/></>,
  Comment: <path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h2v3l5-3h9a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Z"/>,
  Edit: <><path d="m4 16 12-12 4 4L8 20H4v-4ZM13 7l4 4"/></>,
  Lock: <><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4"/></>,
};
export default function Icon({ name }) { return <svg className="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{shapes[name]}</svg>; }
