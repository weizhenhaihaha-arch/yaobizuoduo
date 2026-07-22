# Current AG Task

## Task identity

- Task ID: `G0-T03`
- Gate: G0 main required check and minimal branch protection
- Risk: `D2`
- Status: `accepted_pending_merge`
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

## Generation 3 acceptance

- Accepted exact candidate: `6ca1ace6af66f874eed38f644104f59bbc4009ad`.
- Exact PR CI: run `29893836848`, event `pull_request`, subject SHA equal to the
  accepted candidate, stable check `G0 / exact-head`, terminal `success`.
- Main Codex independently reran canonical status validation, protection
  evidence validation, focused governance/protection tests, exact PR/run
  identity, and live ruleset readback.
- Independent code/security: `APPROVE`; all prior recomputed-digest P1 probes
  fail closed. Independent architecture/route: `CLEAR`.
- Remote ruleset `19526291` remained unchanged. This acceptance does not merge
  PR #6 and grants no G0-T04, G1, deployment, release, or trading authority.

## Generation 3 merge recovery

- GitHub merged PR #6 as exact main subject
  `08d6a3ea8d1898dbe47c7eaf9c82cb7adf1db68f`, with first parent closed main
  `09bfbd23d898198fe694a3a94f77663759dd89d8`, second parent accepted record
  `85509b6dc1b156d3347b6b21ff952d8e55ac18d3`, and tree equal to that record.
- Exact push run `29894526319` proved repository, event, ref and subject identity,
  but canonical validation failed on the historical G0-T02 recovery shape and
  merged-topology validation of the generation-2 blocked authorization.
- The authorized recovery recognizes only this exact merge, the exact accepted
  candidate/review/CI record, exact two-parent authorization `c1e3eba` and
  terminal blocked record `3046d8b`. Parent substitution, order exchange, tree
  drift, fake blocked descendants, other tasks/generations and failure-evidence
  changes fail closed.
- Ruleset `19526291` and its evidence remain immutable. Recovery does not merge
  its own PR, modify main, authorize G0-T04/G1, or expand product capability.

## Recovery-merge recovery

- Main and independent review accepted exact recovery candidate
  `a0885c16582e75613bb203be3a2ecefb01637d37` with exact PR run
  `29896682124`, code/security `APPROVE`, and architecture/route `CLEAR`.
- GitHub merged that accepted record `0b5279b69b70b70500f22753cb6ae3a542b196c7`
  as main subject `bea5cf840ddf45ec4425796861d8956f682ab564`.
  Its first parent is prior failed main `08d6a3e`, second parent is the accepted
  recovery record, and its tree/status equal the second parent.
- Exact push run `29898504840` failed because canonical validation did not yet
  recognize this recovery-merge bridge before generic merge and repeated-
  authorization paths. Both failed main runs remain recorded truthfully.
- This repair is restricted to the exact `bea5cf8` topology and unchanged
  ruleset evidence. It grants no merge, G0-T04/G1, live-data, deployment,
  release, or trading authority.

## Recovery-merge recovery review return and bounded closure repair

- PR #8 candidate `05597ef837031bb6a4aeb6eefb21aa4cecd7ff30` passed exact
  pull-request run `29900351726`, but independent code/security returned
  `REQUEST CHANGES` and architecture/route returned `BLOCK`: a future merge of
  first parent `bea5cf8` and the accepted repair record would still fall through
  the generic merge path and fail canonical validation.
- The current repair remains on the same branch and PR. It must preserve both
  exact failed-main blockers until authoritative-main CI succeeds and may not
  modify ruleset `19526291`, old blocked/recovery refs, main, or any later card.
- A future recovery closure is accepted only when first parent is exact
  `bea5cf840ddf45ec4425796861d8956f682ab564`, second parent directly accepts a
  new single-parent repair candidate, merge tree/status equal that acceptance
  record, and a later non-self-referential receipt binds exact PR CI,
  code/security `APPROVE`, architecture `CLEAR`, the prior rejected candidate
  and unchanged ruleset evidence digest.
- Parent, order, tree, candidate, run, review, ruleset, digest, blocker, task or
  generation substitution must fail closed. The accepted topology must also
  support the ordinary post-merge sequence: strict main success, blocker clear,
  `merged_verified`, finalization D0, and `closed`, without a third recovery PR.
