# TypeScript/JavaScript Debugging Reference

Language-specific debugging techniques, common pitfalls, and diagnostic tools for TypeScript and JavaScript codebases.

---

## Test Runner Debugging Flags

### Jest

| Flag | Purpose | When to Use |
|------|---------|-------------|
| `--verbose` | Show individual test results | See which specific tests pass/fail |
| `--bail` | Stop on first failure | Isolating the first broken test |
| `--detectOpenHandles` | Detect open async handles | Tests hang or don't exit |
| `--runInBand` | Run serially (no workers) | Debugging race conditions between tests |
| `--testPathPattern="pattern"` | Run matching test files | Focus on specific test file |
| `-t "pattern"` | Run matching test names | Focus on specific test case |
| `--no-cache` | Disable transform cache | Stale cache causing issues |
| `--forceExit` | Force exit after tests | Tests hang due to open handles |
| `--testTimeout=10000` | Set timeout (ms) | Async tests timing out |

### Vitest

| Flag | Purpose | When to Use |
|------|---------|-------------|
| `--reporter=verbose` | Detailed output | See individual test results |
| `--bail 1` | Stop on first failure | Isolating failures |
| `--run` | Run once (no watch) | CI or single-run debugging |
| `--testNamePattern="pattern"` | Run matching tests | Focus on specific test |
| `--no-threads` | Disable worker threads | Debugging thread-related issues |
| `--inspect` | Enable Node inspector | Interactive debugging |

### Combining Flags

```bash
# Reproduce and investigate: stop at first failure, verbose, serial
npx jest --bail --verbose --runInBand path/to/test.spec.ts

# Re-run with open handle detection
npx jest --bail --detectOpenHandles --forceExit

# Vitest single test with inspection
npx vitest run --bail 1 --reporter=verbose path/to/test.spec.ts
```

---

## Async/Await Pitfalls

### Missing await

```typescript
// BUG: test passes even when assertion should fail — promise not awaited
it('fetches data', () => {
  const result = fetchData();  // missing await
  expect(result).toBeDefined(); // tests the Promise object, not the result
});

// FIX: await the async operation
it('fetches data', async () => {
  const result = await fetchData();
  expect(result).toBeDefined();
});
```

### Unhandled Promise Rejections

```typescript
// BUG: error swallowed silently
async function process() {
  riskyOperation(); // missing await — rejection goes unhandled
}

// FIX: await and handle
async function process() {
  await riskyOperation(); // now rejection propagates properly
}
```

### Promise.all Error Handling

```typescript
// BUG: first rejection cancels everything, others may leak
try {
  await Promise.all([taskA(), taskB(), taskC()]);
} catch (e) {
  // only catches the first rejection
}

// FIX: use Promise.allSettled when you need all results
const results = await Promise.allSettled([taskA(), taskB(), taskC()]);
const failures = results.filter(r => r.status === 'rejected');
```

### Timer-Based Tests

```typescript
// BUG: real timers make tests slow and flaky
it('debounces input', async () => {
  await new Promise(r => setTimeout(r, 500)); // real delay
});

// FIX: use fake timers
it('debounces input', () => {
  jest.useFakeTimers();
  triggerInput();
  jest.advanceTimersByTime(500);
  expect(handler).toHaveBeenCalled();
  jest.useRealTimers();
});
```

---

## Common TypeScript/JavaScript Gotchas

### `this` Binding

```typescript
// BUG: 'this' is undefined in callback
class Handler {
  name = "handler";
  handle() {
    console.log(this.name); // undefined when called as callback
  }
}
const h = new Handler();
button.onClick(h.handle); // 'this' is lost

// FIX: arrow function or bind
class Handler {
  name = "handler";
  handle = () => {  // arrow preserves 'this'
    console.log(this.name);
  }
}
```

### Closure/Scope in Loops

```typescript
// BUG: all callbacks reference the same variable
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 100); // prints 5,5,5,5,5
}

// FIX: use let (block-scoped)
for (let i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 100); // prints 0,1,2,3,4
}
```

### Type Narrowing Gotchas

```typescript
// BUG: typeof null === 'object'
function process(value: string | object | null) {
  if (typeof value === 'object') {
    value.toString(); // crashes if null
  }
}

// FIX: check null explicitly first
function process(value: string | object | null) {
  if (value === null) return;
  if (typeof value === 'object') {
    value.toString(); // safe
  }
}
```

### Equality Comparisons

```typescript
// BUG: type coercion surprises
0 == ""     // true
0 == false  // true
"" == false // true
null == undefined // true

// FIX: always use strict equality
0 === ""     // false
0 === false  // false
```

### Array/Object Reference vs Value

```typescript
// BUG: arrays/objects compared by reference
[1, 2] === [1, 2]  // false
{ a: 1 } === { a: 1 }  // false

// FIX: deep comparison
JSON.stringify(a) === JSON.stringify(b)  // quick but order-sensitive
// or use lodash.isEqual, util.isDeepStrictEqual
```

### Optional Chaining and Nullish Coalescing

```typescript
// BUG: || treats 0 and "" as falsy
const port = config.port || 3000;  // 0 becomes 3000

// FIX: use ?? for null/undefined only
const port = config.port ?? 3000;  // 0 stays 0
```

---

## Stack Trace Analysis

### Node.js Stack Traces

```
Error: Connection refused
    at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141)  ← Node internal
    at Connection.connect (node_modules/pg/lib/connection.js:38)   ← library
    at Pool._connect (node_modules/pg/lib/pool.js:89)              ← library
    at db.query (src/database.ts:45)                                ← your code
    at UserService.findById (src/services/user.ts:22)              ← your code
    at GET /api/users/:id (src/routes/users.ts:15)                 ← entry point
```

Read top-to-bottom (opposite of Python). Your code is typically in the middle frames.

### Async Stack Traces

Node.js may lose async context in stack traces. Enable `--async-stack-traces` or use `--enable-source-maps` for TypeScript.

```bash
# Better async traces
node --async-stack-traces dist/app.js

# TypeScript source maps in traces
node --enable-source-maps dist/app.js
```

---

## Console Debugging Patterns

### Structured Output

```typescript
// Object inspection
console.dir(complexObject, { depth: null, colors: true });

// Table format for arrays of objects
console.table(users.map(u => ({ id: u.id, name: u.name, role: u.role })));

// Call stack at this point
console.trace("reached here");

// Group related logs
console.group("Processing order #123");
console.log("Items:", order.items.length);
console.log("Total:", order.total);
console.groupEnd();
```

### Conditional Debugging

```typescript
// Only log when condition is true
console.assert(items.length > 0, "Items array is empty!", { items });

// Count how many times a code path is hit
console.count("cache-miss");
console.count("cache-hit");
```

---

## Node.js Inspector

### Starting the Inspector

```bash
# Inspect a script
node --inspect-brk dist/app.js

# Inspect tests (Jest)
node --inspect-brk node_modules/.bin/jest --runInBand

# Inspect tests (Vitest)
npx vitest --inspect --no-threads
```

Open `chrome://inspect` in Chrome to connect to the debugger.

---

## Common Error Patterns

| Error | Typical Cause | Investigation Strategy |
|-------|---------------|------------------------|
| `TypeError: Cannot read properties of undefined` | Accessing property on undefined value | Trace back to where the variable was assigned, check for missing data |
| `TypeError: X is not a function` | Wrong type, missing import, wrong module export | Check imports, verify the export exists |
| `ReferenceError: X is not defined` | Typo, missing import, scope issue | Check spelling, verify import path |
| `SyntaxError: Unexpected token` | Malformed JSON, wrong file extension, missing transpilation | Check the file content at the indicated position |
| `ERR_MODULE_NOT_FOUND` | Wrong import path, missing package | Verify path, check `node_modules` |
| `ECONNREFUSED` | Service not running, wrong port | Check if the target service is up |
| `EADDRINUSE` | Port already in use | `lsof -i :PORT` to find the process |
| `MaxListenersExceededWarning` | Event listener leak | Track where listeners are added without removal |
| `JavaScript heap out of memory` | Memory leak, large data processing | Profile with `--max-old-space-size`, check for retained references |
| `ETIMEOUT` / `ESOCKETTIMEDOUT` | Network timeout, slow service | Check network, increase timeout, add retry |

---

## TypeScript-Specific Investigation

```bash
# Check what TypeScript compiles to
npx tsc --noEmit --pretty  # type check without emitting

# See generated JavaScript for a file
npx tsc --outDir /tmp/debug --sourceMap path/to/file.ts

# Check TypeScript version
npx tsc --version

# Verify tsconfig resolution
npx tsc --showConfig
```
