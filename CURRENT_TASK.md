# Current AG Task

## Task identity

- Task ID: `G0-T05`
- Gate: G0 governance handoff
- Risk: `D0`
- Status: `in_progress`
- Candidate generation: `2`
- Executor: Codex under the confirmed immutable Package A
- Reviewer: main Codex plus independent code/security and architecture/route lanes
- Authorization: product owner confirmed the exact Package A payload digest on 2026-07-23 Asia/Shanghai
- Baseline: `8f3cfc2ba8c7ba533c8e7d065c0f7e5c27a3e373`

## Single goal

Close the remaining G0 governance handoff by binding Package A activation to
the product-owner-confirmed immutable manifest digest while preserving the
required-check, ruleset, route, and capability boundaries.

## Immutable activation identity

- Package: `PACKAGE-A`, generation `2`
- Payload SHA-256:
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
- Activation record: `evidence/g0-t05/package-a-activation.json`
- Exact order: `G0-T05` -> `G1-T01`
- Only G0-T05 is active; G1-T01 remains the sole next not-authorized task.

## Current G0-T05 allowed scope

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `docs/NEXT_WORKFLOW.md`
- `evidence/g0-t05/package-a-activation.json`
- `scripts/validate_project_status.py`
- `tests/test_g0_project_status.py`

No other path is authorized for this card. The Package A manifest and schema
are immutable inputs, not writable G0-T05 scope.

## Current forbidden scope

- No workflow, required-check, ruleset, or repository-setting mutation.
- No G1 implementation before G0-T05 fully closes.
- No business, strategy, adapter, API, persistence, frontend, notification, or
  observability implementation.
- No public/private market network access, credentials, accounts, orders,
  leverage, shorting, trading, paid resources, deployment, release, or
  `LOCAL-PREVIEW`.
- No Package B/C/D activation and no G2+ authorization.

## Current acceptance and stop conditions

- The activation is already authorized by the exact owner-confirmed Package A
  payload digest; no second confirmation is required inside this package.
- Manifest/schema/activation bytes, task order, baseline, HEAD, parents, tree,
  ruleset, allowlist, CI subject, reviews, and capability ceiling must remain
  exact.
- Exact delivery-head CI and independent code/security `APPROVE` plus
  architecture/route `CLEAR` are required before acceptance.
- Ordered-parent/tree, authoritative-main CI, remote ruleset readback,
  fresh-clone validation, and memory close are required before G0-T05 closes.
- G1-T01 may activate automatically only after those G0-T05 close conditions
  pass; any drift, unknown path, external permission, network, credential,
  trading, deployment, release, paid-resource, or cross-package need stops
  without guessing.

## Current verification

- `python3 scripts/validate_project_status.py --repo-root .`
- `python3 -m pytest -q tests/test_g0_project_status.py -k 'package_a or g0_t05'`
- `python3 -m pytest -q --ignore=tests/test_m5_transport.py`
- `npm --prefix frontend test -- --run`
- `npm --prefix frontend run build`
- `python3 -m compileall -q scripts tests`
- `git diff --check`

## Historical appendix

All sections below record superseded G0-T04 planning generations, reviews,
merge recovery, and final close. They are evidence history only and grant no
current path, state, or capability authority.

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

## Generation 3 delivered planning identity

- Implementation SHA:
  `57d65f47709b4f683e4326051c737ed037b15b83`
- Manifest/schema remain unchanged from generation 2:
  `governance/packages/package-a.manifest.json` /
  `package-a-manifest.v2`
- Schema SHA-256 remains:
  `5ebc757f76c58424e88fa6618c806c1bb73ad9dfa9bc09302481e5206c94ceda`
- Normalized payload SHA-256 remains:
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
- Compatibility guard: persistent Package A validation applies when either
  exact HEAD or authorization baseline carries the manifest; it skips only
  when both are absent.
- Adversarial coverage retains fail-closed rejection for baseline-present
  manifest/schema deletion, drift, activation substitution, and allowlist
  escape.
- Package state and first-card state remain `not_authorized`.
- Exact PR-head CI: run `29987891035`, event `pull_request`, subject
  `be45d7fee1f5e4a34b14bd035539d5a3a462dad8`, stable check
  `G0 / exact-head`, terminal `success`.
- Main Codex exact-HEAD verification: canonical validator, 22 focused
  Package A tests, 362 non-transport Python tests, 10 frontend tests,
  TypeScript/Vite production build, compilation, changed-path allowlist,
  committed `100644 blob` identity, secret scan, and live ruleset readback all
  passed.
- Independent code/security: `APPROVE`.
- Independent architecture/route: `CLEAR`.
- Ruleset `19526291`, baseline/main, manifest/schema digests, Package A
  inactive state, and forbidden capability boundaries remained unchanged.
- This acceptance authorizes only the automatic merge closure for G0-T04. It
  does not activate Package A or authorize G0-T05/G1.

## Generation 3 merged-main recovery

- PR #14 merged as exact authoritative-main subject
  `11040ca0d8ea17ba1bc47641705aa95c2cba6a75` with ordered parents
  `[1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f,
  bdf6fbca71b29da79801c1be7a4cdd14f103ce52]` and tree
  `12d85f91119ee802d3f92405ceb619ed18534e4d`.
- The exact push run `29988167026` failed only in canonical governance
  validation; candidate run `29987891035` and closure run `29988100257`
  succeeded.
- Recovery remains at `accepted_pending_merge` with the exact failed-run
  blocker. It does not claim `merged_verified` or `closed`.
- The bounded recovery accepts only a status-identical single-parent repair
  rooted at the failed merge and a future exact two-parent merge whose first
  parent is the failed main and whose tree equals its recovery second parent.
- The Package A manifest/schema/digests/order remain byte-identical and
  `not_authorized`; G0-T05, G1, market access, ruleset mutation, credentials,
  trading, deployment, and release remain outside authority.

## Generation 3 merged-main verification

- Recovery candidate `06feb30d43360ef732242f1be4ad02478823f47a`
  passed exact pull-request CI run `29990406421`, code/security `APPROVE`,
  architecture/route `CLEAR`, and all 264 governance test nodes.
- PR #15 merged as `8d87f58e690a2ea7fac74d432495c8873d5a9d87`
  with ordered parents
  `[11040ca0d8ea17ba1bc47641705aa95c2cba6a75,
  06feb30d43360ef732242f1be4ad02478823f47a]`; its tree equals the recovery
  candidate tree `4b7404240a4f81282764059b63be906fec5da377`.
- Authoritative-main exact-head CI run `29991346572` succeeded. The failed-main
  blocker is therefore cleared and G0-T04 advances only to `merged_verified`.
- Package A remains immutable and `not_authorized`; this record does not
  activate G0-T05, G1, market access, ruleset mutation, deployment, release,
  credentials, or trading.

## Generation 3 final close

- Finalization subject `b7a2e3fa15d09de15293a384e58bf4575e0cdeca`
  passed exact pull-request CI run `29991698097`.
- G0-T04 therefore advances from `merged_verified` to `closed`; the Package A
  manifest, schema, payload digest, ordered task list, and inactive authority
  state remain unchanged.
- `next_authorization` remains G0-T05 `not_authorized`. Package A requires one
  explicit owner confirmation before any package card may activate.
