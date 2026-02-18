# Resolution Cache

## Cached Decisions

| Group Key | Decision Type | Workaround Applied | First Component | Apply Globally |
|-----------|-------------|-------------------|-----------------|---------------|
| unmapped_tool:SendMessage | workaround+TODO | Replace with task-prompt context passing; TODO for inter-agent messaging | agent-core-tools-code-architect | true |
| unmapped_tool:TaskCreate | workaround | Use todowrite with metadata embedded in description text | skill-sdd-tools-create-tasks | true |
| unmapped_tool:TaskUpdate | workaround | Use todowrite rewrite with dependency info in description | skill-sdd-tools-create-tasks | true |
| unmapped_tool:TaskList | workaround | Use todoread full list scan for spec_path in description | skill-sdd-tools-create-tasks | true |
| unmapped_tool:TaskGet | workaround | Use todoread full list scan for task_uid in description | skill-sdd-tools-create-tasks | true |
| unsupported_composition:reference_dir_null | workaround | Inline reference content into skill body | skill-tdd-tools-analyze-coverage | true |
| general_gap:reference_dir | TODO | TODO comments for reference file inlining | skill-sdd-tools-create-tasks | true |
| general_gap:question_tool_subagent | workaround | Note about primary-agent-only constraint; pre-specify params for subagent contexts | skill-tdd-tools-analyze-coverage | true |
| general_gap:question_tool_subagent_restriction | workaround | Ensure invoked as primary agent; restructure for subagent if needed | agent-dev-tools-changelog-manager | true |
| general_gap:skill_unassignable | workaround | Skills available dynamically via skill tool at runtime; note in body comment | agent-core-tools-code-explorer | true |
| unsupported_hook:PreToolUse_shell_to_js | workaround | Port shell script logic to JS plugin using tool.execute.before event | hooks-sdd-tools-hooks | true |
| general_gap:hook_subagent_coverage | workaround | Document "Allow for session" manual approval; hooks don't fire for subagent tool calls | hooks-sdd-tools-hooks | true |
| unsupported_hook:PreToolUse_auto-approve | workaround | Manual "Allow for session" workflow; no path-based auto-approval in OpenCode | hooks-core-tools-hooks | true |
| unmapped_field:disable-model-invocation | workaround | Document user-only constraint in skill description; restrict at agent level | skill-dev-tools-release-python-package | true |
| unmapped_tool:TeamCreate | workaround+TODO | Restructure as parallel task calls; no team registry or membership | skill-core-tools-deep-analysis | true |
| unmapped_tool:TeamDelete | workaround | Remove; tasks are ephemeral, no cleanup needed | skill-core-tools-deep-analysis | true |
| general_gap:tdd_plugin_existence_check | workaround | Replace path-based README check with skill invocation probe or user-confirmed prerequisite | skill-sdd-tools-create-tdd-tasks | true |
| general_gap:bypassPermissions_mode | workaround | Permissions configured in agent frontmatter; ensure agents have appropriate permission settings | skill-sdd-tools-execute-tdd-tasks | true |
