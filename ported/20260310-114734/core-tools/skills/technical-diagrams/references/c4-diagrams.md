# C4 Diagrams Reference

C4 diagrams model software architecture at multiple zoom levels — from system context down to individual components. C4 uses a unique function-call syntax that differs from other Mermaid diagram types.

**Keywords:** `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`

**Compatibility note:** C4 requires Mermaid 10.6+. Verify your rendering platform supports it.

---

## Diagram Levels

| Level | Keyword | Scope | Shows |
|-------|---------|-------|-------|
| Context | `C4Context` | Entire system | People, systems, external dependencies |
| Container | `C4Container` | Single system | Applications, databases, services within one system |
| Component | `C4Component` | Single container | Internal components of one application |
| Dynamic | `C4Dynamic` | Interaction flow | Numbered sequence of interactions |
| Deployment | `C4Deployment` | Infrastructure | Where containers run (servers, cloud, VMs) |

---

## Element Functions

### People

```
Person(alias, "Label", "Description")
Person_Ext(alias, "Label", "Description")
```

- `Person` — Internal user
- `Person_Ext` — External user

### Systems

```
System(alias, "Label", "Description")
System_Ext(alias, "Label", "Description")
System_Boundary(alias, "Label") { ... }
```

- `System` — System under design
- `System_Ext` — External system
- `System_Boundary` — Groups elements belonging to one system

### Containers

```
Container(alias, "Label", "Technology", "Description")
ContainerDb(alias, "Label", "Technology", "Description")
ContainerQueue(alias, "Label", "Technology", "Description")
Container_Ext(alias, "Label", "Technology", "Description")
Container_Boundary(alias, "Label") { ... }
```

- `Container` — Application/service
- `ContainerDb` — Database
- `ContainerQueue` — Message queue
- `Container_Ext` — External container
- `Container_Boundary` — Groups containers

### Components

```
Component(alias, "Label", "Technology", "Description")
ComponentDb(alias, "Label", "Technology", "Description")
ComponentQueue(alias, "Label", "Technology", "Description")
Component_Ext(alias, "Label", "Technology", "Description")
```

### Deployment Nodes

```
Deployment_Node(alias, "Label", "Technology") { ... }
Node(alias, "Label", "Technology") { ... }
```

---

## Relationships

```
Rel(from, to, "Label")
Rel(from, to, "Label", "Technology/Protocol")

Rel_D(from, to, "Label")    %% Downward
Rel_U(from, to, "Label")    %% Upward
Rel_L(from, to, "Label")    %% Left
Rel_R(from, to, "Label")    %% Right

Rel_Back(from, to, "Label")          %% Reverse direction
BiRel(from, to, "Label")             %% Bidirectional
```

---

## Styling

### UpdateElementStyle

```
UpdateElementStyle(alias, $bgColor="color", $fontColor="color", $borderColor="color")
```

### UpdateRelStyle

```
UpdateRelStyle(from, to, $textColor="color", $lineColor="color", $offsetX="n", $offsetY="n")
```

### Layout

```
UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

---

## Title and Description

Always include a title for context:

```
title System Context Diagram for My Application
```

---

## Complete Examples

### System Context Diagram

```mermaid
C4Context
    title System Context — SaaS Platform

    Person(customer, "Customer", "Uses the web application to manage their account and resources")
    Person(admin, "Admin", "Manages platform settings, users, and billing")
    Person_Ext(developer, "Developer", "Integrates via API")

    System(platform, "SaaS Platform", "Core platform providing resource management and analytics")

    System_Ext(email, "Email Service", "SendGrid — transactional and marketing emails")
    System_Ext(payment, "Payment Gateway", "Stripe — subscription billing and payments")
    System_Ext(monitoring, "Monitoring", "Datadog — metrics, logs, and alerting")
    System_Ext(cdn, "CDN", "CloudFront — static asset delivery")

    Rel(customer, platform, "Uses", "HTTPS")
    Rel(admin, platform, "Manages", "HTTPS")
    Rel(developer, platform, "Integrates", "REST API")
    Rel(platform, email, "Sends emails", "SMTP/API")
    Rel(platform, payment, "Processes payments", "API")
    Rel(platform, monitoring, "Sends telemetry", "Agent")
    Rel(platform, cdn, "Serves assets", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Container Diagram

```mermaid
C4Container
    title Container Diagram — SaaS Platform

    Person(customer, "Customer", "End user")
    Person(developer, "Developer", "API consumer")

    System_Boundary(platform, "SaaS Platform") {
        Container(spa, "Web App", "React, TypeScript", "Single-page application for customers")
        Container(api, "API Server", "Node.js, Express", "REST API handling all business logic")
        Container(worker, "Background Worker", "Node.js, Bull", "Async job processing")
        ContainerDb(db, "Database", "PostgreSQL", "Stores users, resources, billing")
        ContainerDb(cache, "Cache", "Redis", "Session store, rate limiting, job queue")
        ContainerQueue(queue, "Message Queue", "Redis/Bull", "Job queue for async processing")
        Container(scheduler, "Task Scheduler", "Node.js, cron", "Periodic maintenance tasks")
    }

    System_Ext(email, "Email Service", "SendGrid")
    System_Ext(payment, "Payment Gateway", "Stripe")
    System_Ext(storage, "Object Storage", "S3")

    Rel(customer, spa, "Uses", "HTTPS")
    Rel(developer, api, "Calls", "REST/HTTPS")
    Rel(spa, api, "Calls", "HTTPS/JSON")
    Rel(api, db, "Reads/writes", "SQL")
    Rel(api, cache, "Reads/writes", "Redis protocol")
    Rel(api, queue, "Enqueues jobs", "Redis protocol")
    Rel(worker, queue, "Processes jobs", "Redis protocol")
    Rel(worker, db, "Reads/writes", "SQL")
    Rel(worker, email, "Sends", "API")
    Rel(worker, storage, "Uploads", "S3 API")
    Rel(api, payment, "Charges", "API")
    Rel(scheduler, db, "Queries", "SQL")
    Rel(scheduler, queue, "Enqueues", "Redis protocol")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

### Component Diagram

```mermaid
C4Component
    title Component Diagram — API Server

    Container_Boundary(api, "API Server") {
        Component(router, "Router", "Express Router", "Routes HTTP requests to controllers")
        Component(auth, "Auth Middleware", "Passport.js", "JWT validation and session management")
        Component(controllers, "Controllers", "Express", "Request handling and response formatting")
        Component(services, "Service Layer", "TypeScript", "Business logic and orchestration")
        Component(repos, "Repositories", "TypeORM", "Data access and query building")
        Component(validators, "Validators", "Zod", "Request payload validation")
        Component(events, "Event Emitter", "EventEmitter2", "Domain event publishing")
    }

    ContainerDb(db, "Database", "PostgreSQL")
    ContainerDb(cache, "Cache", "Redis")
    ContainerQueue(queue, "Job Queue", "Bull/Redis")

    Rel(router, auth, "Authenticates via")
    Rel(router, controllers, "Delegates to")
    Rel(controllers, validators, "Validates with")
    Rel(controllers, services, "Calls")
    Rel(services, repos, "Queries via")
    Rel(services, events, "Publishes to")
    Rel(repos, db, "Reads/writes")
    Rel(services, cache, "Caches in")
    Rel(events, queue, "Enqueues to")
```

### Dynamic Diagram

```mermaid
C4Dynamic
    title User Login Flow

    ContainerDb(db, "Database", "PostgreSQL")
    ContainerDb(cache, "Cache", "Redis")
    Container(api, "API Server", "Node.js")
    Container(spa, "Web App", "React")

    Rel(spa, api, "1. POST /auth/login", "HTTPS")
    Rel(api, db, "2. Validate credentials", "SQL")
    Rel(api, api, "3. Generate JWT")
    Rel(api, cache, "4. Store session", "Redis")
    Rel(api, spa, "5. Return token", "HTTPS")
```
