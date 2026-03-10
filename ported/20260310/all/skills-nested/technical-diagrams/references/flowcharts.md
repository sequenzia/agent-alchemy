# Flowcharts Reference

Flowcharts visualize process flows, decision trees, pipelines, and system architectures. They are the most versatile Mermaid diagram type.

**Keyword:** `flowchart` (prefer over legacy `graph`)

---

## Direction Keywords

| Keyword | Direction | Best For |
|---------|-----------|----------|
| `TD` / `TB` | Top to bottom | Hierarchies, process steps |
| `LR` | Left to right | Pipelines, request flows, timelines |
| `BT` | Bottom to top | Dependency trees |
| `RL` | Right to left | Rarely used |

```mermaid
flowchart LR
    A --> B --> C
```

---

## Node Shapes

| Syntax | Shape | Use For |
|--------|-------|---------|
| `A[Text]` | Rectangle | Default, general purpose |
| `A(Text)` | Rounded rectangle | Processes, steps |
| `A([Text])` | Stadium | Start/end points |
| `A[[Text]]` | Subroutine | External processes |
| `A[(Text)]` | Cylinder | Databases, storage |
| `A((Text))` | Circle | Connectors, small nodes |
| `A{Text}` | Diamond | Decisions, conditions |
| `A{{Text}}` | Hexagon | Preparation steps |
| `A>Text]` | Asymmetric | Flags, signals |
| `A[/Text/]` | Parallelogram | Input/output |
| `A[\Text\]` | Alt parallelogram | Alt input/output |
| `A[/Text\]` | Trapezoid | Transforms |
| `A[\Text/]` | Alt trapezoid | Alt transforms |
| `A(((Text)))` | Double circle | Critical nodes |

---

## Edge Types

### Solid Edges

| Syntax | Description |
|--------|-------------|
| `A --> B` | Arrow |
| `A --- B` | Line (no arrow) |
| `A -->\|label\| B` | Arrow with label |
| `A --label--> B` | Arrow with label (alt) |

### Dotted Edges

| Syntax | Description |
|--------|-------------|
| `A -.-> B` | Dotted arrow |
| `A -.- B` | Dotted line |
| `A -.->\|label\| B` | Dotted arrow with label |

### Thick Edges

| Syntax | Description |
|--------|-------------|
| `A ==> B` | Thick arrow |
| `A === B` | Thick line |
| `A ==>\|label\| B` | Thick arrow with label |

### Multi-Directional

| Syntax | Description |
|--------|-------------|
| `A <--> B` | Bidirectional arrow |
| `A o--o B` | Circle endpoints |
| `A x--x B` | Cross endpoints |

### Edge Length

Add extra dashes/dots/equals to make edges longer:
- `A ---> B` (longer than `A --> B`)
- `A -----> B` (even longer)

---

## Subgraphs

Group related nodes into labeled regions:

```mermaid
flowchart TD
    subgraph frontend["Frontend Layer"]
        A[React App] --> B[State Manager]
    end
    subgraph backend["Backend Layer"]
        C[API Server] --> D[Database]
    end
    B --> C
```

### Nested Subgraphs

```mermaid
flowchart TD
    subgraph cloud["Cloud Infrastructure"]
        subgraph compute["Compute"]
            A[App Server]
        end
        subgraph storage["Storage"]
            B[Object Store]
        end
    end
    A --> B
```

### Subgraph Direction

Override direction inside a subgraph:

```
subgraph section["Section"]
    direction LR
    A --> B --> C
end
```

---

## Styling

### classDef and :::

```mermaid
flowchart LR
    A[Input]:::primary --> B[Process]:::secondary --> C[Output]:::success

    classDef primary fill:#dbeafe,stroke:#2563eb,color:#000
    classDef secondary fill:#f3e8ff,stroke:#7c3aed,color:#000
    classDef success fill:#dcfce7,stroke:#16a34a,color:#000
```

### Inline style

```
style A fill:#dbeafe,stroke:#2563eb,color:#000
```

### Subgraph styling

```
style subgraphId fill:#f8fafc,stroke:#94a3b8,color:#000
```

### linkStyle

Style edges by their 0-based index (order of definition):

```
linkStyle 0 stroke:#2563eb,stroke-width:2px
linkStyle 1 stroke:#dc2626,stroke-dasharray:5
```

### Apply class to multiple nodes

```
class A,B,C primary
```

---

## Complete Examples

### CI/CD Pipeline

```mermaid
flowchart LR
    A([Push]):::neutral --> B[Lint]:::primary
    B --> C[Test]:::primary
    C --> D{Pass?}:::neutral
    D -->|Yes| E[Build]:::primary
    D -->|No| F[Notify]:::danger
    E --> G[Deploy Staging]:::warning
    G --> H{Approve?}:::neutral
    H -->|Yes| I[Deploy Prod]:::success
    H -->|No| J[Rollback]:::danger

    classDef primary fill:#dbeafe,stroke:#2563eb,color:#000
    classDef success fill:#dcfce7,stroke:#16a34a,color:#000
    classDef warning fill:#fef3c7,stroke:#d97706,color:#000
    classDef danger fill:#fee2e2,stroke:#dc2626,color:#000
    classDef neutral fill:#f3f4f6,stroke:#6b7280,color:#000
```

### Layered Architecture

```mermaid
flowchart TD
    subgraph presentation["Presentation Layer"]
        direction LR
        A[Web UI]:::primary
        B[Mobile App]:::primary
        C[CLI]:::primary
    end

    subgraph application["Application Layer"]
        direction LR
        D[Auth Service]:::secondary
        E[User Service]:::secondary
        F[Order Service]:::secondary
    end

    subgraph data["Data Layer"]
        direction LR
        G[(PostgreSQL)]:::neutral
        H[(Redis Cache)]:::neutral
        I[(S3 Storage)]:::neutral
    end

    A & B & C --> D & E & F
    D --> G
    E --> G & H
    F --> G & I

    classDef primary fill:#dbeafe,stroke:#2563eb,color:#000
    classDef secondary fill:#f3e8ff,stroke:#7c3aed,color:#000
    classDef neutral fill:#f3f4f6,stroke:#6b7280,color:#000

    style presentation fill:#eff6ff,stroke:#93c5fd,color:#000
    style application fill:#f5f3ff,stroke:#c4b5fd,color:#000
    style data fill:#f9fafb,stroke:#d1d5db,color:#000
```
