# Architecture

**Proposed design:** This sketch does not establish implemented or deployed
applications. See the [project status](../README.md).

Education Tools uses a small API gateway to route traffic to different micro apps.

```mermaid
graph TD
    User --> WebApp
    WebApp --> API
    API -->|Requests| AlgebraService
    API --> StudyService
    AlgebraService --> DB[(Shared DB)]
    StudyService --> DB
```

Each learning tool runs as its own service behind the gateway. Data is stored in
a shared database so new features can be added without changing the overall flow.
