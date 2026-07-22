# Current AG Task

## Task identity

- Task ID: `G0-T03`
- Gate: G0 main required check and minimal branch protection
- Risk: `D2`
- Status: `in_progress`
- Candidate generation: `1`
- Executor: one bounded developer AG
- Reviewer: main Codex plus independent code/security and architecture lanes
- Authorization: user explicitly authorized G0-T03 and the three-minute developer/review loop on 2026-07-22 Asia/Shanghai
- Baseline: `09bfbd23d898198fe694a3a94f77663759dd89d8`

## Goal

Establish the smallest recoverable protection increment for canonical `main`:
require pull requests, require the already-frozen `G0 / exact-head` context, and
forbid force pushes and branch deletion. Preserve unknown settings and fail
closed when the remote plan, permissions, or rule semantics cannot support an
exact readback and recovery procedure.

## Required deliverables

1. Read the current GitHub rulesets and classic branch protection before any
   mutation; record the repository, rule source and identifier, target, selected
   security-relevant fields, a normalized SHA-256 digest, and a precise recovery
   procedure without credentials.
2. Freeze a minimal delta for `main`: pull requests required; required check
   exactly `G0 / exact-head`; force pushes and branch deletion forbidden.
3. Preserve member permissions, secrets, environments, default branch, approval
   count, unknown fields, and unrelated rules. Never replace or delete an
   unknown rule wholesale.
4. Only after the snapshot and recovery plan are validated, apply the smallest
   supported incremental remote change, then read it back and compare every
   intended field.
5. Add focused fail-closed tests for exact check identity, strict-success
   semantics, secret-free fork operation, unknown-rule preservation, evidence
   digests, readback, recovery, and forged evidence.
6. Update canonical state, task card, and project memory without self-review.

## Allowed scope

- Read-only GitHub repository/rules/protection discovery.
- The minimum recoverable GitHub ruleset or classic branch-protection mutation.
- Focused G0-T03 evidence, validator, fixtures, and tests.
- `PROJECT_STATUS.yaml`, `CURRENT_TASK.md`, and `PROJECT_MEMORY.md`.
- Push the bounded task branch and open a PR after a valid delivery.

## Forbidden scope

- No automatic merge or unknown-rule replacement/deletion.
- No member permission, secret, environment, default-branch, unrelated-rule, or
  approval-count changes.
- No G1/G2+, live/public exchange collection, private APIs, credentials, orders,
  leverage, shorting, trading, deployment, release, profit, or accuracy claims.
- No `LOCAL-PREVIEW` changes.

## Acceptance checks

- Exact before/readback snapshots and digests are repository-bound and complete.
- The remote rule applies to canonical `main`, requires PRs and only the exact
  `G0 / exact-head` check, and forbids force push and branch deletion.
- Missing, failure, cancelled, skipped, neutral, stale, or mismatched checks do
  not satisfy the gate; a strict-success exact check can satisfy it.
- Fork PR operation requires no secrets.
- Recovery is explicit, bounded, and verified without losing unknown settings.
- Canonical validator and focused/full regression suites pass.
- Exact candidate PR CI succeeds; main and both independent review lanes approve.

## Stop conditions

- Stop `BLOCKED` if the private-repository plan or current permissions do not
  expose and support the required protection APIs.
- Stop if current settings cannot be fully read, the target rule is ambiguous,
  the minimum change could lock out recovery, or unknown settings could be lost.
- Stop on any evidence mismatch or inability to restore the exact prior state.
- Do not start another task from a blocked record.

## Required delivery report

Report task ID, exact branch/HEAD, remote preflight and readback identities,
before/after digests, recovery procedure, files, commands/results, PR/run, tests,
blockers, worktree state, and memory update. A blocked report must identify the
exact remote response and confirm that no remote protection mutation occurred.
