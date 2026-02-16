# Test Patterns Reference

This reference provides framework-specific test patterns and conventions for generating high-quality, behavior-driven tests. Use these patterns when producing test files for pytest, Jest, and Vitest.

---

## Common Patterns (All Frameworks)

### Arrange-Act-Assert (AAA)

The foundational test structure. Every test should have three clearly separated sections:

```
Arrange  — Set up the test data, mocks, and preconditions
Act      — Execute the behavior under test (one action per test)
Assert   — Verify the expected outcome
```

**Example (Python):**
```python
def test_user_can_change_email():
    # Arrange
    user = User(email="old@example.com")

    # Act
    user.change_email("new@example.com")

    # Assert
    assert user.email == "new@example.com"
```

**Example (TypeScript):**
```typescript
it("changes the user email", () => {
  // Arrange
  const user = new User("old@example.com");

  // Act
  user.changeEmail("new@example.com");

  // Assert
  expect(user.email).toBe("new@example.com");
});
```

### Given-When-Then

An alternative structuring pattern that reads as a specification. Useful for acceptance-criteria-driven tests:

```
Given  — A precondition or initial state
When   — An action is performed
Then   — The expected outcome is observed
```

**Example:**
```python
def test_given_existing_user_when_duplicate_email_then_raises_error():
    # Given
    repository = InMemoryUserRepository()
    repository.add(User(email="taken@example.com"))
    service = UserService(repository)

    # When / Then
    with pytest.raises(DuplicateEmailError):
        service.register(email="taken@example.com", password="secret123")
```

### Test Isolation

Every test must be independent:
- No shared mutable state between tests
- No reliance on test execution order
- Each test sets up its own preconditions and cleans up after itself
- Use fixtures (pytest) or beforeEach/afterEach (Jest/Vitest) for shared setup

### One Assertion Per Concept

A test should verify one logical concept. Multiple `assert` statements are acceptable when they verify different aspects of the same behavior:

```python
# Good — multiple asserts verifying one concept (user creation)
def test_creates_user_with_defaults():
    user = create_user(email="test@example.com")
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.created_at is not None

# Bad — testing two unrelated concepts in one test
def test_user_creation_and_login():
    user = create_user(email="test@example.com")
    assert user.is_active is True
    token = login(user.email, "password")
    assert token is not None  # This is a separate behavior
```

---

## Behavior-Driven vs Implementation-Detail Tests

### What to Prefer: Behavior-Driven Tests

Behavior-driven tests verify **what** the code does, not **how** it does it. They survive refactoring because they test the public contract.

**Characteristics of good behavior-driven tests:**
- Test inputs and outputs (public API)
- Describe the behavior in the test name
- Do not depend on internal data structures
- Survive refactoring when behavior stays the same
- Read like a specification of the feature

**Good example — tests behavior:**
```python
def test_order_total_includes_tax():
    order = Order(items=[Item(price=100), Item(price=50)])
    assert order.total() == 165.0  # 150 + 10% tax
```

```typescript
it("calculates order total including tax", () => {
  const order = new Order([new Item(100), new Item(50)]);
  expect(order.total()).toBe(165.0);
});
```

### What to Avoid: Implementation-Detail Tests

Implementation-detail tests break when you refactor without changing behavior. They test **how** the code works internally.

**Characteristics of implementation-detail tests:**
- Assert on internal method calls or call counts
- Mock internal collaborators that are not boundary dependencies
- Check private state directly
- Break when refactoring without behavior change
- Read like a description of the implementation

**Bad example — tests implementation details:**
```python
def test_order_calls_tax_calculator(mocker):
    calc = mocker.patch("orders.TaxCalculator.calculate")
    calc.return_value = 15.0
    order = Order(items=[Item(price=100), Item(price=50)])
    order.total()
    calc.assert_called_once_with(150.0)  # Tied to internal implementation
```

```typescript
it("calls tax calculator with subtotal", () => {
  const calcSpy = jest.spyOn(TaxCalculator, "calculate");
  const order = new Order([new Item(100), new Item(50)]);
  order.total();
  expect(calcSpy).toHaveBeenCalledWith(150.0); // Breaks if refactored
});
```

### When Implementation-Detail Tests Are Acceptable

Some situations justify testing implementation details:
- **External service calls**: Verify the correct API endpoint is called with correct parameters
- **Side effects**: Verify an email was sent, a log was written, or a metric was recorded
- **Security-critical paths**: Verify a specific hashing algorithm is used
- **Performance-critical paths**: Verify caching or batching is applied

When writing such tests, add a comment explaining why the implementation detail matters:

```python
def test_password_uses_bcrypt_hashing():
    """Verify bcrypt is used — security requirement, not an implementation preference."""
    user = User(password="secret")
    assert user.password_hash.startswith("$2b$")
```

---

## pytest Patterns

### Test Naming Conventions

```
test_{behavior_description}
test_{given}_{when}_{then}
test_{method_name}_{scenario}_{expected_result}
```

**Examples:**
```python
def test_user_registration_with_valid_email():
def test_given_empty_cart_when_checkout_then_raises_error():
def test_calculate_total_with_discount_returns_reduced_price():
```

### Fixtures

Use fixtures for reusable test setup. Prefer function-scoped fixtures for isolation:

```python
import pytest

@pytest.fixture
def user():
    """Create a standard test user."""
    return User(
        email="test@example.com",
        name="Test User",
    )

@pytest.fixture
def authenticated_client(client, user):
    """Create an authenticated test client."""
    token = create_token(user)
    client.headers["Authorization"] = f"Bearer {token}"
    return client

def test_profile_returns_user_data(authenticated_client, user):
    response = authenticated_client.get("/api/profile")
    assert response.status_code == 200
    assert response.json()["email"] == user.email
```

**Fixture scopes:**
```python
@pytest.fixture(scope="function")   # Default — new instance per test (preferred)
@pytest.fixture(scope="class")      # Shared within a test class
@pytest.fixture(scope="module")     # Shared within a test module
@pytest.fixture(scope="session")    # Shared across entire test session (use sparingly)
```

### conftest.py Conventions

Place shared fixtures in `conftest.py` files at appropriate directory levels:

```
tests/
├── conftest.py              # Project-wide fixtures (db, client, factories)
├── unit/
│   ├── conftest.py          # Unit test fixtures (mocks, stubs)
│   └── test_user.py
├── integration/
│   ├── conftest.py          # Integration fixtures (real db, test server)
│   └── test_api.py
└── e2e/
    ├── conftest.py          # E2E fixtures (browser, full app)
    └── test_workflow.py
```

**Common conftest.py patterns:**
```python
# tests/conftest.py
import pytest

@pytest.fixture
def db_session():
    """Provide a database session that rolls back after each test."""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def factory(db_session):
    """Provide a test data factory."""
    return TestFactory(db_session)
```

### Parametrize

Use `@pytest.mark.parametrize` to test multiple inputs against the same logic:

```python
@pytest.mark.parametrize("email,is_valid", [
    ("user@example.com", True),
    ("user@sub.example.com", True),
    ("user+tag@example.com", True),
    ("", False),
    ("not-an-email", False),
    ("@example.com", False),
    ("user@", False),
])
def test_email_validation(email, is_valid):
    assert validate_email(email) == is_valid
```

**Parametrize with IDs for readable output:**
```python
@pytest.mark.parametrize("status_code,expected_retry", [
    pytest.param(429, True, id="rate-limited"),
    pytest.param(500, True, id="server-error"),
    pytest.param(502, True, id="bad-gateway"),
    pytest.param(400, False, id="client-error-no-retry"),
    pytest.param(404, False, id="not-found-no-retry"),
])
def test_retry_on_status_code(status_code, expected_retry):
    assert should_retry(status_code) == expected_retry
```

### Markers

Use markers to categorize tests:

```python
# pytest.ini or pyproject.toml
# [tool.pytest.ini_options]
# markers = [
#     "slow: marks tests as slow (deselect with '-m \"not slow\"')",
#     "integration: marks integration tests",
#     "e2e: marks end-to-end tests",
# ]

@pytest.mark.slow
def test_full_data_migration():
    ...

@pytest.mark.integration
def test_database_persistence():
    ...

# Run specific markers:
# pytest -m "not slow"
# pytest -m integration
```

### Exception Testing

```python
def test_raises_on_invalid_input():
    with pytest.raises(ValueError, match="email cannot be empty"):
        validate_email("")

def test_raises_specific_error_type():
    with pytest.raises(NotFoundError) as exc_info:
        find_user(id="nonexistent")
    assert exc_info.value.resource == "User"
```

### Mocking with pytest-mock

```python
def test_sends_welcome_email(mocker):
    mock_send = mocker.patch("users.services.send_email")
    register_user(email="new@example.com")
    mock_send.assert_called_once_with(
        to="new@example.com",
        template="welcome",
    )
```

---

## Jest Patterns

### Test Naming Conventions

Use `describe` blocks for grouping and `it` or `test` for individual tests:

```typescript
describe("OrderService", () => {
  describe("calculateTotal", () => {
    it("sums item prices with tax", () => { ... });
    it("applies discount when coupon is valid", () => { ... });
    it("throws when cart is empty", () => { ... });
  });

  describe("placeOrder", () => {
    it("creates order with pending status", () => { ... });
    it("sends confirmation email", () => { ... });
  });
});
```

**Naming conventions:**
- `describe` — noun (class/module/function name)
- `it` — reads as a sentence: "it {does something}"
- Avoid implementation language in test names

### Setup and Teardown

```typescript
describe("UserRepository", () => {
  let repository: UserRepository;
  let db: TestDatabase;

  beforeAll(async () => {
    // Runs once before all tests in this describe block
    db = await TestDatabase.create();
  });

  afterAll(async () => {
    // Runs once after all tests
    await db.destroy();
  });

  beforeEach(async () => {
    // Runs before each test — preferred for isolation
    repository = new UserRepository(db);
    await db.clean();
  });

  afterEach(() => {
    // Runs after each test
    jest.restoreAllMocks();
  });

  it("finds user by email", async () => {
    await repository.create({ email: "test@example.com" });
    const user = await repository.findByEmail("test@example.com");
    expect(user).toBeDefined();
    expect(user!.email).toBe("test@example.com");
  });
});
```

### jest.mock

Mock entire modules:

```typescript
// Mock at the top of the file
jest.mock("../services/emailService");

import { EmailService } from "../services/emailService";

const mockEmailService = jest.mocked(EmailService);

describe("UserRegistration", () => {
  it("sends welcome email after registration", async () => {
    mockEmailService.prototype.send.mockResolvedValue(undefined);

    await registerUser({ email: "new@example.com" });

    expect(mockEmailService.prototype.send).toHaveBeenCalledWith(
      expect.objectContaining({
        to: "new@example.com",
        template: "welcome",
      })
    );
  });
});
```

**Manual mocks (for complex modules):**
```
__mocks__/
  emailService.ts    # Auto-used when jest.mock("../services/emailService")
```

### jest.fn and jest.spyOn

```typescript
// Create a standalone mock function
const mockCallback = jest.fn();
mockCallback.mockReturnValue(42);
mockCallback.mockResolvedValue({ data: "result" });

// Spy on an existing method
const spy = jest.spyOn(calculator, "add");
calculator.add(1, 2);
expect(spy).toHaveBeenCalledWith(1, 2);
expect(spy).toHaveReturnedWith(3);
```

### Async Testing

```typescript
it("fetches user data", async () => {
  const user = await userService.getById("123");
  expect(user.name).toBe("Test User");
});

it("rejects with error for invalid id", async () => {
  await expect(userService.getById("invalid"))
    .rejects.toThrow("User not found");
});
```

### Test Utilities and Custom Matchers

```typescript
// test-utils.ts
export function createTestUser(overrides: Partial<User> = {}): User {
  return {
    id: "test-id",
    email: "test@example.com",
    name: "Test User",
    createdAt: new Date("2026-01-01"),
    ...overrides,
  };
}

// Usage in tests
it("displays user name", () => {
  const user = createTestUser({ name: "Alice" });
  expect(formatGreeting(user)).toBe("Hello, Alice!");
});
```

### Snapshot Testing (Use Sparingly)

```typescript
// Good use — stable output like error messages or serialized config
it("formats validation errors correctly", () => {
  const errors = validate({ email: "", age: -1 });
  expect(errors).toMatchInlineSnapshot(`
    [
      "email is required",
      "age must be positive",
    ]
  `);
});

// Avoid — unstable output that changes frequently
it("renders component", () => {
  const { container } = render(<UserProfile user={user} />);
  expect(container).toMatchSnapshot(); // Fragile, breaks on any UI change
});
```

---

## Vitest Patterns

Vitest is API-compatible with Jest but includes Vitest-specific features. Most Jest patterns apply directly.

### Key Differences from Jest

| Feature | Jest | Vitest |
|---------|------|--------|
| Mock functions | `jest.fn()` | `vi.fn()` |
| Module mocks | `jest.mock()` | `vi.mock()` |
| Spy | `jest.spyOn()` | `vi.spyOn()` |
| Timers | `jest.useFakeTimers()` | `vi.useFakeTimers()` |
| Clear mocks | `jest.restoreAllMocks()` | `vi.restoreAllMocks()` |
| Config file | `jest.config.ts` | `vitest.config.ts` |
| Runner | Custom | Vite-native (faster) |

### vi.fn and vi.mock

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";

// Module mock
vi.mock("../services/emailService", () => ({
  EmailService: vi.fn().mockImplementation(() => ({
    send: vi.fn().mockResolvedValue(undefined),
  })),
}));

describe("UserRegistration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends welcome email after registration", async () => {
    const { EmailService } = await import("../services/emailService");
    const mockInstance = new EmailService();

    await registerUser({ email: "new@example.com" });

    expect(mockInstance.send).toHaveBeenCalledWith(
      expect.objectContaining({
        to: "new@example.com",
        template: "welcome",
      })
    );
  });
});
```

### vi.spyOn

```typescript
import { vi, describe, it, expect } from "vitest";

describe("Logger", () => {
  it("logs error with timestamp", () => {
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    logger.error("something failed");

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining("something failed")
    );

    consoleSpy.mockRestore();
  });
});
```

### In-Source Testing

Vitest supports tests inside source files (useful for utility functions):

```typescript
// utils.ts
export function slugify(text: string): string {
  return text.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
}

if (import.meta.vitest) {
  const { describe, it, expect } = import.meta.vitest;

  describe("slugify", () => {
    it("converts spaces to hyphens", () => {
      expect(slugify("hello world")).toBe("hello-world");
    });

    it("removes special characters", () => {
      expect(slugify("hello@world!")).toBe("helloworld");
    });
  });
}
```

### Type-Safe Mocking

```typescript
import { vi, type MockInstance } from "vitest";

let fetchSpy: MockInstance;

beforeEach(() => {
  fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ data: "test" }), { status: 200 })
  );
});

afterEach(() => {
  fetchSpy.mockRestore();
});
```

### Vitest Workspace (Monorepo)

```typescript
// vitest.workspace.ts
export default [
  "packages/*/vitest.config.ts",
  {
    test: {
      name: "unit",
      include: ["tests/unit/**/*.test.ts"],
    },
  },
  {
    test: {
      name: "integration",
      include: ["tests/integration/**/*.test.ts"],
    },
  },
];
```

---

## Test Naming Conventions Summary

| Framework | File Pattern | Test Pattern | Example |
|-----------|-------------|--------------|---------|
| pytest | `test_*.py` or `*_test.py` | `def test_{description}():` | `test_user_registration.py` |
| Jest | `*.test.ts` or `*.spec.ts` | `it("description", () => {})` | `user.test.ts` |
| Vitest | `*.test.ts` or `*.spec.ts` | `it("description", () => {})` | `user.test.ts` |

### pytest Naming

```python
# File: test_user_service.py or user_service_test.py

class TestUserService:
    def test_creates_user_with_valid_email(self):
        ...

    def test_rejects_duplicate_email(self):
        ...

# Or without class grouping:
def test_user_service_creates_user_with_valid_email():
    ...
```

### Jest/Vitest Naming

```typescript
// File: userService.test.ts or userService.spec.ts

describe("UserService", () => {
  it("creates user with valid email", () => { ... });
  it("rejects duplicate email", () => { ... });
});
```

---

## Anti-Patterns to Avoid

### 1. Testing Private Methods Directly

```python
# Bad — testing internals
def test_parse_internal_cache_key():
    service = UserService()
    key = service._build_cache_key("user", "123")  # Private method
    assert key == "user:123"

# Good — test through public API
def test_caches_user_lookup():
    service = UserService(cache=InMemoryCache())
    service.get_user("123")
    service.get_user("123")  # Second call
    assert service.repository.call_count == 1  # Only one DB call
```

### 2. Excessive Mocking

```python
# Bad — mocking everything, test verifies nothing real
def test_process_order(mocker):
    mocker.patch("orders.validate_order", return_value=True)
    mocker.patch("orders.calculate_total", return_value=100)
    mocker.patch("orders.save_order", return_value=Order(id=1))
    mocker.patch("orders.send_confirmation")
    result = process_order(order_data)
    assert result.id == 1  # This test only verifies mocks talk to each other

# Good — test with real collaborators, mock only boundaries
def test_process_order(db_session, mock_email_service):
    order_data = {"items": [{"product_id": 1, "quantity": 2}]}
    result = process_order(order_data)
    assert result.status == "confirmed"
    assert result.total == 25.98
    mock_email_service.send.assert_called_once()
```

### 3. Test Logic Duplication

```python
# Bad — reimplementing the production logic in the test
def test_discount_calculation():
    price = 100
    discount = 0.2
    expected = price - (price * discount)  # Duplicating the logic
    assert calculate_discount(price, discount) == expected

# Good — use known expected values
def test_discount_calculation():
    assert calculate_discount(100, 0.2) == 80.0
```

### 4. Non-Deterministic Tests

```python
# Bad — depends on current time
def test_token_expiry():
    token = create_token()
    assert token.expires_at > datetime.now()  # Flaky if slow

# Good — control time explicitly
def test_token_expiry(freezer):
    freezer.move_to("2026-01-01T00:00:00")
    token = create_token(ttl_seconds=3600)
    assert token.expires_at == datetime(2026, 1, 1, 1, 0, 0)
```

### 5. Assertion-Free Tests

```python
# Bad — no assertion, only verifies "doesn't crash"
def test_process_data():
    data = load_test_data()
    process(data)  # No assert — what are we verifying?

# Good — verify the expected outcome
def test_process_data_returns_summary():
    data = load_test_data()
    result = process(data)
    assert result.total_records == 42
    assert result.errors == []
```
