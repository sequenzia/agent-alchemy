# Agent Alchemy CS Tools

Competitive programming and LeetCode problem-solving with educational explanations. Classifies problems, loads domain-specific algorithmic references, and produces structured solutions with complexity analysis, walkthroughs, and verification.

## Skills

| Skill | Invocable | Description |
|-------|-----------|-------------|
| `/solve` | Yes | Problem-solving workflow — classifies the problem, loads relevant reference patterns, spawns problem-solver agent (Opus) to produce a complete solution with educational walkthrough |
| `/verify` | Yes | Solution verification — performs static analysis, generates test cases (basic, edge, stress), runs them, and reports correctness verdict with bug analysis |
| `dp-patterns` | No | Dynamic programming patterns: Fibonacci, 0/1 Knapsack, LCS, LIS, Grid DP, Kadane's, Coin Change, Bitmask DP |
| `graph-algorithms` | No | Graph algorithm patterns: BFS, DFS, Dijkstra, Topological Sort, Union-Find, MST, Bellman-Ford, Bipartite |
| `search-and-optimization` | No | Search and optimization patterns: Binary search, binary search on answer, two pointers, sliding window, greedy, prefix sums, merge intervals, monotonic stack |
| `data-structures` | No | Advanced data structure patterns: Heap/PQ, monotonic stack/queue, trie, segment tree, Fenwick tree, stack-based parsing, ordered set |
| `math-and-combinatorics` | No | Math and combinatorics patterns: Modular arithmetic, Sieve, GCD/LCM, binomial coefficients, fast exponentiation, counting, inclusion-exclusion, game theory |
| `string-algorithms` | No | String algorithm patterns: KMP, Z-function, Rabin-Karp, Manacher's, string hashing, suffix array, Aho-Corasick |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `problem-solver` | Opus | Solves problems with structured educational output — verifies against examples before returning |
| `solution-verifier` | Opus | Tests solutions through static analysis, generated test cases, and Python execution |

## How It Works

### `/solve` Workflow

```
Problem Statement → Classify (category, sub-pattern, difficulty, constraints)
                  → Load reference skill(s) for the identified category
                  → Spawn problem-solver with classification + references
                  → Structured solution output
```

1. User pastes a problem statement (or describes the problem)
2. The skill classifies it: category, technique, difficulty, constraint-to-complexity mapping
3. Loads 1-2 relevant reference skills (e.g., `dp-patterns` for a knapsack problem)
4. Spawns the `problem-solver` agent with the problem + classification + reference material
5. Agent produces: key insight, approach, Python code, complexity analysis, walkthrough, edge cases, common mistakes

### `/verify` Workflow

```
Problem + Solution → Spawn solution-verifier
                   → Static analysis + test generation + execution
                   → Verdict with bug analysis
```

1. User provides a problem statement and their solution code
2. The skill spawns the `solution-verifier` agent
3. Agent performs static analysis, generates test cases (basic, edge, stress), writes and executes a test harness
4. Reports: verdict (CORRECT/INCORRECT/PARTIALLY CORRECT/TLE RISK), test results, bug analysis, improvement suggestions

## Supported Problem Categories

| Category | Reference Skill | Example Techniques |
|----------|----------------|-------------------|
| Dynamic Programming | `dp-patterns` | 0/1 Knapsack, LIS, Grid DP, Bitmask DP |
| Graph Algorithms | `graph-algorithms` | BFS, DFS, Dijkstra, Topological Sort, MST |
| Search & Optimization | `search-and-optimization` | Binary Search, Two Pointers, Sliding Window, Greedy |
| Data Structures | `data-structures` | Segment Tree, Trie, Heap, Monotonic Stack |
| Math & Combinatorics | `math-and-combinatorics` | Modular Arithmetic, Sieve, Game Theory |
| String Algorithms | `string-algorithms` | KMP, Z-function, Suffix Array, Aho-Corasick |

## Directory Structure

```
cs-tools/
├── agents/
│   ├── problem-solver.md
│   └── solution-verifier.md
├── skills/
│   ├── solve/
│   │   └── SKILL.md
│   ├── verify/
│   │   └── SKILL.md
│   ├── dp-patterns/
│   │   └── SKILL.md
│   ├── graph-algorithms/
│   │   └── SKILL.md
│   ├── search-and-optimization/
│   │   └── SKILL.md
│   ├── data-structures/
│   │   └── SKILL.md
│   ├── math-and-combinatorics/
│   │   └── SKILL.md
│   └── string-algorithms/
│       └── SKILL.md
└── README.md
```
