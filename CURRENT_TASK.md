# Current AG Task

## Task identity

- Task ID: `G0-T03`
- Gate: G0 main required check and minimal branch protection
- Risk: `D2`
- Status: `awaiting_review`
- Candidate generation: `3`
- Executor: one bounded developer AG
- Reviewer: main Codex plus independent code/security and architecture lanes
- Authorization: product owner explicitly authorized public-repository recovery on 2026-07-22 Asia/Shanghai
- Baseline: `09bfbd23d898198fe694a3a94f77663759dd89d8`
- Prior terminal blocked record: `3046d8bb023e169d3b64bfbe7093eee3ec52f722`

## Goal

Establish one recoverable repository ruleset for canonical `main` that requires
pull requests, requires the exact established `G0 / exact-head` context, and
forbids force pushes and branch deletion. Preserve unknown settings and prove
the exact before, after, readback, and rollback identities.

## Required deliverables

1. Create generation 2 through an exact two-parent authorization record whose
   first parent is authoritative closed main and second parent is generation 1's
   immutable blocked record; then use ordinary `authorized -> in_progress`.
2. Record read-only rulesets and classic protection before snapshots, normalized
   SHA-256, and a precise rollback procedure without credentials.
3. Create only one active repository ruleset targeting `refs/heads/main`, with
   no bypass actors, requiring pull requests without changing approval count,
   requiring only `G0 / exact-head`, and blocking deletion/non-fast-forward.
4. Read the new rule back by ID and compare name, target, enforcement,
   conditions, rules, and digest exactly.
5. Add focused governance and behavior tests for exact context, strict-success,
   secret-free fork operation, preservation, evidence integrity, readback,
   rollback, and forged evidence.
6. Push one bounded branch, create a PR, wait for exact-head CI, and deliver only
   `awaiting_review` without self-approval or merge.

## Allowed scope

- Read-only GitHub repository/rules/protection discovery.
- One minimum recoverable GitHub repository ruleset for canonical `main`.
- Focused G0-T03 evidence, validator, fixtures, and tests.
- `PROJECT_STATUS.yaml`, `CURRENT_TASK.md`, and `PROJECT_MEMORY.md`.

## Forbidden scope

- No automatic merge, unknown-rule replacement/deletion, bypass actors, or
  member permission, secret, environment, default-branch, unrelated-rule, or
  approval-count changes.
- No G0-T04/G1+, market collection, private APIs, credentials, orders, leverage,
  shorting, trading, deployment, release, profit, accuracy, or `LOCAL-PREVIEW`.

## Acceptance and stop conditions

- Before/readback snapshots and digests must be complete and repository-bound.
- Rule target and semantics must exactly match the frozen minimum; missing,
  failed, cancelled, skipped, neutral, stale, or mismatched checks fail closed.
- Rollback must delete only the newly created rule ID and verify the exact before
  state. Any permission, semantic, identity, preservation, or recovery ambiguity
  stops the card as `BLOCKED` without guessing.
- Candidate requires exact PR-head CI, main review, code/security `APPROVE`, and
  architecture/route `CLEAR`; developer never merges or starts another card.

## Required delivery report

Report both authorization parents, task ID/generation, exact branch/HEAD,
before/after digests, rule ID/name/target/readback, rollback procedure, files,
commands/results, PR/run, tests, blockers, worktree state, and memory update.

## Generation 2 review result: returned

- Reviewed exact PR head: `090db8c80f9f792d86e9550e2eeb5ad1b1de91df`.
- Exact successful run: `29892661541`.
- Architecture/route: `CLEAR`; remote ruleset `19526291` is correct and immutable
  for this repair.
- Code/security: `REQUEST CHANGES`. The local evidence validator trusts
  recomputed digests for attacker-controlled snapshots, permits incomplete or
  unknown structures, and can accept simultaneous desired/readback drift.
- Repair is limited to strict local evidence schema, semantics, rollback binding,
  and adversarial tests. No remote ruleset mutation is allowed.

## Generation 3 repair scope

- `returned -> in_progress` atomically cleared generation 2 implementation,
  candidate, CI and reviewer identities.
- Freeze every evidence object and nested parameter to an exact field set and
  value; a recomputed digest never substitutes for semantic truth.
- Reject incomplete values, unknown fields/parameters, simultaneous desired and
  readback drift, non-positive IDs, and any rollback method/repository/ID/result
  mismatch.
- Remote ruleset `19526291` must remain byte-semantically unchanged.
