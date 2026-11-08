# Optional private sync request compression

Authenticated private `/sync` requests accept identity or gzip encoding. Both wire and expanded payloads retain the existing 4 MiB limit. Authentication precedes decompression. Truncated data, extra gzip members, trailing bytes, duplicate Content-Encoding headers and unsupported encodings are rejected. Signed operations and Store admission remain unchanged. Public MCP and sync responses remain uncompressed.

The sending operator may set `REFMEM_SYNC_REQUEST_ENCODING=gzip` only after upgrading the destination. The default remains identity for older peers. Remove that setting before rolling a receiver back. This setting changes transport representation, not peer admission or network policy.

A clean scheduler stop now resumes the persisted retry deadline when a new process starts; it does not bypass backoff or a hard-error pause. Production-handler interoperability, malformed streams, expansion bounds and restart timing are covered by synthetic tests.
