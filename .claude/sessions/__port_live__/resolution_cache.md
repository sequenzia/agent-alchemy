# Resolution Cache

## Cached Decisions

| Group Key | Decision Type | Workaround Applied | First Component | Apply Globally |
|-----------|-------------|-------------------|-----------------|---------------|
| unsupported_composition:reference_dir_null | workaround | Inline reference file content into the skill body | technical-diagrams | true |
| unmapped_tool:SendMessage | workaround | Replace with output-based communication — agent outputs findings in final response, task tool returns to parent | bug-investigator | true |
| unmapped_tool:TeamCreate | workaround | Replace with orchestrated sequential/parallel task tool calls with explicit context passing in prompts | N/A | true |
| unmapped_tool:TeamDelete | workaround | Remove — no cleanup needed when using task tool calls instead of teams | N/A | true |
| unmapped_tool:TaskCreate | workaround | Replace with todowrite tool (session-scoped scratchpad, limited functionality) | bug-investigator | true |
| unmapped_tool:TaskUpdate | workaround | Replace with todowrite tool (simple status changes only) | bug-investigator | true |
| unmapped_tool:TaskList | workaround | Replace with todoread tool (reads full list, no filtering) | bug-investigator | true |
| unmapped_tool:TaskGet | workaround | Replace with todoread tool (no per-task ID retrieval) | bug-investigator | true |
