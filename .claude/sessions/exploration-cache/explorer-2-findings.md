## Explorer 2: Task Manager Application

### Key Findings

**Real-Time Data Flow:**
- File system → Chokidar (polling 300ms) → SSE → TanStack Query invalidation → React
- HMR-safe singleton pattern using globalThis to persist FileWatcher across hot reloads
- Server Component + Client Component hydration with SSE-driven cache invalidation

**Architecture:**
- 14 high/medium relevance files across lib/, components/, hooks/, api/
- Server Components for initial data fetch, Client Components with real-time hooks
- 3-column Kanban board (pending/in_progress/completed) with search filtering

**API Surface (5 routes):**
- GET /api/health — Health check
- GET /api/task-lists — List available task lists
- GET /api/tasks/:listId — Get tasks for a list
- GET /api/events?taskListId=<id> — SSE stream for real-time updates
- GET /api/execution-context/:listId — Execution context data

**7 Major Code Patterns:**
1. Global singleton (globalThis for FileWatcher)
2. SSE streaming (ReadableStream)
3. Query invalidation (TanStack Query + SSE events)
4. Path traversal protection (security validation)
5. Server/Client component boundary
6. Execution context monitoring with tabbed artifact viewer
7. shadcn/ui (new-york variant) + Tailwind v4 + next-themes dark mode

### Challenges Identified
1. Polling overhead (300ms interval) — could use platform detection for native fsevents
2. No pagination — loads all tasks, recommend virtual scrolling for >100 tasks
3. Execution context uses polling (5s) — could extend SSE for lower latency
4. Markdown rendering needs sanitization (potential XSS from artifacts)
