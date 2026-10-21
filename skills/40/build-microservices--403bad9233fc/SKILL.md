---
name: build-microservices
description: Build or modify microservice architectures. Use when adding service-to-service calls, service manifests, permission contracts, service registration, frontend client manifests, dedicated auth/accounts frontends, generated clients, API contracts, or centralized authentication and authorization across services.
---

# Build Microservices

## Core Defaults

Use this skill for systems where multiple services, workers, frontends, or CLIs communicate through explicit APIs and shared auth boundaries.

Design microservices around clear ownership, explicit contracts, service registration, permission-aware service-to-service calls, generated clients where useful, and strong operational visibility. Avoid hidden coupling through shared databases or undocumented cross-service assumptions.

## Required Pieces

For a microservice ecosystem, define:

- one clear auth/identity authority for users, services, JWT issuance, and public keys
- per-service API contracts, preferably OpenAPI for HTTP services
- per-service manifests or metadata files describing identity, ownership, permissions, URLs, and runtime needs
- a service registration workflow that applies manifest metadata to the auth/service registry
- a dedicated auth frontend for login, signup, password recovery, and auth callbacks when browser auth is needed
- a dedicated accounts frontend for account/profile/account-settings UX when the product needs account management
- frontend client manifests for browser apps when redirect/logout/origin metadata must be registered
- generated or checked clients for important service-to-service and frontend-to-service APIs
- a docs page per service describing ownership, calls, permissions, env vars, and runbooks

## Service Manifests

Use service manifests as checked-in operational contracts, not loose documentation. A manifest should describe:

- stable service ID
- stable bare service name
- human-readable name and description
- client/service type, such as confidential backend service or public browser frontend
- whether the service should be activated during registration
- permissions provided by the service
- permissions required from other services
- service secret metadata for confidential services
- browser auth metadata for public frontends

Backend service manifests should follow this general shape:

```yaml
service:
  activate: true
  id: svc:<service-name>
  bare-id: <service-name>
  name: <Human Name>
  description: <what the service does>
  client_type: confidential_service

permissions:
  provides:
    merge: false
    claims:
      - id: service:<service-name>:<resource>:retrieve
        description: Retrieve <resource>
  requires:
    merge: false
    claims:
      - service:<other-service>:<resource>:retrieve

secrets:
  name: service-level
  expires: null
```

Public frontend manifests should follow this general shape:

```yaml
service:
  activate: true
  id: app:<app-name>
  bare-id: <app-name>
  name: <Human Name>
  description: <what the frontend does>
  client_type: public_frontend

browser_auth:
  redirect_uris:
    - https://<app-domain>/auth/callback
  post_logout_redirect_uris:
    - https://<app-domain>
  allowed_origins:
    - https://<app-domain>
  default_redirect_uri: https://<app-domain>/auth/callback

permissions:
  provides:
    merge: false
    claims: []
  requires:
    merge: false
    claims: []

secrets: null
```

Keep service IDs and bare IDs stable after registration. Changing them should be treated as creating a new service identity.

## Permissions

Model permissions as a public contract:

- `provides` declares what the service exposes to callers.
- `requires` declares what the service needs from other services.
- Provided claims should include a stable key and human-readable description.
- Required claims should reference provided permissions from other services.
- Use consistent permission keys such as `service:<service>:<resource>:<action>` for service-level permissions.
- Use `user:<service>:<resource>:<action>` when a permission is user-scoped.
- Include wildcard-style aggregate permissions when useful, such as `service:<service>:<resource>:*` and `service:<service>:*:*`.

When adding service-to-service calls, update both sides of the contract: the caller's required permission and the callee's provided permission.

## Registration Workflow

Services and browser clients should be registered from manifests through a repeatable script or CI job. The registration workflow should:

- validate manifest shape before making network calls
- create or update service/client metadata
- apply provided and requested permissions
- activate services when requested
- register browser redirect URIs, logout URIs, and allowed origins
- check service secret existence and only create secrets after an explicit decision
- support environment-specific frontend manifests when domains differ

If the repo already has a registration script or manifest schema, extend that existing workflow instead of inventing a parallel one.

## Auth And Service Calls

Backend services should:

- authenticate service-to-service calls with service credentials or signed tokens
- verify JWTs with asymmetric public keys from the auth authority
- check permissions before serving protected resources
- avoid sharing databases across service boundaries
- call other services through typed clients or explicit HTTP/gRPC clients

Browser frontends should:

- use public frontend manifests
- avoid service secrets
- declare exact redirect URIs, logout redirect URIs, and allowed origins
- use environment-specific manifests when callback domains differ

## Documentation

Document each service in `docs/services/<service>.md` or the closest existing docs structure. Include:

- service purpose and ownership
- services it calls and why
- services that call it
- permissions it provides
- permissions it requires
- manifest location
- OpenAPI/client generation details
- local run commands
- environment variables
- deployment and registration notes
