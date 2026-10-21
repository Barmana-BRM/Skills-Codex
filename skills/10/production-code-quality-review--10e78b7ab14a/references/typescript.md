# TypeScript And Frontend Review Heuristics

Load this reference when the change includes TypeScript, JavaScript, frontend, or shared runtime contracts.

## TypeScript

Check:

- runtime validation at API and IO boundaries
- `any`, unsafe casts, non-null assertions, and silent optional chaining
- Promise rejection paths
- data parsing and narrowing before use
- config, env var, and feature-flag assumptions
- discriminated union exhaustiveness in branching logic
- schema drift between generated types and runtime payloads
- accidental widening through helper return types
- silent fallback values that hide missing server data

## React And UI

Check:

- state ownership and duplication
- stale closures and effect dependency bugs
- loading, empty, error, disabled, optimistic, and retry states
- hydration mismatch or client-only assumptions
- accessibility for labels, keyboard flow, and focus handling
- server and client component boundary leaks when the stack uses them
- mutation flows that update UI before rollback or error recovery is defined
- list keys and cache identity when data is merged incrementally

## Performance

Check:

- waterfall fetches
- repeated expensive computation in render paths
- unbounded client-side lists
- accidental re-renders due to unstable props or closures
- large serialization payloads crossing server to client boundaries
- duplicated fetch logic that defeats caching or dedupe layers

## Security

Check:

- unsafe HTML rendering
- URL construction from untrusted input
- auth state assumptions on the client
- secrets or privileged config leaking to the browser

## Review Prompts

Ask:

- where is runtime validation guaranteed, and where is it only assumed by types?
- would a rejected promise surface to the user, the error boundary, or nowhere?
- if API payload shape changes, what fails first and how obvious is the failure?
