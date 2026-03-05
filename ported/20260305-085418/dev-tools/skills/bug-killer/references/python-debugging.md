# Python Debugging Reference

Language-specific debugging techniques, common pitfalls, and diagnostic tools for Python codebases.

---

## pytest Debugging Flags

| Flag | Purpose | When to Use |
|------|---------|-------------|
| `-x` | Stop on first failure | Isolating the first broken test |
| `--tb=long` | Full traceback | Need complete call stack |
| `--tb=short` | Abbreviated traceback | Quick scan of failures |
| `--pdb` | Drop into debugger on failure | Interactive investigation |
| `--lf` | Re-run only last failed tests | Iterating on a fix |
| `-s` | Disable output capture | See print/logging output |
| `-k "pattern"` | Run tests matching pattern | Focus on specific tests |
| `-v` | Verbose output | See individual test names |
| `--no-header` | Suppress header | Cleaner output for parsing |
| `--tb=no` | No traceback | Quick pass/fail check |

### Combining Flags

```bash
# Reproduce and investigate: stop at first failure, full trace, show output
pytest -x --tb=long -s path/to/test_file.py

# Re-run failures with debugger
pytest --lf --pdb

# Run specific test with verbose output
pytest -xvs -k "test_specific_function" path/to/test_file.py
```

---

## Traceback Analysis

### Reading Python Tracebacks

Python tracebacks read **bottom-to-top** — the actual error is at the bottom, the call chain above.

```
Traceback (most recent call last):          ← oldest frame
  File "app/main.py", line 42, in handle    ← your code (relevant)
    result = service.process(data)
  File "app/service.py", line 18, in process  ← your code (relevant)
    return transformer.apply(data)
  File "venv/lib/.../transformer.py", line 7  ← library code (context)
    raise ValueError("invalid input")
ValueError: invalid input                    ← actual error (start here)
```

### Frame Identification

| Frame Pattern | Type | Action |
|---------------|------|--------|
| Your project paths (`app/`, `src/`, `lib/`) | Your code | Primary investigation target |
| `venv/`, `site-packages/` | Library code | Check what you passed in |
| `<frozen importlib>`, `<string>` | Python internals | Usually skip |

### Key Questions at Each Frame

1. What arguments were passed to this function?
2. What state was the object in at this point?
3. Is the data type what the function expects?

---

## Common Exception Types

| Exception | Typical Cause | Investigation Strategy |
|-----------|---------------|------------------------|
| `AttributeError` | Wrong type, None where object expected, typo | Check the object's actual type with `type()`, trace where it was assigned |
| `KeyError` | Missing dict key, wrong key name | Print available keys, check data source |
| `TypeError` | Wrong argument types, wrong number of args | Compare function signature with call site |
| `ImportError` / `ModuleNotFoundError` | Missing package, circular import, wrong path | Check `sys.path`, verify package installed, check for circular deps |
| `ValueError` | Correct type but invalid value | Check input data, trace where value originates |
| `IndexError` | List/tuple index out of range | Check collection length, off-by-one |
| `FileNotFoundError` | Wrong path, missing file | Print `os.getcwd()`, check relative vs absolute |
| `PermissionError` | File/directory permissions | Check file ownership and mode |
| `RecursionError` | Infinite recursion | Check base case, print recursion depth |
| `StopIteration` | Exhausted iterator, bare `next()` | Use `next(iter, default)` or check before consuming |
| `UnicodeDecodeError` | Wrong encoding assumption | Check file encoding, use `errors='replace'` to diagnose |

---

## Python Gotchas

### Mutable Default Arguments

```python
# BUG: shared list across all calls
def append_to(item, target=[]):
    target.append(item)
    return target

# FIX: use None sentinel
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

### Late Binding Closures

```python
# BUG: all functions return 4 (last value of i)
functions = [lambda: i for i in range(5)]

# FIX: capture with default argument
functions = [lambda i=i: i for i in range(5)]
```

### Circular Imports

Symptoms: `ImportError`, `AttributeError` on module attribute, partially initialized module.

Investigation:
1. Check import order — which module loads first?
2. Move imports inside functions (lazy import) as a quick fix
3. Restructure to break the cycle for a proper fix

### None Comparisons

```python
# BUG: can fail with objects that override __eq__
if value == None:

# FIX: use identity check
if value is None:
```

### Integer Division

```python
# Python 3: this is float division
result = 7 / 2   # 3.5

# Integer division requires //
result = 7 // 2  # 3
```

### String Immutability and Identity

```python
# BUG: 'is' checks identity, not equality
if name is "admin":  # unreliable

# FIX: use == for value comparison
if name == "admin":
```

---

## Diagnostic Logging

### Targeted Debug Logging

```python
import logging

logger = logging.getLogger(__name__)

# Temporary diagnostic (remove after fixing)
logger.debug("process_order called: order_id=%s, items=%d, total=%s",
             order.id, len(order.items), order.total)
```

### Quick Diagnostic Print

For rapid investigation (remove before committing):

```python
# Print with context
print(f"DEBUG [{__name__}:{line}] variable={variable!r} type={type(variable)}")

# Print collection contents
print(f"DEBUG keys={list(data.keys())}")
print(f"DEBUG len={len(items)}, first={items[0] if items else 'EMPTY'}")
```

### Logging Configuration for Debugging

```python
# Enable debug logging for specific module
logging.getLogger("app.service").setLevel(logging.DEBUG)

# See all SQL queries (SQLAlchemy)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

---

## Performance Investigation

### cProfile Quick Start

```bash
# Profile a script
python -m cProfile -s cumulative script.py

# Profile a specific function in tests
python -m cProfile -s tottime -m pytest -x test_slow.py
```

### Targeted Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # top 20 functions
```

---

## Git Bisect with pytest

```bash
# Start bisect
git bisect start

# Mark current (broken) as bad
git bisect bad

# Mark known good commit
git bisect good <commit-hash>

# Automate with pytest
git bisect run pytest -x path/to/failing_test.py

# When done
git bisect reset
```

---

## Environment Investigation

```bash
# Check Python version
python --version

# Check installed package version
pip show <package-name>

# List all installed packages
pip list

# Check for conflicting dependencies
pip check

# Verify virtual environment is active
which python
echo $VIRTUAL_ENV
```
