# Conversion Result: skill-dev-tools-code-quality

## Metadata

| Field | Value |
|-------|-------|
| Component ID | skill-dev-tools-code-quality |
| Component Type | skill |
| Group | dev-tools |
| Name | code-quality |
| Source Path | claude/dev-tools/skills/code-quality/SKILL.md |
| Target Path | skills/code-quality/SKILL.md |
| Fidelity Score | 68% |
| Fidelity Band | yellow |
| Status | partial |

## Converted Content

~~~markdown
---
description: Provides code quality principles including SOLID, DRY, testing strategies, and best practices for implementation review. Use when reviewing code or applying quality standards.
user-invocable: false
---

# Code Quality

This skill provides code quality principles and best practices for reviewing and improving implementations.

---

## SOLID Principles

### Single Responsibility Principle (SRP)
A class/function should have one reason to change.

**Bad:**
```typescript
class UserService {
  createUser(data) { /* creates user */ }
  sendEmail(user) { /* sends email */ }
  generateReport(users) { /* generates report */ }
}
```

**Good:**
```typescript
class UserService {
  createUser(data) { /* creates user */ }
}
class EmailService {
  sendEmail(user) { /* sends email */ }
}
class ReportService {
  generateReport(users) { /* generates report */ }
}
```

### Open/Closed Principle (OCP)
Open for extension, closed for modification.

**Bad:** Adding new payment types requires modifying existing code
```typescript
function processPayment(type, amount) {
  if (type === 'credit') { /* ... */ }
  else if (type === 'debit') { /* ... */ }
  // Must modify to add new types
}
```

**Good:** New payment types can be added without modification
```typescript
interface PaymentProcessor {
  process(amount: number): Promise<void>;
}
class CreditProcessor implements PaymentProcessor { /* ... */ }
class DebitProcessor implements PaymentProcessor { /* ... */ }
```

### Liskov Substitution Principle (LSP)
Subtypes must be substitutable for their base types.

**Bad:**
```typescript
class Bird {
  fly() { /* ... */ }
}
class Penguin extends Bird {
  fly() { throw new Error("Can't fly!"); } // Violates LSP
}
```

**Good:**
```typescript
class Bird { /* ... */ }
class FlyingBird extends Bird {
  fly() { /* ... */ }
}
class Penguin extends Bird { /* no fly method */ }
```

### Interface Segregation Principle (ISP)
Clients shouldn't depend on interfaces they don't use.

**Bad:**
```typescript
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}
```

**Good:**
```typescript
interface Workable { work(): void; }
interface Eatable { eat(): void; }
interface Sleepable { sleep(): void; }
```

### Dependency Inversion Principle (DIP)
Depend on abstractions, not concretions.

**Bad:**
```typescript
class UserService {
  private db = new PostgresDatabase();
}
```

**Good:**
```typescript
class UserService {
  constructor(private db: Database) {}
}
```

---

## DRY, KISS, YAGNI

### DRY (Don't Repeat Yourself)
Every piece of knowledge should have a single representation.

**Apply when:**
- Same logic appears 3+ times
- Changes to one place require changes to others
- Bug fixes need to be applied in multiple places

**Don't over-apply:**
- Two similar things might diverge later
- Premature abstraction can be worse than duplication

### KISS (Keep It Simple, Stupid)
Prefer simple solutions over clever ones.

**Simple code:**
- Easy to read and understand
- Easy to debug
- Easy to modify
- Has fewer bugs

### YAGNI (You Aren't Gonna Need It)
Don't add functionality until it's needed.

**Avoid:**
- Building for hypothetical requirements
- Adding "just in case" features
- Over-engineering for scale you don't have

---

## Clean Code Principles

### Meaningful Names
```typescript
// Bad
const d = new Date();
const arr = users.filter(u => u.a > 18);

// Good
const currentDate = new Date();
const adultUsers = users.filter(user => user.age > 18);
```

### Small Functions
- Do one thing well
- Few parameters (ideally 0-3)
- Single level of abstraction

### Avoid Side Effects
```typescript
// Bad: side effect hidden in getter
getUser() {
  this.lastAccess = Date.now(); // Side effect!
  return this.user;
}

// Good: explicit about what it does
getUser() {
  return this.user;
}
recordAccess() {
  this.lastAccess = Date.now();
}
```

### Error Handling
```typescript
// Be specific about errors
class ValidationError extends Error {}
class NotFoundError extends Error {}
class AuthorizationError extends Error {}

// Handle at appropriate level
try {
  await processOrder(order);
} catch (error) {
  if (error instanceof ValidationError) {
    return res.status(400).json({ error: error.message });
  }
  if (error instanceof NotFoundError) {
    return res.status(404).json({ error: error.message });
  }
  throw error; // Re-throw unexpected errors
}
```

---

## Testing Strategies

### Test Pyramid
```
      /\
     /  \      E2E Tests (few)
    /────\
   /      \    Integration Tests (some)
  /────────\
 /          \  Unit Tests (many)
/────────────\
```

### Unit Testing
- Test individual functions/classes
- Mock dependencies
- Fast and isolated

```typescript
describe('calculateTotal', () => {
  it('sums item prices', () => {
    const items = [{ price: 10 }, { price: 20 }];
    expect(calculateTotal(items)).toBe(30);
  });

  it('applies discount', () => {
    const items = [{ price: 100 }];
    expect(calculateTotal(items, { discount: 0.1 })).toBe(90);
  });

  it('handles empty cart', () => {
    expect(calculateTotal([])).toBe(0);
  });
});
```

### Integration Testing
- Test component interactions
- Use real dependencies (or test doubles)
- Database, API integration

### Test Behavior, Not Implementation
```typescript
// Bad: tests implementation details
it('calls _internalMethod', () => {
  const spy = jest.spyOn(service, '_internalMethod');
  service.doThing();
  expect(spy).toHaveBeenCalled();
});

// Good: tests behavior
it('sends welcome email on registration', async () => {
  await service.registerUser({ email: 'test@test.com' });
  expect(emailSent).toContainEqual({
    to: 'test@test.com',
    template: 'welcome'
  });
});
```

### Edge Cases to Test
- Empty inputs
- Null/undefined
- Boundary values
- Error conditions
- Concurrent operations
- Large inputs

---

## Code Review Checklist

### Correctness
- [ ] Does the code do what it's supposed to?
- [ ] Are edge cases handled?
- [ ] Are error conditions handled?

### Security
- [ ] Is input validated?
- [ ] Are outputs escaped?
- [ ] Are secrets protected?

### Performance
- [ ] Are there N+1 queries?
- [ ] Are there unnecessary loops?
- [ ] Is caching used appropriately?

### Maintainability
- [ ] Is the code readable?
- [ ] Are names meaningful?
- [ ] Is complexity reasonable?
- [ ] Is there appropriate documentation?

### Testing
- [ ] Are there tests?
- [ ] Do tests cover edge cases?
- [ ] Are tests maintainable?

---

## Common Code Smells

| Smell | Description | Solution |
|-------|-------------|----------|
| Long Method | Function > 20-30 lines | Extract methods |
| Large Class | Class with too many responsibilities | Split into focused classes |
| Long Parameter List | > 3-4 parameters | Use parameter object |
| Duplicate Code | Same code in multiple places | Extract function |
| Dead Code | Unused code | Delete it |
| Magic Numbers | Unexplained numeric literals | Use named constants |
| Nested Conditionals | Deep if/else nesting | Early returns, extract methods |
| Feature Envy | Method uses another class's data heavily | Move method to that class |

---

## Refactoring Techniques

### Extract Function
When a code block can be grouped and named

### Inline Function
When the function body is as clear as the name

### Extract Variable
When an expression is complex

### Rename Variable/Function
When the name doesn't communicate intent

### Replace Conditional with Polymorphism
When you have repeated switch/if statements on type

### Introduce Parameter Object
When several parameters travel together
~~~

## Fidelity Report

| Mapping Type | Count | Weight | Contribution |
|-------------|-------|--------|-------------|
| Direct | 2 | 1.0 | 2.0 |
| Workaround | 1 | 0.7 | 0.7 |
| TODO | 0 | 0.2 | 0.0 |
| Omitted | 1 | 0.0 | 0.0 |
| **Total** | **4** | | **2.7** |

**Score:** 2.7 / 4 * 100 = **68%** (yellow — moderate fidelity)

**Notes:** The score reflects frontmatter-level losses only. The skill body is pure reference knowledge with no tool calls, composition references, or path variables — it converts at 100% fidelity. The 68% score is driven entirely by two frontmatter fields mapping to null/embedded. All body content is preserved verbatim.

## Decisions

| Feature | Decision Type | Original | Converted | Rationale | Confidence | Resolution Mode |
|---------|-------------|----------|-----------|-----------|------------|----------------|
| name field | relocated | `name: code-quality` in frontmatter | Derived from directory path `skills/code-quality/SKILL.md` | OpenCode derives skill name from directory structure (embedded:filename mapping). No frontmatter field needed. | high | auto |
| description field | direct | `description: Provides code quality principles...` | `description: Provides code quality principles...` (unchanged) | Direct 1:1 mapping. OpenCode skill frontmatter supports `description`. | high | N/A |
| user-invocable field | direct | `user-invocable: false` | `user-invocable: false` (unchanged) | Direct 1:1 mapping. Controls whether skill appears in command dialog. | high | N/A |
| disable-model-invocation field | omitted | `disable-model-invocation: false` | (omitted) | Maps to null in OpenCode. Value was `false` (invocation not restricted), so omitting has zero behavioral impact — OpenCode always allows model invocation of skills regardless. | high | auto |
| skill body content | direct | All SOLID/DRY/testing/refactoring reference content | Identical content preserved | No tool references, composition patterns, or path variables in body. Pure reference knowledge transfers verbatim. | high | N/A |

## Gaps

| Feature | Reason | Severity | Workaround | User Acknowledged |
|---------|--------|----------|------------|-------------------|
| disable-model-invocation | No OpenCode equivalent. Per conversion_knowledge.md: "No concept of preventing model auto-invocation. `skill` tool is always available." | cosmetic | Omit field. Original value was `false` (disabled restriction), so no functional behavior is lost. | false |
| name frontmatter field | OpenCode derives skill identity from filesystem path, not an explicit `name` field. | cosmetic | Skill name is embedded in directory path `skills/code-quality/SKILL.md` per `skill_file_pattern: {name}/SKILL.md`. | false |

## Unresolved Incompatibilities

No unresolved incompatibilities. All gaps are cosmetic and have been auto-resolved.
