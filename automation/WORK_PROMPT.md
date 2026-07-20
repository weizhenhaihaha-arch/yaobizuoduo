# Work Transition

Implement or repair only the task currently defined in `CURRENT_TASK.md`.

1. Respect every allowed/forbidden scope item and acceptance criterion.
2. Reuse approved contracts and architecture. Do not silently decide unresolved product or strategy questions.
3. Add focused tests where the repository already has tests, then run all checks required by the task.
4. Update `DESIGN.md` only for durable UI decisions and update `PROJECT_MEMORY.md` with durable facts and verification results.

On success:

- Set the current task status to `awaiting_review`.
- Commit the implementation, tests, task status, and memory as one atomic task commit.
- Do not run the baseline script; the dispatch baseline must remain unchanged for review detection.
- Stop and report files, decisions, commands/results, risks, branch, commit, workspace state, and memory sync.

On a genuine external blocker:

- Set status to `blocked`, record the exact blocker and attempted alternatives in `CURRENT_TASK.md` and `PROJECT_MEMORY.md`, commit that state, and stop.

Do not review your own implementation, dispatch a new task, or continue into another milestone during this invocation.
