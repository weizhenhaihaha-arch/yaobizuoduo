# Review Transition

Review the completed implementation for the current task.

1. Read `.ag_loop_state.json` to identify the dispatch baseline and audit the complete diff from that baseline through `HEAD`.
2. Inspect the implementation, task report evidence in Git/memory, scope boundaries, and user-facing behavior.
3. Run the narrowest relevant checks, then the required broader tests, fixture validation, build/type checks, `git diff --check`, scope scan, and secret scan.
4. Use adversarial probes for fail-closed, stale, empty, error, or malformed states when relevant.

If review fails:

- Keep the same task ID.
- Set `CURRENT_TASK.md` status to `repair_requested` and record precise blocking defects and acceptance checks.
- Update `PROJECT_MEMORY.md` with durable review facts.
- Commit only the review/task/memory transition.
- Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/set_ag_task_baseline.ps1 -TaskId <same-task-id>`.
- Stop. Do not implement the repair during this invocation.

If review passes:

- Record the pass in `PROJECT_MEMORY.md`.
- Select only the next smallest task explicitly supported by `DEVELOPMENT_WORKFLOW.md`, product/design contracts, and unfinished current-milestone work.
- Replace `CURRENT_TASK.md` with that bounded task and status `dispatched`. If no safe next task is derivable, set the reviewed task to `blocked` with the exact decision needed instead of inventing scope.
- Commit only the approval and next-task dispatch transition.
- If a next task was dispatched, run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/set_ag_task_baseline.ps1 -TaskId <new-task-id>`.
- Stop. Do not implement the newly dispatched task during this invocation.

Your final message must report review result, tests, commit, resulting task/status, workspace state, and memory synchronization.
