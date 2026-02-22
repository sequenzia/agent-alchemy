# Complexity Signals Reference

Complexity signals are patterns in user-supplied context that indicate a project requires more thorough interview coverage. This file defines the signal categories, detection thresholds, and assessment format.

## Signal Categories

### High Weight Signals

| Signal | Detection Patterns |
|--------|-------------------|
| **Multiple subsystems** | 2+ distinct bounded contexts, separate services, or independently deployable components described |
| **Integration density** | 3+ external APIs, third-party services, or system integrations mentioned |
| **Compliance/regulatory** | GDPR, HIPAA, PCI-DSS, SOC 2, WCAG, ADA, FERPA, CCPA, FDA, FedRAMP, or similar regulatory frameworks |
| **Distributed architecture** | Microservices, event-driven architecture, CQRS, event sourcing, saga patterns, message queues, service mesh |

### Medium Weight Signals

| Signal | Detection Patterns |
|--------|-------------------|
| **Multi-role authorization** | 3+ distinct user roles, RBAC, ABAC, role hierarchies, permission matrices |
| **Complex data models** | 5+ core entities, polymorphic relationships, graph structures, multi-tenant data isolation |
| **Security concerns** | Encryption at rest/in transit, zero-trust, audit logging, secrets management, SSO/SAML/OIDC |
| **Real-time requirements** | WebSockets, SSE, sub-second latency targets, live collaboration, streaming, pub/sub |
| **Scale requirements** | Millions of users/records, 99.9%+ availability, horizontal scaling, global distribution, CDN |

### Low Weight Signals

| Signal | Detection Patterns |
|--------|-------------------|
| **Multi-platform** | iOS + Android + Web, cross-platform frameworks, responsive + native, desktop + mobile |
| **Phased rollout** | Feature flags, canary deployments, A/B testing infrastructure, gradual migration |

## Threshold Rules

A project is considered **complex** when ANY of the following conditions are met:

1. **3 or more high-weight signals** detected
2. **5 or more signals of any weight** detected (mix of high, medium, and low)

## Assessment Output Format

After scanning user-supplied context, produce an internal assessment (not shown to user):

```
## Complexity Assessment

**Signals Detected**: {count}
- High: {list of high-weight signals found}
- Medium: {list of medium-weight signals found}
- Low: {list of low-weight signals found}

**Threshold Result**: Complex / Standard
**Primary Complexity Areas**: {top 2-3 areas driving complexity}
```

## Assessment Guidelines

- **Assess content, not length**: A short document mentioning HIPAA + microservices + 5 user roles = complex. A long document describing a simple CRUD app = not complex.
- **Look for implicit signals**: "Each department manages their own data" implies multi-tenant. "Users see different dashboards based on their role" implies multi-role authorization.
- **Don't double-count**: If "microservices" and "event-driven" describe the same architecture, count as one high-weight signal (distributed architecture), not two.
- **Context matters**: A compliance mention in a "nice to have" section carries less weight than one in core requirements. Use judgment on whether a signal is central to the project.
- **When uncertain, lean toward standard**: The expanded interview is opt-in — false positives waste the user's time with an unnecessary complexity alert.
