# General Debugging Reference

Language-agnostic debugging strategies, systematic investigation methods, and common bug categories.

---

## Systematic Debugging Methods

### Binary Search for Bugs

Narrow the problem space by half at each step:

1. Identify the full code path from input to incorrect output
2. Place a diagnostic check at the midpoint
3. Determine which half contains the bug
4. Repeat in the failing half until the exact location is found

Works for: data transformation pipelines, middleware chains, multi-step processes.

### Git Bisect

Automate binary search through commit history:

```bash
git bisect start
git bisect bad                    # current commit is broken
git bisect good <known-good-sha> # this commit was working

# Automated: let a test command drive the search
git bisect run <test-command>     # returns 0 = good, non-0 = bad

git bisect reset                  # when done
```

Best for: regressions where you know "it used to work."

### Delta Debugging

Minimize the input that triggers the bug:

1. Start with the full failing input
2. Remove half the input — does it still fail?
3. If yes, keep the smaller input and repeat
4. If no, restore and try removing the other half
5. Continue until you find the minimal failing case

Works for: large inputs, complex configurations, test case reduction.

### Rubber Duck Debugging

Explain the problem out loud (or in writing), step by step:

1. State what the code is supposed to do
2. Walk through the actual execution, line by line
3. At each step, explain what the state should be vs. what it is
4. The discrepancy often reveals itself during the explanation

### 5 Whys

Drill past symptoms to root causes:

```
Bug: Users see a 500 error on checkout
Why? → The payment API call throws a timeout
Why? → The request takes >30 seconds
Why? → The order total calculation is O(n²)
Why? → It recalculates item prices for each item pair
Why? → The discount logic compares every item against every other item
Root cause: Quadratic discount calculation algorithm
```

Stop when the answer is something you can directly fix.

---

## Reading Stack Traces

### Universal Patterns

| Element | What It Tells You |
|---------|-------------------|
| Error type/name | Category of failure (null access, type mismatch, etc.) |
| Error message | Specific details about what went wrong |
| File path + line number | Where the error was thrown |
| Function/method name | What was executing when it failed |
| Frame ordering | The call chain that led to the error |

### What Stack Traces CAN'T Tell You

- **Why** the wrong value got there (you need to trace backwards)
- **When** the state became corrupted (may have happened much earlier)
- **Where** in async code the real problem is (async gaps in traces)
- **Whether** a caught-and-rethrown error lost its original context

### Investigation Strategy

1. Read the **error message** first — it often contains the key clue
2. Find **your code** in the trace (skip framework/library frames)
3. Read the **immediate caller** — what arguments were passed?
4. Check the **state** at that point — are variables what you expect?
5. Trace **backwards** from the error to where the data originated

---

## Bug Categories

### Off-by-One Errors

**Symptoms:** Missing first/last element, array index out of bounds, fencepost errors.

**Check for:**
- `<` vs `<=` in loop conditions
- 0-based vs 1-based indexing confusion
- Inclusive vs exclusive range boundaries
- Empty collection edge case (length 0)

### Null/Undefined/None Errors

**Symptoms:** Null reference exceptions, "undefined is not a function," AttributeError.

**Check for:**
- Uninitialized variables
- Missing return values (functions that implicitly return null/undefined)
- Optional fields accessed without guards
- API responses with unexpected null fields
- Database queries returning no results

### Race Conditions

**Symptoms:** Intermittent failures, works in debugger but fails normally, order-dependent results.

**Check for:**
- Shared mutable state accessed concurrently
- Missing locks/synchronization
- Read-then-write without atomicity
- Callback ordering assumptions
- File system operations assuming sequential access

### Resource Leaks

**Symptoms:** Slow degradation, eventual crashes, "too many open files," memory growth.

**Check for:**
- File handles not closed (missing `close()` / `with` / `using`)
- Database connections not returned to pool
- Event listeners added but never removed
- Timers/intervals not cleared
- Temporary files not cleaned up

### State Corruption

**Symptoms:** Inconsistent data, works sometimes but not always, cascade of errors after a specific action.

**Check for:**
- Mutation of shared objects
- Missing deep copies (aliased references)
- Partial updates (crash between related writes)
- Cache invalidation issues
- Global/singleton state modified by multiple code paths

---

## Diagnostic Logging Strategy

### Targeted Logging

Log at decision points and data boundaries:

```
[ENTRY] function_name called with: key_arg=value
[BRANCH] taking path X because condition=value
[DATA] received from external: summary_of_data
[EXIT] function_name returning: summary_of_result
```

### Logging Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| Logging everything | Noise hides signal | Log at boundaries and decision points |
| Logging sensitive data | Security risk | Redact or hash sensitive fields |
| Logging inside tight loops | Performance impact, massive output | Log summary after loop, or sample every Nth iteration |
| Logging without context | "Error occurred" is useless | Include function name, key parameters, state |
| Leaving debug logs in code | Clutters production output | Use conditional debug level, remove before commit |

### Effective Diagnostic Pattern

1. **Before the suspected area:** Log inputs and state
2. **At decision points:** Log which branch was taken and why
3. **After the suspected area:** Log outputs and state
4. **Compare:** Are the inputs/outputs what you expect at each point?

---

## Investigation Checklist

Before proposing a fix, verify you can answer:

### Understanding the Bug
- [ ] Can you reproduce the bug reliably?
- [ ] What is the expected behavior vs actual behavior?
- [ ] When did this start happening? (regression or latent bug?)
- [ ] Does it happen always, sometimes, or in specific conditions?

### Root Cause Identification
- [ ] Have you identified the specific line(s) causing the issue?
- [ ] Do you understand WHY those lines produce the wrong result?
- [ ] Is this the root cause, or a symptom of a deeper issue?
- [ ] Could this same root cause affect other code paths?

### Fix Validation
- [ ] Does the fix address the root cause, not just the symptom?
- [ ] Could the fix introduce new bugs? (side effects, changed behavior)
- [ ] Are there existing tests that should have caught this?
- [ ] Does the fix handle all edge cases for this code path?

### Broader Impact
- [ ] Are there similar patterns elsewhere that might have the same bug?
- [ ] Does the fix require updates to documentation or configuration?
- [ ] Could this be a regression? If so, what change introduced it?
- [ ] Is a new test needed to prevent this from recurring?
