---
name: build-typescript-apps
description: Build or modify standalone TypeScript Fastify applications using the user's preferred backend structure and defaults. Use when working on TypeScript APIs, Fastify routes, services, dependency integrations, models, validation, OpenAPI schemas, errors, Bun or Node runtime setup, observability, tests, Biome, or strict TypeScript app setup.
---

# Build TypeScript Apps

## Core Defaults

Build TypeScript backend apps as standalone Fastify applications by default. Do not assume a monorepo unless the existing repository is already one.

Use Bun as the default runtime and package manager for new TypeScript apps. Keep Node.js when the existing app already uses Node, has a Node lockfile/tooling contract, or depends on Node-specific runtime behavior.

Use strict TypeScript, Biome for formatting and linting, typed request and response boundaries, explicit validation, structured errors, OpenAPI schemas, and environment-specific config modules.

Prefer `src` layout with the same conceptual boundaries as the Rust apps.

## Structure

Use this default source layout:

```text
src/
├── App.ts
├── main.ts
├── routes/
├── services/
├── libs/
├── middleware/
├── models/
├── config/
├── types/
└── errors.ts
```

Keep boundaries strict:

- `routes`: Fastify endpoint registration, schemas, auth/permission hooks, request parsing, service calls, and HTTP responses.
- `services`: internal business logic, domain rules, transactions, orchestration, and reusable use cases.
- `libs`: integrations with dependencies such as database clients, Redis, Resend, Temporal, Kafka, Sentry, telemetry, logging, Liquid/templates, and external APIs.
- `models`: data/domain models, persistence models, DTO-adjacent domain shapes, and model helpers.
- `middleware`: request hooks, auth, idempotency, throttling, metrics, and request context.
- `config`: env parsing, constants, permissions, and runtime settings.
- `types`: app-wide TypeScript declarations and shared interfaces.

Do not place business rules in route handlers. Do not place dependency setup directly in route files.

## Fastify API Pattern

Routes should be thin:

- Register each domain under its own file in `src/routes`.
- Use Fastify schemas for body, params, querystring, and response.
- Include OpenAPI metadata such as tags, operation IDs, summaries, security, and standard error responses where the app exposes docs.
- Use pre-validation/pre-handler hooks for auth and permissions.
- Catch expected domain validation/not-found errors and map them to stable HTTP responses.
- Let unexpected errors bubble to the global error handler.

Services should accept explicit dependencies, usually a database handle/client and the payload needed for the use case. Keep static class services only when the project already uses that style; otherwise prefer regular functions or instance services consistently.

## Tooling

Use:

- `typescript` with `strict`, `strictNullChecks`, `isolatedModules`, `moduleResolution: "Bundler"` where appropriate, and no unnecessary `any`.
- `@biomejs/biome` for format and lint.
- Bun for local execution, scripts, dependency management, and lockfiles in new apps.
- Node.js, `tsx`, or the repo's existing runner only when the app already uses Node.
- `vitest` or the existing test runner for tests.
- `dotenv` or typed env parsing from `src/config/env.ts`.

Package scripts should cover `dev`, `build`, `lint`, `format`, `type-check`, and `test`.

## Data, Errors, And Observability

Keep repository/database calls behind `libs` or repository-style helpers when the app uses them. Keep domain decisions in services.

For runtime behavior:

- Use structured logging and request logging hooks.
- Hook Sentry/telemetry into the Fastify instance when configured.
- Register cleanup handlers for database pools, Redis clients, workers, and server shutdown.
- Keep secrets out of logs.
- Use typed custom errors for validation, not found, forbidden, and conflict cases.

## Testing And Verification

Test route behavior through Fastify injection or HTTP integration tests when possible. Test service logic directly for domain rules and edge cases.

Run the closest available checks:

- `bun run type-check` or `tsc --noEmit`
- `bun run lint`
- `bun run test`
- `bun run build`

Use the existing package manager and lockfile for existing apps. Do not migrate Node/npm/pnpm/yarn apps to Bun unless the user asks or the task is explicitly to adopt the default stack.
