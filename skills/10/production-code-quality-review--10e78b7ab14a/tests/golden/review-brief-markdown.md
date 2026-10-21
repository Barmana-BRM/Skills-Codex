# Review Brief

## Scope
- Base: `main`
- Current branch: `feature/review`
- Scope mode: `working_tree`
- Changed files: `src/app.ts`, `Dockerfile`

## Routing
- Review mode: `specialist`
- Risk level: `high`
- Why this mode: high-risk change touches sensitive production surfaces
- Reviewer set: `correctness`, `architecture`, `reliability`, `security`, `tests`
- Follow-up: `synthesizer`

## Risk Flags
- `api_or_network_boundary`
- `container_or_runtime`

## Suggested References
- `review-framework.md`
- `output-contract.md`
- `false-positive-control.md`
- `typescript.md`
- `backend-and-integrations.md`
- `verification-and-operations.md`

## Changed Line Ranges
- `src/app.ts`
  added: 10-14

## Verification Commands
- `npm test`: Verify regressions.
