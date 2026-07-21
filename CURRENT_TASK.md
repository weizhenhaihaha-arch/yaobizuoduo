# Current AG Task

## Task identity

- Task ID: `G0-T01`
- Gate: G0 governance baseline
- Risk: `D0`
- Status: `in_progress`
- Executor: one bounded developer AG
- Reviewer: main Codex plus independent code/security and architecture lanes
- Authorization: user explicitly authorized G0 on 2026-07-21 Asia/Shanghai
- Baseline: `7aadae13efd45023d19bf8a280f7680667c930fa`

## Goal

Create the smallest canonical, machine-validatable governance source of truth
for this repository, migrate the approved beginner-first product and G0-G9
route into formal repository documents, and map legacy M0-M7 evidence without
upgrading its maturity.

This card establishes governance only. It does not establish bootstrap CI,
GitHub branch protection, integration, continuous Paper validation, or release
readiness.

## Required deliverables

1. Add root `PROJECT_STATUS.yaml` as the only mutable current-state source.
   It must identify G0, exactly one active task (`G0-T01`), D0 risk, the legal
   task state, evidence SHA fields, reviewer/CI state, capability maturity,
   blockers, and next authorization.
2. Add a versioned status schema and an offline validator with deterministic,
   fail-closed diagnostics. Avoid a new unpinned runtime dependency; a
   JSON-compatible YAML representation plus Python standard library is
   acceptable for this bootstrap card.
3. Validate at least: unknown states, illegal transitions, multiple active
   tasks, missing or malformed SHA fields when required, missing reviewer/CI
   evidence when required, conflicting current-state claims in governed
   documents, and invalid maturity upgrades.
4. Encode the legal lifecycle:
   `planned -> authorized -> in_progress -> awaiting_review -> returned | blocked | accepted_pending_merge -> merged_verified -> closed`.
   `closed` may only follow `merged_verified`; returned candidates invalidate
   prior CI and review identity.
5. Add a legacy M0-M7 evidence map. Historical accepted work may be represented
   only as `OFFLINE_EVIDENCE_ACCEPTED`; L0 remains the documented legacy-local
   exception and must not be rewritten as exact-HEAD remote CI evidence.
6. Replace stale M-era current-route claims in governance documents with the
   approved G0-G9 route and one-card closure loop. `PROJECT_MEMORY.md` remains
   historical facts; `CURRENT_TASK.md` remains the task card; neither may
   compete with `PROJECT_STATUS.yaml` for current machine state.
7. Synchronize the approved beginner-first contract into formal `DESIGN.md`:
   one product and one signal truth source; default view answers whether a
   confirmed long signal exists; professional metrics and internal terms are
   hidden behind progressive disclosure; no beginner/expert split.
8. Add deterministic tests/fixtures for valid and adversarial status examples,
   and update `PROJECT_MEMORY.md` with delivery evidence without self-approval.

## Allowed scope

- `PROJECT_STATUS.yaml`
- `schemas/project_status.schema.json`
- `scripts/validate_project_status.py`
- status-validator tests and fixtures under `tests/` and `fixtures/g0/`
- `docs/LEGACY_EVIDENCE_MAP.md`
- `AGENTS.md`
- `DEVELOPMENT_WORKFLOW.md`
- `AG_WORK_LOOP.md`
- `DESIGN.md`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`

New files equivalent to the named schema, validator, fixture, test, or mapping
paths are allowed only when the developer explains why the exact path differs.

## Forbidden scope

- No `.github/workflows`, GitHub settings, branch-protection mutation, PR merge,
  supervisor/scheduler/heartbeat implementation, deployment, or release work.
- No exchange network request, private API, credential, order, leverage, short
  logic, strategy threshold, signal algorithm, database, notification provider,
  frontend feature, or live/Paper runtime change.
- No claim that G0 is complete, CI is active, branch protection exists, or the
  product is integration/Paper/release ready.
- Do not modify existing business implementation, contracts, M1-M7 fixtures,
  backend tests, frontend source, dependency locks, or automation scripts.
- Do not start `G0-T02` or any G1+ work.

## Acceptance checks

- Validator accepts the canonical repository state and deterministic valid
  fixtures, and rejects every required adversarial fixture with stable,
  sanitized diagnostics and a non-zero exit status.
- Schema and validator agree; unknown keys and ambiguous/coercible field types
  fail closed.
- A repository/document conflict check finds zero stale current-stage claims in
  governed documents while preserving clearly labelled history.
- Legacy mapping contains traceable evidence and never upgrades M0-M7 above
  `OFFLINE_EVIDENCE_ACCEPTED`.
- Beginner-facing design contains the confirmed information hierarchy, six-item
  signal-card budget, plain-language state translations, progressive disclosure,
  and one-truth-source rule.
- Focused G0 tests, all existing backend tests, frontend tests/build, M1 fixture
  validation, Python compilation, `git diff --check`, allowed-scope scan,
  forbidden-feature scan, and tracked-secret scan pass.
- Delivery is on task branch `codex/g0-t01-canonical-status`, with an immutable
  candidate commit pushed to origin and a complete report. The developer must
  set the task/status to `awaiting_review` but must not write `accepted`.

## Required delivery report

Report task ID, files changed, decisions, exact commands/results, candidate SHA,
branch/upstream status, PR status if one exists, risks/blockers, worktree status,
and memory update. Stop after delivery and wait for independent review.

## Independent review result: returned

- Reviewed exact PR head:
  `6be3e708ad019b46685e3a7986a828df7103239d`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- The product route, beginner-first design, allowed scope, legacy maturity cap,
  focused tests, backend tests, frontend tests/build, and local static checks are
  not the reason for return.

### Repair requirements

1. Make candidate identity executable: the delivered PR exact head is the review
   subject. A prior implementation/content commit may be recorded separately,
   but cannot masquerade as the exact delivered candidate. Do not require any
   commit to contain its own SHA.
2. Replace the single CI object with phase-specific evidence for candidate,
   closure, merged-main, finalization/close D0 as required by the formal loop.
   Define which later commit records each already-existing SHA, and validate Git
   object existence, ancestry, phase, and subject identity when repository
   checks are enabled. Fabricated unrelated SHAs must fail.
3. Resolve the bootstrap deadlock explicitly. G0-T01 is forbidden from creating
   CI, while normal acceptance requires CI. Define one narrow, machine-checked,
   non-reusable G0-T01 bootstrap exception bound to this task, authorization
   baseline, independent dual review, local evidence, and offline maturity. It
   must not relax G0-T02 or any later task.
4. A `returned` state must retain a negative review bound to the exact returned
   candidate and reject pending reviewers or unrelated/success CI. Starting a
   repair must atomically clear old candidate/review/CI identities and increment
   generation.
5. Enforce maturity ceilings across G0-G9. G0-G5 cannot exceed offline evidence;
   G6-G7 cannot exceed integration; G8 cannot exceed Paper validated; G9
   `RELEASE_READY` requires explicit product-owner go and complete release
   evidence.
6. Make document conflict validation structural for every permitted current
   mirror; otherwise forbid current-state claims. Include `PROJECT_MEMORY.md` in
   its historical-only rule. A canonical G0 state must reject conflicting G9,
   task, status, or maturity claims.
7. Add architecture `watch` as a faithful, non-mergeable review result. Validate
   `next_authorization.gate` against its task prefix and permitted route.
8. Catch unreadable/non-UTF-8 governed documents and return a stable sanitized
   validation failure without traceback.
9. Add adversarial tests for every defect above, preserve all existing passing
   behavior, rerun the complete original acceptance set, update status/memory,
   push a new immutable delivery head to the same PR, and stop at
   `awaiting_review`. Do not start G0-T02.

## Generation 2 independent review result: returned

- Reviewed exact delivered head:
  `e2d948f5919a02d9db0abc4aefa00ae28ac03b3d`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- Generation 2 repaired self-referential phase identity, distinct phase CI
  slots, bootstrap handling, returned evidence shape, architecture WATCH,
  maturity ceilings, next-gate checks, and document decoding.

### Generation 3 repair requirements

1. In repository-aware mode, read the direct first parent's committed
   `PROJECT_STATUS.yaml`. Require immutable project/task/gate/risk/baseline and
   bootstrap identity continuity; require `transition.from == parent.state`;
   require generation unchanged for ordinary transitions and exactly parent + 1
   for `returned -> in_progress`. Reject jumps, reuse, rollback, or reappearance
   of a consumed bootstrap exception. Repair start must also clear blockers.
2. Bind `merged_main` to an explicit authoritative main ref. A merge commit only
   reachable from a task/fake branch must fail. Add off-main regression coverage.
3. Bind every active CI identity to the canonical repository remote: URL owner
   and repository must match GitHub origin, URL run number must equal `run_id`,
   and phase `subject_sha` must remain exact.
4. Make the canonical governed-document set mandatory and unique. It must
   include `AGENTS.md`, `DEVELOPMENT_WORKFLOW.md`, `AG_WORK_LOOP.md`, `DESIGN.md`,
   `CURRENT_TASK.md`, and `PROJECT_MEMORY.md`; entries may not be removed,
   duplicated, aliased, or replaced to disable conflict validation.
5. Replace G9 owner-go and release-complete booleans with traceable immutable
   approval and release evidence identities. `RELEASE_READY` must not be
   reachable by self-asserting two booleans.
6. Strengthen phase-subject continuity to include project, current gate, risk,
   implementation SHA, and bootstrap identity. Add rewrite regressions.
7. Require same-gate `next_authorization` task sequence to move forward, and
   reject leftover blockers in normal `in_progress` repair state.
8. Preserve all passing checks; update status/memory, deliver a new exact PR
   head on the same branch, and stop at `awaiting_review`. No G0-T02.

## Generation 3 independent review result: returned

- Reviewed exact delivered head:
  `2384d22ace87ad7d304f3def74a7ff7f19cdf7c7`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- Generation 3 fixed direct-parent transition checks, exact generation increments,
  origin-shaped CI identities, mandatory document membership, same-gate task
  ordering, blocker-free repair starts, and basic main reachability. Focused and
  full backend tests, frontend tests/build, canonical validation, and diff checks
  passed independently.

### Generation 4 repair requirements

1. Validate durable first-parent status history back to the task authorization
   boundary, or introduce an equally durable transition ledger. Reject forged
   intermediate generations and same-status laundering. Same-status commits may
   be allowed only for constrained `in_progress` implementation work; a phase
   state must not silently move its implicit candidate or stale verification.
2. Validate every direct-parent status document against the same schema and
   exact types before continuity comparison or arithmetic.
3. Define and validate one legal inter-task handoff from a fully finalized
   `closed` task to its exact `next_authorization`: generation resets to 1,
   prior evidence/reviews/CI/blockers are cleared, the new baseline binds to the
   accepted main close state, and the consumed bootstrap exception is retired
   permanently. Task, gate, and risk may change only under this rule.
4. Require `merged_main` to be on the authoritative main first-parent chain and
   bind local main to fetched `origin/main` (or equivalent immutable remote-main
   evidence). A second-parent-only fake merge and a movable local-only main ref
   must fail.
5. Enforce monotonic immutable phase CI evidence: inactive may become pending or
   terminal; pending may become terminal only for the same subject, run, and
   URL; terminal evidence cannot be replaced. Apply this to every phase.
6. Bind G9 `release_sha` to the exact finalization/release subject. Release
   approval must name an approving authority and durable authorization identity,
   and the manifest must enumerate its evidence rather than self-asserting
   completeness.
7. Require every mandatory governed path and parent component to be a regular
   repository file, never a symlink or alias. Add adversarial coverage for all
   findings above, preserve the complete passing suite, and return only this
   same G0-T01 card to `awaiting_review`. Do not start G0-T02.

## Generation 4 independent review result: returned

- Reviewed exact delivered head:
  `982e9d0e2d36136f31ce54e63c61ba14001edf2e`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- Main and independent checks passed 61 focused governance tests, all 123
  backend tests, 10 frontend tests and the production build, canonical
  validation, and diff checks. Generation 4 repaired the legal close-to-next
  handoff, phase CI continuity, remote-main first-parent binding, mandatory
  regular documents, and exact G9 evidence shape, but three governance bypasses
  remain.

### Generation 5 repair requirements

1. Make ledger creation an explicit one-time migration authorized only for this
   repository, task, baseline, and exact generation-4 start SHA `fa047696761f235cb1e5cd94bbf1881b49e4bb21`.
   A fresh repository or any other commit must not be able to seal a previously
   invalid generation jump or transition. Preserve digest tamper, reorder,
   truncate, rollback, and anchor checks.
2. From the sealed anchor onward, validate every status commit against the
   current canonical schema with exact types. A post-anchor schema failure is
   terminal; never route it through legacy comparison, even if that historical
   commit includes a locally weakened schema. Add the reproduced floating
   generation/schema-downgrade and restore regression.
3. Make `capability.maturity` monotonic and evidence-transition-bound. Preserve
   maturity across task handoff and every planned, authorized, in-progress,
   awaiting-review, returned, and blocked transition. Permit an upgrade only on
   an explicitly defined accepted/closed transition with the qualifying gate,
   exact candidate, dual review, required phase CI, and exit evidence. Reject
   rollback and skipped levels.
4. Add adversarial coverage for G5 closed/offline to G6 authorized/integration
   inflation, G6 pre-review or returned inflation, G7 to G8 Paper inflation,
   arbitrary rollback, and the fresh-repository self-seal proof. Preserve all
   existing checks and deliver only G0-T01 generation 5 on the same PR. Do not
   start G0-T02 or any runtime/business work.

## Generation 5 independent review result: returned

- Reviewed exact delivered head:
  `702888c6c8e03857879d561eff71ed471f6f449c`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- Generation 5 closed the fresh-ledger fabrication, post-anchor historical
  schema downgrade, and maturity inflation paths. Independent checks passed 70
  focused, 132 backend, 10 frontend tests/build and canonical/diff checks, but
  the schema authority itself and invalid-node fail-closed boundary remain open.

### Generation 6 repair requirements

1. Give the canonical schema an immutable, content-addressed identity and a
   machine-validated migration protocol. Reject arbitrary working-tree or
   committed schema weakening; any future schema change requires an explicit
   previous digest, new digest, version step, authorized migration subject, and
   deterministic compatibility rule.
2. Replace Python loose equality at status identity boundaries with canonical
   typed comparison after schema success. Integer `5` and number `5.0`, booleans
   and integers, or coercible identities must never be byte-equivalent state.
3. Treat every direct-parent and post-anchor schema error as terminal before
   semantic continuity. Do not call parent, maturity, mapping, or arithmetic
   helpers on an invalid node. Diagnostics must be deterministic, sanitized,
   and traceback-free.
4. Add regressions for current-schema weakening plus generation `5.0`, invalid
   maturity containers such as `[]` hidden behind a later valid commit, invalid
   direct parents, schema digest/version rollback, unauthorized migration, and
   a valid no-change schema path. Preserve all prior checks and deliver only
   G0-T01 generation 6. No G0-T02 or business/runtime work.

## Generation 6 independent review result: returned

- Reviewed exact delivered head:
  `5f4503bc7e15ccac74784210fdd260f3c9057d3a`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- Invalid-node terminal gating and the current schema authority were materially
  improved, but exact-head verification failed: focused was 78 passed / 1
  failed and full backend was 140 passed / 1 failed. Two additional authority
  and typed-continuity defects were independently reproduced.

### Generation 7 repair requirements

1. A schema migration must be authorized by a prior immutable subject that
   already binds the proposed `from_revision`, `from_sha256`, `to_revision`,
   `to_sha256`, compatibility rule, task/gate, and migration purpose. The new
   schema commit cannot create its own authorization. A generic closed parent
   without that exact proposal is insufficient.
2. Define and validate the durable schema-migration authorization artifact or
   prior-state field, including canonical serialization/content digest,
   repository/main reachability, single-use consumption, rollback prevention,
   and explicit no-migration state. Do not require a commit to contain its own
   SHA and do not widen this card into G0-T02.
3. Apply typed equality to generation arithmetic/continuity and every remaining
   numeric or identity comparison. Explicitly reject int/float and bool/int
   equivalence before addition or equality.
4. Make the unchanged-schema positive regression independent of the live
   delivery state: build or pin a valid `in_progress` fixture before appending
   ordinary work. Run the entire suite after creating the separate
   `awaiting_review` delivery commit, so the reported exact head itself must
   pass 100%.
5. Add regressions for a self-authorized weakened revision-2 schema, a valid
   prior-content-authorized migration, authorization digest mismatch/reuse,
   generation `1` versus `1.0`, and exact delivery-head suite stability.
   Preserve all prior checks; deliver only G0-T01 generation 7.

## Generation 7 exact-head result: returned before dual review

- Exact delivered and independently reproduced head:
  `b3ed7d4521e2ed3745c92ff4eab8dd57c6c27581`.
- Main code verdict: `REQUEST CHANGES`.
- Route status: `BLOCK` because exact-head acceptance is red.
- The implementation-head suite passed, but the separate delivery HEAD produced
  82 focused passes and one failure. The validator correctly rejects the
  unauthorized migration earlier with `explicit no-migration decision must bind
  current schema authority`; the regression still requires the superseded
  `schema migration is unauthorized or discontinuous` text.

### Generation 8 repair requirements

1. Repair only the stale diagnostic assertion so it accepts the current,
   deterministic earlier fail-closed boundary. Do not weaken validation or
   change production behavior merely to reproduce the old message.
2. Start a new generation atomically; do not append a repair commit to the
   generation-7 `awaiting_review` phase. Preserve all schema authority,
   migration-control, typed-continuity, ledger, maturity, CI, main, G9 and
   product-route behavior.
3. Create the separate generation-8 `awaiting_review` delivery commit first,
   then run focused, full backend, frontend/build, canonical, diff, ancestry,
   allowlist, forbidden and secret checks on that exact immutable delivery HEAD.
   Report only those post-delivery results and stop for dual independent review.
4. No G0-T02, business, runtime, network, Paper, deployment, release or trading
   work is authorized.

## Generation 8 independent review result: returned

- Reviewed exact delivered head:
  `f46c8bb3e7ba8aa59f1031385f4a9e13fb199696`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `CLEAR`.
- Main and independent exact-head verification passed 83 focused, 145 backend,
  10 frontend tests and the production build. The prior migration authorization,
  generation typing, and stable exact-head defects were repaired, but broader
  review found three remaining continuity gaps.

### Generation 9 repair requirements

1. Make schema-migration authorization consumption unique across every relevant
   local and remote repository ref, not only the consumer's first-parent
   ancestors. Reject a second child/branch consuming the same authorization.
   Bind final acceptance to the single canonical remote-main first-parent route;
   document the Git visibility boundary without claiming knowledge of absent
   objects.
2. Maintain an immutable digest history for schema authority and reject reuse of
   any digest previously assigned to an earlier revision. Revisions and content
   must both move forward; a higher revision may not restore old bytes.
3. Extend typed recursive equality to tuples, or remove tuples from governed
   identity comparisons. Explicitly reject `("consumed", True)` versus
   `("consumed", 1)` and `(1,)` versus `(1.0,)`, including bootstrap and CI
   identity paths.
4. Add repository-level sibling-consumption, schema-digest rollback, and nested
   tuple regressions. Preserve all existing tests and production behavior.
   Create the separate delivery commit before running and reporting the entire
   exact-head suite. Deliver only G0-T01 generation 9; no G0-T02 or other scope.
