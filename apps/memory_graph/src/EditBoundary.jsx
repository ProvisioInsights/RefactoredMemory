import { createContext } from 'react';

// A save with an uncertain outcome keeps its exact arguments and blocks
// accidental navigation until an identical retry or an explicit reload.
export default createContext({ set: () => {}, active: false });
