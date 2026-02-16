# Behavior-Driven Test Rubric

This reference defines the quality scoring dimensions used by the `test-reviewer` agent to evaluate AI-generated tests. The rubric enforces behavior-driven testing practices and provides actionable feedback for improving test quality.

---

## Scoring Dimensions

Four dimensions are evaluated independently, each scored 0-100. The overall score is a weighted average of all four dimensions.

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Meaningful Assertions | 35% | Tests verify behavior and outcomes, not implementation details |
| Edge Case Coverage | 25% | Boundary conditions, error paths, and unusual scenarios covered |
| Test Independence | 20% | Tests can run in isolation without shared mutable state |
| Readability | 20% | Tests are clear, well-named, and follow consistent structure |

---

## Dimension 1: Meaningful Assertions (Weight: 35%)

Tests should verify **what** the code does (behavior), not **how** it does it (implementation). This is the most heavily weighted dimension because behavior-driven assertions are the foundation of valuable, maintainable tests.

### Scoring Criteria

| Score Range | Description | Characteristics |
|-------------|-------------|-----------------|
| 90-100 | Excellent | Every assertion targets an observable outcome; test names describe behavior; no implementation coupling |
| 70-89 | Good | Most assertions are behavior-driven; minor implementation coupling that is justified |
| 50-69 | Acceptable | Mix of behavior and implementation assertions; some tests lack clear purpose |
| 30-49 | Below Average | Heavy implementation coupling; many assertions on internals; weak test purposes |
| 0-29 | Poor | Primarily tests implementation details; assertions on call counts, internal state, private methods |

### Green Flags (Score Boosters)

- **Asserting return values**: Verifying the output of a function or method call
- **Asserting state changes**: Checking that observable state changed correctly (e.g., user.email updated)
- **Asserting error messages**: Verifying that errors contain the right message and type
- **Asserting side effects at boundaries**: Checking that an email was sent, a record was persisted, a log was written
- **Descriptive assertion messages**: Custom failure messages that explain what went wrong
- **One logical concept per test**: Each test verifies a single behavior or scenario

### Red Flags (Score Reducers)

- **Asserting call counts on internal collaborators**: `mock.assert_called_once()` on non-boundary dependencies
- **Mocking internal methods**: Patching private methods or implementation helpers
- **Testing private methods directly**: Calling `_private_method()` or accessing private fields
- **Asserting internal state**: Checking data structures that are not part of the public API
- **Assertion-free tests**: Tests that only verify "doesn't crash" without any assertions
- **Logic duplication**: Re-implementing the production logic in the test to compute expected values

### Examples

**High score (90+) -- behavior-driven:**
```python
def test_order_total_includes_tax():
    order = Order(items=[Item(price=100), Item(price=50)])
    assert order.total() == 165.0  # 150 + 10% tax

def test_registration_rejects_duplicate_email():
    service = UserService(repository=InMemoryRepo())
    service.register(email="taken@example.com", password="secret")
    with pytest.raises(DuplicateEmailError, match="already registered"):
        service.register(email="taken@example.com", password="other")
```

**Low score (below 50) -- implementation-detail-driven:**
```python
def test_order_calls_tax_calculator(mocker):
    calc = mocker.patch("orders.TaxCalculator.calculate")
    calc.return_value = 15.0
    order = Order(items=[Item(price=100)])
    order.total()
    calc.assert_called_once_with(100.0)  # Tied to internal wiring

def test_user_service_calls_repository_save(mocker):
    repo = mocker.patch("users.UserRepository.save")
    service = UserService(repository=repo)
    service.register(email="new@example.com", password="secret")
    repo.save.assert_called_once()  # Tests plumbing, not behavior
```

---

## Dimension 2: Edge Case Coverage (Weight: 25%)

Tests should cover boundary conditions, error paths, and unusual-but-valid scenarios beyond the "happy path."

### Scoring Criteria

| Score Range | Description | Characteristics |
|-------------|-------------|-----------------|
| 90-100 | Excellent | Comprehensive boundary testing; all error paths covered; race conditions considered |
| 70-89 | Good | Most boundaries tested; key error paths covered; minor gaps |
| 50-69 | Acceptable | Happy path well-tested; some edge cases present; error paths partially covered |
| 30-49 | Below Average | Primarily happy path; few edge cases; error handling largely untested |
| 0-29 | Poor | Only happy path tested; no boundary conditions; no error scenarios |

### What to Look For

**Boundary conditions:**
- Empty collections (empty list, empty string, empty dict)
- Null/None/undefined values
- Maximum and minimum values (integer overflow, max string length)
- Zero, negative numbers, floating-point edge cases
- Single-element collections (off-by-one scenarios)
- First and last items in sequences

**Error paths:**
- Invalid input (wrong type, malformed data, out-of-range values)
- Missing required data (null fields, absent keys)
- External service failures (network errors, timeouts, 500 responses)
- Permission denied / authorization failures
- Resource not found scenarios
- Concurrent modification conflicts

**Concurrency and race conditions** (where applicable):
- Simultaneous writes to the same resource
- Read-after-write consistency
- Timeout handling during long operations

**Unusual but valid scenarios:**
- Unicode characters in string inputs
- Very large inputs (stress boundaries)
- Leap years, timezone edge cases (for date handling)
- Empty but valid configurations

### Examples

**High score (90+):**
```python
@pytest.mark.parametrize("input_val,expected", [
    ("user@example.com", True),     # Valid standard email
    ("user+tag@example.com", True), # Valid with tag
    ("", False),                     # Empty string
    (None, False),                   # None value
    ("@example.com", False),         # Missing local part
    ("user@", False),                # Missing domain
    ("a" * 255 + "@example.com", False),  # Exceeds max length
])
def test_email_validation(input_val, expected):
    assert validate_email(input_val) == expected

def test_transfer_with_insufficient_funds():
    account = Account(balance=50)
    with pytest.raises(InsufficientFundsError):
        account.transfer(amount=100, to=other_account)
    assert account.balance == 50  # Balance unchanged on failure
```

**Low score (below 30):**
```python
def test_email_validation():
    assert validate_email("user@example.com") is True
    # Only tests the happy path -- no invalid inputs, no boundaries
```

---

## Dimension 3: Test Independence (Weight: 20%)

Each test must be able to run in isolation, in any order, without affecting other tests.

### Scoring Criteria

| Score Range | Description | Characteristics |
|-------------|-------------|-----------------|
| 90-100 | Excellent | Full isolation; proper fixtures/setup; no shared mutable state; mock cleanup |
| 70-89 | Good | Mostly isolated; minor shared state that is reset between tests |
| 50-69 | Acceptable | Some tests depend on setup from other tests; shared state partially managed |
| 30-49 | Below Average | Significant shared mutable state; test order matters in several cases |
| 0-29 | Poor | Tests routinely depend on other tests; global state pollutes across tests |

### Green Flags (Score Boosters)

- **Proper setup/teardown**: Using fixtures (`@pytest.fixture`), `beforeEach`/`afterEach`, or factory functions
- **Fresh instances per test**: Each test creates its own data rather than sharing mutable objects
- **Mock cleanup**: Mocks are restored after each test (`vi.restoreAllMocks()`, `mocker` auto-cleanup)
- **No global state mutation**: Tests do not modify module-level variables, singletons, or environment variables without cleanup
- **Database transaction rollback**: Integration tests use transactions that roll back after each test

### Red Flags (Score Reducers)

- **Tests that depend on other tests**: Test B assumes Test A ran first and created some state
- **Shared global mutable state**: Module-level variables modified by tests without reset
- **Order-dependent test suites**: Tests fail when run in a different order or individually
- **Shared mutable fixtures without reset**: A fixture that accumulates state across tests
- **Missing mock cleanup**: Mocks or patches that leak into subsequent tests
- **Environment variable mutations**: Setting `os.environ` or `process.env` without restoring original values

### Examples

**High score (90+) -- fully isolated:**
```python
@pytest.fixture
def user_service():
    """Fresh service instance per test with in-memory dependencies."""
    repo = InMemoryUserRepository()
    email_service = FakeEmailService()
    return UserService(repo=repo, email_service=email_service)

def test_registers_new_user(user_service):
    result = user_service.register("new@example.com", "password")
    assert result.email == "new@example.com"

def test_rejects_duplicate_registration(user_service):
    user_service.register("taken@example.com", "password")
    with pytest.raises(DuplicateEmailError):
        user_service.register("taken@example.com", "other")
```

**Low score (below 30) -- coupled tests:**
```python
# Bad -- shared mutable state, order-dependent
created_user = None

def test_create_user():
    global created_user
    created_user = UserService().register("test@example.com", "password")
    assert created_user is not None

def test_get_user():
    # Fails if test_create_user didn't run first
    user = UserService().get_by_email(created_user.email)
    assert user.email == "test@example.com"
```

---

## Dimension 4: Readability (Weight: 20%)

Tests should be easy to read, understand, and maintain. A test file should read like a specification of the feature it tests.

### Scoring Criteria

| Score Range | Description | Characteristics |
|-------------|-------------|-----------------|
| 90-100 | Excellent | Clear names; consistent AAA structure; good helpers; reads like documentation |
| 70-89 | Good | Mostly clear; AAA followed; minor naming or structure inconsistencies |
| 50-69 | Acceptable | Understandable but verbose or inconsistent; some unclear test names |
| 30-49 | Below Average | Confusing test names; inconsistent structure; hard to understand intent |
| 0-29 | Poor | Cryptic names; no discernible structure; excessive duplication; unclear intent |

### Green Flags (Score Boosters)

- **Descriptive test names**: Names describe the scenario and expected behavior (`test_user_with_expired_token_gets_401`)
- **AAA pattern followed**: Each test has clearly separated Arrange, Act, and Assert sections
- **Reasonable test length**: Tests are long enough to be clear but short enough to be scannable (5-20 lines typical)
- **Consistent style**: All tests in the file follow the same structure and naming convention
- **Effective use of helpers/fixtures**: Shared setup extracted into reusable helpers to reduce duplication
- **Comments for non-obvious setup**: A brief comment explains why unusual test data or configuration is needed

### Red Flags (Score Reducers)

- **Cryptic test names**: `test_1`, `test_case_a`, `test_it_works`
- **Missing structure**: No discernible Arrange/Act/Assert separation
- **Excessive test length**: Tests over 30 lines with deeply nested logic
- **Inconsistent style**: Mix of naming conventions, assertion styles, or structure within one file
- **Copy-paste duplication**: Same setup repeated across multiple tests instead of using fixtures
- **Magic values**: Hard-coded numbers or strings without context (`assert result == 42`)

### Examples

**High score (90+):**
```python
class TestOrderDiscount:
    """Tests for the order discount calculation behavior."""

    @pytest.fixture
    def standard_order(self):
        """An order with two items totaling $150."""
        return Order(items=[Item(price=100), Item(price=50)])

    def test_no_discount_below_threshold(self, standard_order):
        # Act
        total = standard_order.calculate_total(discount_threshold=200)

        # Assert
        assert total == 165.0  # $150 + 10% tax, no discount applied

    def test_applies_percentage_discount_above_threshold(self, standard_order):
        # Act
        total = standard_order.calculate_total(
            discount_threshold=100,
            discount_percent=20,
        )

        # Assert
        assert total == 132.0  # ($150 - 20%) + 10% tax = $120 + $12
```

**Low score (below 30):**
```python
def test1():
    o = Order(items=[Item(price=100), Item(price=50)])
    assert o.calculate_total(200) == 165.0
    assert o.calculate_total(100, 20) == 132.0
    o2 = Order(items=[])
    assert o2.calculate_total(0) == 0
    # Multiple unrelated scenarios in one test, no clear structure
```

---

## Overall Score Calculation

### Formula

The overall score is a weighted average of the four dimensions:

```
overall = 0.35 * meaningful_assertions
        + 0.25 * edge_case_coverage
        + 0.20 * test_independence
        + 0.20 * readability
```

### Example Calculation

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Meaningful Assertions | 85 | 0.35 | 29.75 |
| Edge Case Coverage | 70 | 0.25 | 17.50 |
| Test Independence | 90 | 0.20 | 18.00 |
| Readability | 80 | 0.20 | 16.00 |
| **Overall** | | | **81.25** |

### Threshold

- **Default threshold**: 70 (configurable via `.claude/agent-alchemy.local.md` under `tdd.test-review-threshold`)
- **Below threshold**: The test suite is flagged for improvement with dimension-specific suggestions
- **At or above threshold**: The test suite passes quality review

#### Configuring the Threshold

In `.claude/agent-alchemy.local.md`:

```markdown
## TDD Settings
- `tdd.test-review-threshold`: 70  <!-- default; set higher for stricter quality gates -->
```

Set higher values (80-90) for projects requiring strict quality standards. Set lower values (50-60) for legacy codebases or exploratory development where any tests are an improvement.

---

## Scoring Guidelines

### 90-100: Excellent

Comprehensive, behavior-driven, well-structured tests. The test file reads like a specification.

- All assertions target observable behavior
- Thorough edge case and error path coverage
- Full test isolation with proper fixtures
- Clear names, AAA structure, consistent style
- **Action**: No changes needed. Optionally note exemplary patterns for reuse.

### 70-89: Good

Solid tests with minor gaps. Meets quality standards for most projects.

- Most assertions are behavior-driven; minor implementation coupling with justification
- Key edge cases covered; some minor boundaries missing
- Tests are mostly isolated; minor shared state that is managed
- Readable with minor inconsistencies
- **Action**: Provide specific suggestions for the weaker dimensions but approve the tests.

### 50-69: Acceptable

Tests work but have quality issues that should be addressed.

- Mix of behavior and implementation assertions
- Happy path well-tested but edge cases sparse
- Some test interdependencies
- Structure is inconsistent or unclear in places
- **Action**: Flag specific improvements. Provide concrete before/after examples for the lowest-scoring dimension.

### Below 50: Poor

Tests need significant improvement before they provide reliable value.

- Primarily tests implementation details
- Only happy path; no edge cases or error handling
- Tests depend on execution order or shared global state
- Cryptic names, no structure, excessive duplication
- **Action**: Provide concrete improvement suggestions for each dimension. Include rewritten examples showing how to transform the worst tests into behavior-driven equivalents.

---

## Implementation Detail Detection

### Anti-Patterns to Flag

The following patterns indicate implementation-detail testing and should be flagged by the test-reviewer agent:

| Anti-Pattern | Description | Example |
|-------------|-------------|---------|
| **Internal mock assertions** | Asserting call counts or arguments on mocked internal collaborators | `internal_helper.assert_called_once_with(...)` |
| **Private method testing** | Directly calling or asserting on private/protected methods | `obj._private_method()`, `obj.__internal` |
| **Internal state inspection** | Asserting on data structures that are not part of the public API | `assert service._cache == {"key": "value"}` |
| **Call order verification** | Asserting that internal methods were called in a specific order | `assert mock.call_args_list == [call(1), call(2)]` on internals |
| **Excessive mocking** | Mocking every collaborator so the test verifies only wiring, not behavior | 3+ mocks with no real collaborator in the test |
| **Spy-heavy tests** | Using spyOn on internal methods rather than checking outputs | `jest.spyOn(service, 'internalHelper')` |
| **Constructor/init verification** | Testing that internal objects are constructed with specific arguments | `assert MockDep.called_with(config_a, config_b)` |

### When Implementation-Detail Testing Is Acceptable

Some situations require testing implementation details. These are exceptions, not the norm, and should include an explicit justification comment in the test.

| Scenario | Why It Is Acceptable | Example |
|----------|---------------------|---------|
| **Security-critical algorithm** | Verifying the correct algorithm prevents security vulnerabilities | Asserting bcrypt hash prefix `$2b$` to confirm bcrypt usage |
| **External service integration** | The external call IS the behavior; verifying the correct API is called matters | Asserting an HTTP request was made to the correct endpoint with correct payload |
| **Middleware/plugin chains** | Framework conventions require verifying registration order | Asserting middleware was registered in the expected order |
| **Side effect verification** | The side effect IS the expected behavior (email sent, log written) | Asserting `send_email` was called with correct recipient and template |
| **Protocol compliance** | Verifying adherence to a specific protocol or specification | Asserting TLS version, HTTP method, header format |
| **Performance-critical caching** | Verifying cache hits vs misses is the behavior under test | Asserting the database was called once despite multiple lookups |

**Rule**: When flagging an implementation-detail test, check if any of the acceptable scenarios apply. If the test includes a justification comment (e.g., `# Security requirement: must use bcrypt`), accept the test with a note rather than penalizing it.

---

## Low-Score Improvement Suggestions

When a test suite scores below the threshold, the test-reviewer agent should provide concrete, actionable improvement suggestions organized by dimension.

### Meaningful Assertions (score below 70)

**Suggestions:**
- Replace mock call-count assertions with output/state assertions
- Remove mocks on internal collaborators; mock only at system boundaries (external APIs, databases, file system)
- Add explicit assertions to assertion-free tests — ask "what behavior am I verifying?"
- Replace logic-duplicated expected values with known constants

**Template suggestion:**
```
Instead of:
  mock_calculator.assert_called_once_with(100)
Try:
  assert order.total() == 110.0  # Verify the result, not the internal call
```

### Edge Case Coverage (score below 70)

**Suggestions:**
- Add boundary tests: empty input, null/None, zero, negative, maximum values
- Add error path tests: invalid input, missing data, service failures
- Use parametrize/test.each to cover multiple boundary values efficiently
- Consider: "What happens if this input is empty? Null? Very large? Negative?"

**Template suggestion:**
```
Add these test cases for `validate_email()`:
  - Empty string: ""
  - None value: None
  - Maximum length: "a" * 255 + "@example.com"
  - Missing @: "userexample.com"
  - Unicode: "user@exämple.com"
```

### Test Independence (score below 70)

**Suggestions:**
- Extract shared setup into fixtures (`@pytest.fixture`) or `beforeEach` blocks
- Replace shared mutable variables with fresh instances per test
- Add mock cleanup: `vi.restoreAllMocks()`, `jest.restoreAllMocks()`, or use `mocker` (auto-cleanup in pytest)
- Ensure environment variable changes are reverted in teardown

**Template suggestion:**
```
Instead of:
  global shared_user
  shared_user = create_user()  # In test_setup
  ...
  shared_user.update(...)      # In test_update (depends on test_setup)
Try:
  @pytest.fixture
  def user():
      return create_user()     # Fresh instance per test
```

### Readability (score below 70)

**Suggestions:**
- Rename tests to describe the scenario: `test_expired_token_returns_401` instead of `test_case_3`
- Add AAA section comments (`# Arrange`, `# Act`, `# Assert`) to tests longer than 10 lines
- Extract repeated setup into named fixtures or helper functions
- Replace magic values with named constants or descriptive variables

**Template suggestion:**
```
Instead of:
  def test1():
      r = fn(42, "abc", True)
      assert r == 7
Try:
  def test_calculates_score_for_premium_user():
      score = calculate_score(user_id=42, tier="abc", is_active=True)
      assert score == 7
```

---

## Review Output Format

The test-reviewer agent should produce a structured review in the following format:

```
TEST REVIEW: {test_file_path}

SCORES:
  Meaningful Assertions: {score}/100 (weight: 35%)
  Edge Case Coverage:    {score}/100 (weight: 25%)
  Test Independence:     {score}/100 (weight: 20%)
  Readability:           {score}/100 (weight: 20%)
  Overall:               {weighted_score}/100

RESULT: {PASS|NEEDS IMPROVEMENT}  (threshold: {threshold})

{If PASS:}
STRENGTHS:
  - {Notable positive patterns}

{If NEEDS IMPROVEMENT:}
IMPROVEMENTS:
  {dimension_name} ({score}/100):
    - {Specific suggestion with before/after example}
    - {Specific suggestion with before/after example}
```
