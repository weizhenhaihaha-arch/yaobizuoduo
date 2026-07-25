# Current AG Task

- Task ID: `G1-T01`
- Gate: G1
- Risk: `D1`
- Status: `returned`
- Candidate generation: `1`
- Baseline: `94c87f28436e2ea8899c9a407e1f1413de893603`

## Goal

Establish one documented, cross-platform and reproducible backend/frontend CI
entrypoint. It must pin Python, API and Node dependency identities; collect and
pass `tests/test_m5_transport.py`; and fail closed across governance, fixtures,
types, builds, dependencies, secrets and forbidden scope.

## Frozen scope

Only the exact G1-T01 `allowed_paths` in
`governance/packages/package-a.manifest.json` may change. The manifest,
activation receipt, ruleset `19526291`, stable required-check name
`G0 / exact-head`, product behavior and offline capability ceiling are
immutable.

## Forbidden scope

No business, strategy, adapter, API or frontend behavior change; no market
network, credentials, accounts, orders, trading, paid resources, deployment,
release, ruleset/repository-setting mutation, required-check rename,
LOCAL-PREVIEW expansion, G2+ implementation or another package.

## Acceptance

Run every exact `acceptance_commands` entry from the frozen manifest. Delivery
must stop at a clean local `awaiting_review` candidate for independent
code/security and architecture/route review. No push, PR, merge or next-card
start is part of the developer delivery.

Authorization was recorded at
`af478f3557ee24bf41e7b06f4249a06c13780c08`; exact implementation
`c07ab506026e660561127f09e65d757c80dfcdb9` produced exact generation-1
candidate `bcc9f6e13befeb49c009008bb2ca23d54ed589d4`. Independent review
returned that candidate: code/security was `REQUEST_CHANGES` for
`PYTHON_3_9_6_UNAVAILABLE_ON_UBUNTU_24_04` and
`OFFLINE_PROCESS_TREE_EGRESS_NOT_ISOLATED`, with nonblocking findings for
pre-setup Python execution, missing Python artifact hashes and narrow secret
patterns; architecture/route was `BLOCK` for `PR_FAST_EXCEEDS_20_MIN`,
`OFFLINE_PROCESS_TREE_EGRESS_NOT_ISOLATED`,
`PYTHON_ARTIFACT_HASHES_MISSING`, and
`LOCAL_VERIFICATION_RECORDED_BEFORE_EXACT_GREEN`. Exact PR CI, push, merge and
every later task remain unclaimed.
