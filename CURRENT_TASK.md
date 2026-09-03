# Current AG Task

- Task ID: `G1-T01`
- Gate: G1
- Risk: `D1`
- Status: `in_progress`
- Candidate generation: `4`
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

## Generation 2 repair boundary

The returned candidate remains immutable. This repair only:

- uses exact Python `3.12.10`, available from `actions/python-versions` for
  Ubuntu 24.04 x64 and Windows x64, before any repository Python execution;
- requires SHA-256 hashes for every Python artifact;
- installs dependencies before reversible OS-level egress isolation and
  mechanically denies Python, Node and curl child-process connections;
- restores Linux and Windows network policy both in-process and through
  `always()` cleanup;
- partitions every platform's complete collection into four deterministic,
  disjoint shards and uses bounded pytest workers under the 20-minute job cap;
- keeps local verification pending until the new exact candidate is actually
  green.

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
`LOCAL_VERIFICATION_RECORDED_BEFORE_EXACT_GREEN`. Generation 2 is now the only
active repair and clears all implementation, candidate, review, CI and blocker
claims until a new exact candidate is genuinely verified.

Generation-2 implementation `3702d4c65e6ae5b1642ce8e09883390bebfb93e6`
is now locally verified. Exact Python 3.12.10 installed the complete hashed
dependency closure without an index; the one final raw suite passed 603/603,
and the corrected unified entrypoint passed canonical status, transport 6/6,
the complete suite 603/603 with four workers, dependency integrity, frontend
10/10, production build, compilation and diff checks. Delivery is frozen at
`d752b155fa578a8e017bb3d76483558c6260ae4a`. PR #39 exact-head run
`33648740889` bound that exact subject but failed all four Linux shards, all
four Windows shards and aggregate `G0 / exact-head`. Independent code/security
returned `REQUEST_CHANGES` and architecture/route returned `BLOCK`, both bound
to that candidate. The candidate is therefore returned without rewriting its
commit or CI history. No merge or later task is authorized by this record.

## Generation 3 portability repair boundary

Generation 3 starts through the legal `returned -> in_progress` transition and
clears every generation-2 active implementation, candidate, phase-CI, review,
and blocker identity while preserving the immutable history above. This repair
is limited to four hosted-CI defects: platform-neutral governed-text digests
that retain worktree tamper detection, nested-test isolation from outer shard
variables without weakening egress guards, deterministic self-contained Git
history fixtures without alternates or hidden refs, and fixed test-only author,
committer and time identity for generated commits. It must use only the minimum
necessary existing manifest allowlist paths, pass focused regressions and every
frozen acceptance command, and stop at a new clean `awaiting_review` delivery.

Generation-3 implementation `7c0a1b2877b52a9445f59dd79f1864648915662b`
keeps the production validator unchanged and makes the final two historical Git
tests self-contained. The exact Python 3.12.10 raw suite passed 607/607 in
3279.47 seconds; Transport passed 6/6; the unified offline entrypoint passed
canonical validation, Transport 6/6, the complete four-worker suite 607/607 in
1083.38 seconds, dependency integrity, frontend 10/10, production build,
compilation and diff checks. Delivery stops at `awaiting_review`; hosted CI,
independent reviews, merge, G2 and every product capability remain unclaimed.

Hosted run `33715808959` bound exact generation-3 delivery
`e31cb8b390e9ccbf1b3c127d3103a7accb1af347` and failed. All four Windows jobs
failed because Git output containing UTF-8 governed text was decoded through
the runner's cp1252 locale; all four Linux jobs failed the same CRLF portability
fixture because the test itself made an awaiting-review checkout dirty. Remote
logs also proved every nominal shard ran the complete 607-test collection
because the nested verifier overwrote the outer shard identity. Independent
review therefore returned this exact candidate with code/security
`REQUEST_CHANGES` and architecture/route `BLOCK`. Generation 3 is returned;
the failure is immutable evidence and grants no G2 or product authority.

## Generation 4 final bounded repair

Generation 4 starts through the legal `returned -> in_progress` transition and
clears every active generation-3 implementation, candidate, phase-CI and review
identity. The repair is capped at exactly three hosted-CI defects already proven
by run `33715808959`: strict UTF-8 Git-output decoding on Windows, a genuinely
clean CRLF checkout fixture, and preservation of the outer four-shard identity.
It may change only the minimum existing Package A allowlist files, must retain
strict dirty-worktree and egress protection, and must stop if a fourth
independent root cause appears. No strategy, market, API, UI, credential,
deployment, release, order or G2 capability is authorized.
