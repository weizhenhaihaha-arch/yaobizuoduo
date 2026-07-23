# Current AG Task

## Task identity

- Task ID: `G0-T04`
- Gate: G0 planning-only package manifest
- Risk: `D0`
- Status: `in_progress`
- Candidate generation: `3`
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

## Generation 1 delivered planning identity (superseded)

- Implementation SHA:
  `ab351b2a14e16f71177cf56c10870b98b6f0f503`
- Manifest: `governance/packages/package-a.manifest.json`
- Schema/version: `schemas/package_a_manifest.schema.json` /
  `package-a-manifest.v1`
- Schema SHA-256:
  `95974fb830e65221a14e8c7068a6c313277d879a49067e3847328f24276b61f4`
- Normalized payload SHA-256:
  `a7f69d3aacfecb9511e602ce649c80cc4e5a53409928a773abb6ff1eb16d41ff`
- Frozen order: `G0-T05` -> `G1-T01`
- Package state: `not_authorized`
- Review state: awaiting exact delivery-HEAD CI and independent code/security
  plus architecture/route review.

## Generation 1 review result

- Exact candidate:
  `2629f414a52bdcf6ed57db02f17a4973b9a3d8f0`
- Code/security: `REQUEST CHANGES`
- Architecture/route: `BLOCK`
- The generation-1 payload digest `a7f69d3aacfecb9511e602ce649c80cc4e5a53409928a773abb6ff1eb16d41ff`
  is superseded and cannot be confirmed or activated.
- Repair remains limited to G0-T04 manifest/schema/validator/tests/docs.

## Generation 2 repair scope

1. Freeze G1-T01 as complete backend CI, including pinned API dependencies and
   mandatory collected/passing `tests/test_m5_transport.py`.
2. Correct G0-T05's D0 non-transport regression command to ignore the real
   `tests/test_m5_transport.py`; every referenced test/ignore path must exist.
3. Read manifest/schema only from exact committed `100644` Git blobs and reject
   symlink, executable, submodule, tree, or external-byte substitution.
4. Persist manifest/schema/digest/activation and per-card allowlist validation
   after G0-T04, including G0-T05 authorized/in-progress drift rejection.

## Generation 2 delivered planning identity

- Implementation SHA:
  `e385984a25ac06a6db26608a46f9ab6549add691`
- Manifest/schema: `governance/packages/package-a.manifest.json` /
  `package-a-manifest.v2`
- Schema SHA-256:
  `5ebc757f76c58424e88fa6618c806c1bb73ad9dfa9bc09302481e5206c94ceda`
- Normalized payload SHA-256:
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
- Superseded payload SHA-256:
  `a7f69d3aacfecb9511e602ce649c80cc4e5a53409928a773abb6ff1eb16d41ff`
- Frozen order: `G0-T05` -> `G1-T01`
- Package state and first-card state: `not_authorized`
- Review state: awaiting new exact delivery-HEAD CI and independent dual review.

## Generation 2 review result

- Exact candidate:
  `6bc50423fe7aee0f20ef9fb64d3f9953326c99cf`
- Code/security: `REQUEST CHANGES`
- Architecture/route: `BLOCK`
- Full regression exposed an old generic G1 fixture that has no Package A
  manifest in either HEAD or its authorization baseline; generation 2 wrongly
  forced it through Package A persistence checks.
- Repair must preserve OR semantics: enter persistence validation when HEAD or
  baseline carries Package A, and skip only when both are absent.

## Generation 3 repair scope

- Preserve the complete generation-2 Package A v2 manifest and all four review
  repairs unchanged.
- Treat a G0-T05/G1-T01 history as Package A only when its exact HEAD or
  authorization baseline carries the Package A manifest.
- If both are absent, preserve compatibility with pre-Package-A generic
  fixtures.
- If baseline carries Package A but HEAD deletes manifest or schema, continue
  validation and fail closed.
- Retain drift, activation, and per-card allowlist rejection.
