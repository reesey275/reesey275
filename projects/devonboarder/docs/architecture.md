# Architecture

DevOnboarder runs as a Compose-managed suite of services that automate onboarding
workflows across Discord and the web. The public API brokers requests from the
Discord bot and the coordinator-facing frontend, delegates credential checks to
the auth service, and persists shared state in the program database. Supporting
tooling—`docker-compose.yml`, the migration runner, and diagnostics utilities—keeps
those services aligned and observable during day-to-day operations.

```mermaid
flowchart LR
    subgraph Client Interfaces
        Frontend[Frontend (services/frontend)]
        DiscordBot[Discord Bot (services/discord-bot)]
    end

    subgraph Core Services
        API[Program API (services/api)]
        Auth[Auth Service (services/auth)]
    end

    subgraph Data Plane
        DB[(Shared Program Database (infra/db))]
    end

    subgraph Supporting Tooling
        Compose[docker-compose.yml]
        Migrations[Migration Runner]
        Diagnostics[Diagnostics Suite]
    end

    Frontend -->|REST + Webhooks| API
    DiscordBot -->|Intake Commands| API
    API -->|Token Checks| Auth
    Auth --> DB
    API --> DB

    Compose --> Frontend
    Compose --> DiscordBot
    Compose --> API
    Compose --> Auth
    Compose --> DB
    Compose --> Migrations
    Compose --> Diagnostics

    Migrations --> DB
    Diagnostics --> Frontend
    Diagnostics --> DiscordBot
    Diagnostics --> API
    Diagnostics --> Auth
    Diagnostics --> DB
```

## Service responsibilities

- **Program API:** Normalizes onboarding workflows, exposes REST and webhook
  entry points, and issues tasks to downstream automation via a single
  orchestration interface.
- **Auth service:** Manages session lifecycles, token validation, and Discord
  credential exchanges before requests touch the shared database.
- **Discord bot:** Runs the first-touch intake flow, pulls workflow templates
  from the API, and feeds back execution signals that become after action
  reports.
- **Frontend:** Gives coordinators visibility into onboarding state, audit
  trails, and diagnostics surfaced by the supporting tooling.
- **Shared program database:** Persists onboarding state, Discord session
  metadata, and diagnostic checkpoints used by the automation guardrails.

## Operational coupling

- **Docker Compose:** Defines the multi-container topology in `docker-compose.yml`.
  Every service, including the operational helpers, shares the same network and
  environment configuration so onboarding automation can be reproduced locally
  and in CI with the same command: `docker compose up`.
- **Migrations:** Ship alongside the Compose project and run as `docker compose
  run --rm migrations`. Schema changes land before services come online,
  guaranteeing that the API, auth service, and Discord bot operate against the
  same data contract during onboarding events.
- **Diagnostics:** Execute through `docker compose run --rm diagnostics` to hit
  API endpoints, verify Discord command wiring, and sanity-check the frontend.
  Results feed the shared database and surface in the frontend so coordinators
  can catch drift before it blocks a contributor.
