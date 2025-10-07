# Architecture

DevOnboarder runs as a collection of services that share a common automation
surface: the public API, a dedicated auth service, the Discord bot that fronts
onboarding, and the web frontend used by coordinators. Each service persists
state in the shared program database and relies on supporting tooling that keeps
the environment reproducible and observable.

```mermaid
flowchart LR
    subgraph Client Interfaces
        Frontend[Frontend Portal]
        DiscordBot[Discord Bot]
    end

    subgraph Core Services
        API[Program API]
        Auth[Auth Service]
    end

    subgraph Data Plane
        DB[(Shared Program Database)]
    end

    subgraph Supporting Tooling
        Compose[Docker Compose]
        Migrations[Schema Migration Runner]
        Diagnostics[Diagnostics Runner]
    end

    Frontend -->|REST + Webhooks| API
    DiscordBot -->|Task Hooks| API
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
```

Docker Compose anchors the automation surface by building and wiring every
service, database dependency, and operational task through a single invocation.
Migrations run inside the Compose project so schema updates travel with the same
images that ship to production, keeping the API, auth layer, and bots aligned
with the latest data model. The diagnostics runner executes in that shared
environment to probe REST, webhook, and auth flows, catching integration drift
early so onboarding automation stays reliable for new contributors.
