# Project development rules

1. Read `PROJECT_MEMORY.md` before planning or editing.
2. Keep this project separate from the `yaobi-radar` short-reversal project.
3. Do not add real-order execution or exchange credential storage without a separate approved design and explicit user approval.
4. Update `PROJECT_MEMORY.md` before finishing each development task.
5. Never store API keys, tokens, cookies, private keys, or other secrets in the repository.
6. Treat `PROJECT_STATUS.yaml` as the only mutable current machine-state source;
   task cards and memory may describe scope and history but must not compete with it.
7. Keep exactly one active task and follow the validated G0-G9 closure loop in
   `DEVELOPMENT_WORKFLOW.md` and `AG_WORK_LOOP.md`.
