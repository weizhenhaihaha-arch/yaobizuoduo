# Current AG Task

## Task identity

- Task ID: `G0-T03`
- Gate: G0 main required check and minimal branch protection
- Risk: `D2`
- Status: `closed`
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

## Recovery closure repair acceptance record

- Main review passed the exact future-closure focus and canonical/protection
  validators for candidate `d259f75cb13a56b7256779ad87115120c005ddec`.
- Exact pull-request run `29904268309` completed with `success` for stable check
  `G0 / exact-head`; independent code/security returned `APPROVE` and
  architecture/route returned `CLEAR` for that same candidate.
- The later acceptance receipt records those exact identities, the prior
  rejected `05597ef`/run `29900351726` negative result, ruleset `19526291`, and
  frozen evidence digest. The receipt did not exist in the reviewed candidate,
  so it cannot self-attest.
- `PROJECT_STATUS.yaml` remains byte-identical at `accepted_pending_merge` with
  both failed authoritative-main runs retained as blockers. This record proves
  only candidate acceptance; it does not claim merge or main CI success and
  grants no G0-T04/G1 or wider authority.

## Recovery closure merged verification

- User-authorized PR #8 merge is exact authoritative main
  `a98dada059c91dc70714119f333d0d03ab1cb9f1`, ordered parents
  `[bea5cf840ddf45ec4425796861d8956f682ab564,
  3263cf207cecac1e3fb019df2fbd6c2a6435d5bd]`, with tree equal to the
  accepted record.
- Exact push/main run `29906115287` completed successfully for subject
  `a98dada`, after acceptance-head run `29905690883` succeeded for record
  `3263cf2`. The receipt in that record preserves the separately reviewed
  repair candidate `d259f75`/run `29904268309` and both independent green
  conclusions.
- Only after the authoritative-main success were failed runs `29894526319` and
  `29898504840` cleared from current blockers. They remain immutable history in
  this task card, project memory, and Git history.
- Current phase is `merged_verified`. Finalization/D0 and `closed` are not yet
  established; the finalization branch/PR may proceed serially but must not be
  merged automatically or authorize G0-T04/G1.

## Finalization and candidate close record

- Merged-verification record `e4fd7ae620955867ac0c6914aff2c913420c3ba2`
  passed exact pull-request run `29906677035` on PR #9. That successful exact
  subject is now the finalization/D0 evidence.
- The later close record transitions only `merged_verified -> closed` and binds
  finalization commit/run without changing candidate, acceptance, merged-main,
  ruleset or capability evidence. Current blockers remain empty.
- `closed` here is the candidate close status on an open, unmerged finalization
  PR. The close-record HEAD still requires its own exact PR CI and user merge
  decision. G0-T04/G1 remain `not_authorized`.

## Final-close merge recovery

- User-authorized PR #9 merged as exact main subject
  `b1544c168cf3acf9e0ce0c1c7e3785041c02e87c`, with ordered parents
  `[a98dada059c91dc70714119f333d0d03ab1cb9f1,
  cf15b25533769c7f589dd5dad275627802d9ae7d]` and tree/status equal to the
  closed second parent.
- Exact push/main run `29909220290` proved repository, event and subject
  identity but failed canonical validation because the final-close bridge was
  not recognized before generic history and repeated-authorization paths.
- Recovery is restricted to this exact failed merge plus a status-identical
  single-parent repair lineage. A future two-parent recovery must use `b1544c1`
  first, directly accept the reviewed repair candidate second, preserve the
  acceptance tree/status, and include a later non-self-referential receipt
  binding the complete repair/closure/finalization/closed history, exact PR CI,
  dual-green review, ruleset `19526291`, and its frozen evidence digest.
- Parent/order/tree/status/task/generation/candidate/run/review/ruleset/blocked-
  history substitution and ordinary closed merges fail closed. Current status
  stays `closed`, this exact failed run remains the sole blocker, and G0-T04/G1,
  live data, deployment, release and trading remain unauthorized.

## Final-close receipt review return

- PR #10 exact candidate `8048455a8d0d827d7f99af67716d111336df7b07`
  passed exact pull-request run `29913039430`; architecture/route remained
  `CLEAR`, but code/security returned `REQUEST CHANGES`.
- The receipt previously defined its own candidate run ID and URL. Synchronously
  replacing both values and recomputing the payload digest could therefore make
  a nonexistent or unrelated run pass.
- This same-slice repair moves candidate/run identity outside the receipt into
  an immutable reviewed-run binding. The receipt must equal that complete
  binding; positive integers, URL self-consistency, and digest recomputation are
  no longer sufficient. The exact PR #10 pair is preserved as the first audited
  binding, while any later repair candidate must be sealed only after its real
  exact-head run is known and before a later acceptance record consumes it.
- Synchronized run/URL/digest replacement, nonexistent runs, unrelated runs,
  subject drift and missing bindings fail closed. Status remains `closed`, the
  exact failed main run remains the sole blocker, and all route limits remain.
