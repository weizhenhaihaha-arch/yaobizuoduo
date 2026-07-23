# Current AG Task

## Task identity

- Task ID: `G0-T04`
- Gate: G0 planning-only package manifest
- Risk: `D0`
- Status: `in_progress`
- Candidate generation: `1`
- Executor: one bounded planning/developer AG
- Reviewer: main Codex plus independent code/security and architecture/route lanes
- Authorization: product owner explicitly authorized this planning-only card on 2026-07-23 Asia/Shanghai
- Baseline: `1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f`

## Single goal

Produce and mechanically validate one immutable Package A manifest. The manifest
must freeze the exact later cards needed to finish G0 governance and establish
G1 reproducible full CI. Completing this card does not activate Package A.

## Required outputs

1. One machine-readable Package A manifest that binds its repository-relative
   path, schema/version, generation, authoritative baseline, canonical
   serialization and payload digest, first card, last card, and exact ordered
   card list.
2. For every Package A card, freeze its task ID, gate, risk, goal, inputs,
   outputs, allowed paths, forbidden scope, acceptance commands, default
   fail-closed decisions, automatic-continuation preconditions, and stop
   conditions.
3. Define mechanical validation that rejects unknown fields, card reordering,
   digest or baseline drift, scope expansion, non-serial cards, missing
   independent review, automatic cross-package continuation, and any implicit
   Package A activation.
4. Reconcile human-facing governance documents with the current authoritative
   G0-T03 close and the standing automatic-merge rule for explicitly authorized
   cards.
5. Preserve the formal G0 -> G1 -> ... -> G9 route and the current capability
   ceiling `OFFLINE_EVIDENCE_ACCEPTED`.

## Allowed scope

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `README.md`
- `DEVELOPMENT_WORKFLOW.md`
- `AG_WORK_LOOP.md`
- `docs/NEXT_WORKFLOW.md`
- One new Package A manifest and, if required, its local schema.
- Focused manifest validator code and governance tests only.

## Forbidden scope

- No G0 implementation work beyond planning/validation.
- No G1 implementation or required-check mutation.
- No business, strategy, adapter, API, persistence, frontend, notification, or
  observability implementation.
- No public/private market network access, credentials, accounts, orders,
  leverage, shorting, trading, paid resources, deployment, release, or
  `LOCAL-PREVIEW`.
- No GitHub ruleset or repository-setting mutation.
- No Package B/C/D activation and no authorization of G2+.

## Acceptance and stop conditions

- The manifest is immutable by path, baseline, generation, normalized digest,
  first/last card, ordered task list, and exact field sets.
- Package A contains only later, uniquely numbered cards; `G0-T04` cannot be
  reused as an implementation card.
- Package A remains `not_authorized` after this card closes. The product owner
  must confirm the exact manifest digest once before any Package A card starts.
- Automatic continuation is legal only inside an authorized package and only
  after the prior card's merged-main/fresh-clone acceptance with no
  HEAD/base/tree/ruleset/allowlist drift.
- Any new goal, semantic change, unknown path, implementation work, network
  requirement, external permission, paid resource, ruleset change, deployment,
  release, credential, or trading need stops this card without guessing.

## Required verification

- Canonical project-status validation from the exact task HEAD.
- Focused positive and adversarial manifest-validator tests.
- Full existing non-transport Python suite.
- Frontend tests and production build to prove no regression.
- Python compilation, whitespace, changed-path allowlist, forbidden-scope, and
  tracked-secret checks.
- Exact PR-head CI and independent dual review before automatic merge.
- Ordered-parent/tree, authoritative-main CI, remote readback, fresh-clone
  validation, and memory close after merge.

## Required delivery report

Report task/baseline/generation, manifest path/schema/digest/first-last cards,
ordered Package A cards, frozen per-card scope and commands, validator tests,
full verification, changed paths, forbidden-scope scan, PR/run, independent
reviews, blockers, worktree state, and repository/external memory updates.
