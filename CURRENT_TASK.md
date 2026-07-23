# Current AG Task

## Task identity

- Task ID: `G0-T04`
- Gate: G0 governance anomaly recovery
- Risk: `D0`
- Status: `blocked`
- Candidate generation: `3`
- Baseline: `1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f`
- Exact anomalous authoritative main:
  `4f358cf42b9a8e0f741563425fc26cf532df98fb`

## Single goal

Close only the G0-T04 governance anomaly by binding the exact PR #15, #17,
#19, #20, #21, and #22 histories without rewriting them, neutralizing the
unobserved Package A activation assertion, and restoring the current
authorization boundary.

## Current truth

- Reviews for PR #15, #17, #19, #20, #21, and #22 are all empty.
- Independent code/security is `REQUEST CHANGES`.
- Independent architecture/route is `BLOCK`.
- No product-owner confirmation of Package A was observed.
- Package A payload
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
  remains byte-frozen but `not_authorized`.
- `G0-T05` is `not_authorized`.
- `G1-T01` and all later work are `not_authorized`.
- Capability remains capped at `OFFLINE_EVIDENCE_ACCEPTED`.

The immutable anomaly receipt is
`evidence/g0-t04/pr15-pr22-review-chain.json`. The false activation assertion
previously stored at `evidence/g0-t05/package-a-activation.json` is absent from
the recovery tree but remains permanently visible in Git history.

## Exact recovery topology

1. Implementation is one direct child of
   `4f358cf42b9a8e0f741563425fc26cf532df98fb` and changes only validator/tests.
2. Delivery directly follows implementation and changes only the frozen
   G0-T04 anomaly allowlist.
3. A future recovery merge must have ordered parents
   `[4f358cf42b9a8e0f741563425fc26cf532df98fb, delivery]` and a tree exactly
   equal to delivery.
4. Live validation requires local main and fetched origin/main to equal the
   exact current main; historical replay never consults a moving main ref.

## Frozen allowlist

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `docs/NEXT_WORKFLOW.md`
- `evidence/g0-t04/pr15-pr22-review-chain.json`
- deletion of `evidence/g0-t05/package-a-activation.json`
- `scripts/validate_project_status.py`
- `tests/test_g0_project_status.py`

## Forbidden scope

- No G0-T05 or G1 implementation or authorization.
- No Package A activation or product-owner confirmation claim.
- No manifest/schema/order/payload mutation.
- No workflow, required-check, ruleset, repository-setting, or remote mutation.
- No business, strategy, adapter, API, persistence, frontend, notification, or
  observability implementation.
- No market network access, credentials, accounts, orders, leverage, shorting,
  trading, paid resources, deployment, release, or `LOCAL-PREVIEW`.

## Verification and stop conditions

- Exact topology, receipt bytes, Package blobs, ruleset identity, activation
  neutralization, status, ledger, and cumulative allowlist must all validate.
- Required commands:
  - `python3 scripts/validate_project_status.py --repo-root . PROJECT_STATUS.yaml`
  - `python3 -m pytest -q tests/test_g0_project_status.py -k 'pr15_pr22 or transition_ledger'`
  - `python3 -m pytest -q --ignore=tests/test_api_transport.py --ignore=tests/test_m5_transport.py`
  - `npm --prefix frontend test -- --run`
  - `npm --prefix frontend run build`
  - `python3 -m compileall -q scripts tests`
  - `git diff --check`
- Any failed test, review, topology, identity, blob, ruleset, allowlist, or
  authority check returns only this G0-T04 card.
- Stop after delivery. No push, PR, merge, or next-card dispatch is authorized.
