# Current AG Task

- Task ID: `G1-T01`
- Gate: G1
- Risk: `D1`
- Status: `in_progress`
- Candidate generation: `14`
- Baseline: `94c87f28436e2ea8899c9a407e1f1413de893603`

## Goal

Establish one documented, cross-platform and reproducible backend/frontend CI
entrypoint. It must pin Python, API and Node dependency identities; collect and
pass `tests/test_m5_transport.py`; and fail closed across governance, fixtures,
types, builds, dependencies, secrets and forbidden scope.

## Generation 14 Windows output-encoding authorization

The product owner explicitly authorized one single-root repair after exact
Generation 13 candidate `d0e7c9b494f67d5663f4eb3878ea0dd295106216`
passed all four Ubuntu shards but failed all four Windows shards in run
`33837192832`. Every Windows job failed before test execution when the complete
verifier attempted to emit Git diff output containing U+7684 through the
runner's locale-dependent `charmap` codec.

This authorization is the exact two-parent record whose first parent is
authoritative close `94c87f28436e2ea8899c9a407e1f1413de893603` and whose
second parent is immutable Generation 13 blocked record
`394bad121f80304587d5ebc408560f789be1c8a1`. The trend-signal and strategy
engineer may change only `scripts/verify_full_ci.py` and
`tests/test_verify_full_ci.py` to make verifier output explicit, strict and
predictable UTF-8 across Windows, Linux and macOS, preserve fail-closed
diagnostics, and add direct regression coverage using non-ASCII Git diff
output.

The 870-second local deadline, hosted 15-minute step, 20-minute job, test
collection, assertions, four-shard assignment, dependency and workflow
behavior, governance rules and every product file remain frozen. Deleting,
skipping or weakening tests, changing dependencies or workflows, creating a
new PR, rewriting history, or starting P1, G2, Signal V1, market, database,
API or UI work is forbidden. Delivery stops after focused tests, compilation,
scope/diff/secret/clean checks and independent review. The accepted integrated
SHA receives one complete local validation; failure, a new root, or required
scope expansion stops without Generation 15.

### Generation 14 two-file repair acceptance

The trend-signal and strategy engineer's delivery
`82ba378475742acf1f39a0a003d376ccdcbb7f93`, directly based on exact start
`2a54c323a1c04e2cdf74fa014a442e4308c828b1`, is independently accepted and
frozen. Only `scripts/verify_full_ci.py` and `tests/test_verify_full_ci.py`
changed. Verifier-owned output now uses strict UTF-8 bytes instead of the host
text code page; non-ASCII Git diff output works under an ASCII-strict simulated
code page, while invalid Unicode and invalid subprocess UTF-8 still fail
closed.

Owner verification passed the complete focused verifier file with 47 passed
and one existing Windows-only skip, compilation, exact scope, diff, clean
worktree and secret checks. Independent code/security returned `APPROVE` and
architecture/route returned `CLEAR`. The 870-second local deadline, hosted
15/20-minute limits, test collection, four-shard workflow, dependencies,
process cleanup, governance and product code remain unchanged. This accepted
delivery is not yet the complete-validation candidate, upload, hosted CI,
merge, G1 closure, P1, G2 or UI authority.

## Generation 13 clean dependency preparation authorization

The product owner explicitly authorized one environment-preparation retry after
Generation 12 stopped on a missing local `frontend/node_modules` tree. This
authorization is the exact two-parent record whose first parent is authoritative
close `94c87f28436e2ea8899c9a407e1f1413de893603` and whose second parent is the
immutable Generation 12 blocked record
`124fbc9829c552064e1c0c561750f5e6439097f0`.

Generation 13 changes no product, validator, test, dependency lock, workflow or
timeout. In a new isolated worktree it may prepare only ignored
`frontend/node_modules` using exact Node `24.14.0`, npm `11.9.0`, the unchanged
lockfile and `npm ci --ignore-scripts`. It must try the local npm cache first;
if that cannot complete, only unauthenticated `https://registry.npmjs.org/` is
allowed. Copying dependencies from an older worktree or using another registry
is forbidden.

Before the sole complete validation, the owner must prove exact runtime and
package/lock identities, successful `npm ls --all --offline`, all ten direct
dependency versions, unchanged tracked files, a clean Git worktree and no
secrets. A preflight failure does not consume the complete-validation chance.
Only after all preflight gates pass may the owner form the exact validation
subject and run `scripts/verify_full_ci.py --offline --fail-closed
--require-transport` once under the unchanged 870-second deadline. Any complete
validation failure, code/lock/workflow drift, dirty state, identity mismatch or
new root stops without an automatic Generation 14. G2, P1 and all Signal V1/UI
product writes remain inactive until G1 legally closes.

Exact Generation 13 authorization `c499d751797fd7aaa6f4196a985dbc9cc873d71c`
passed the canonical project-status validator with ordered parents
`[94c87f28436e2ea8899c9a407e1f1413de893603,
124fbc9829c552064e1c0c561750f5e6439097f0]`. The owner now starts only the
clean dependency preflight described above. No product/UI work, tracked source
change or complete-validation run is active at this point.

### Generation 13 dependency preflight acceptance

The clean preflight on exact start `623015bd28c3053a45ff2bd8cbc1a3490f41fa73`
used Node `24.14.0` and npm `11.9.0`. `frontend/node_modules` was initially
absent, then `npm --prefix frontend ci --ignore-scripts --offline` installed
142 packages from the local cache and reported zero vulnerabilities. Offline
`npm ls --all` succeeded and the ten direct packages exactly matched the
unchanged manifest. `frontend/package.json` retained SHA-256
`a34daf0cd3b4a3c57cb8f12179dcaed167857ba76055f3f0dc87b37cc24197ee` and
`frontend/package-lock.json` retained SHA-256
`a7102e645d5df34e3539000c6793cab99179d778fbdab64b2692ca8558d729c3`.
Tracked state, whitespace, fixture inventory, authorized scope and secret scan
all passed. No official-registry fallback was needed and no tracked source,
test, lock, workflow, product or UI file changed. The strict child of this
record is the sole Generation 13 complete-validation subject.

### Generation 13 complete local validation

The sole complete local validation ran once on exact subject
`032f8203ee4bfa5cc62222c7f82b275d33232fbd` and returned `FULL_CI_OK` under the
unchanged 870-second deadline. Canonical status and Transport collection/run
6/6 passed; the complete backend suite passed 644 tests with two platform-only
skips in 267.79 seconds; Python dependency integrity passed; offline frontend
dependency readback passed; frontend tests passed 10/10; the production build,
Python compilation and final whitespace check passed. The worktree remained
clean and no tracked file was changed by validation. This strict child records
only a local `awaiting_review` candidate. Upload, hosted Ubuntu/Windows CI,
independent reviews, merge, G1 closure, G2 and product/UI authority remain
unestablished.

## Generation 12 performance-only authorization

The product owner explicitly authorized one evidence-led performance repair
after Generation 11 exhausted its single complete local validation. This
authorization is the exact two-parent record whose first parent is authoritative
close `94c87f28436e2ea8899c9a407e1f1413de893603` and whose second parent is the
immutable Generation 11 blocked record
`5d4abc9ae9e08b2e118e4205572e19003526ecf1`.

Before implementation, the owner must perform bounded read-only profiling and
freeze exactly one performance root. The repair may then change exactly one of
these mutually exclusive file groups: (A) `scripts/validate_project_status.py`
and `tests/test_g0_project_status.py`, or (B) `scripts/verify_full_ci.py` and
`tests/test_verify_full_ci.py`. It may cache immutable Git reads, reuse
equivalent test setup, reduce duplicate identical temporary repositories, or
optimize equivalent local scheduling, but it may not change validation
semantics, the 870-second internal deadline, hosted 15-minute step, 20-minute
job, test collection, assertions, four-shard identity, strict UTF-8/CRLF,
egress isolation, process-tree cleanup, dependencies, workflow behavior,
governance rules, product code or Signal V1.

Only focused durations, small test groups, read-only profiles, Git subprocess
counts and existing logs may be used during diagnosis; no complete validation
is permitted before a delivery passes owner checks and independent read-only
review. The accepted integrated SHA receives exactly one complete local
validation. A remaining timeout, new root cause, output change, dirty worktree
or identity mismatch stops Generation 12 without an automatic Generation 13.
G2 and all product writes remain inactive until G1 legally closes and P1 shared
contracts are frozen.

### Frozen Generation 12 performance root

Owner diagnosis freezes only file group A. A single canonical-status pytest
case did not complete before a bounded stop at 321.89 seconds, and a separate
ordinary repository-aware validator run remained CPU-active until its bounded
stop at 111.74 seconds. The captured stack repeatedly cycles through
`_blocked_reauthorization_errors()` -> `_history_errors()` ->
`_parent_status_errors()` for nested immutable blocked-generation ancestry,
while re-running Git reads such as schema-control lookups. This establishes the
single repair root as uncached repeated validation of the same immutable Git
history and Git objects.

Implementation is therefore limited to `scripts/validate_project_status.py`
and `tests/test_g0_project_status.py`. The engineer may add validation-scoped
memoization for immutable Git/status/schema/history results and direct
equivalence/performance regression coverage. Group B, all verifier behavior,
deadlines, workflow, test collection, assertions, governance semantics and
product paths remain forbidden.

### Generation 12 performance delivery acceptance

The trend-signal and strategy engineer's repaired delivery
`64d27ca45f1dfb8b5df12c95fd75853f3643f08a`, based on exact Generation 12
start `3fb67cbf22a97ab2c4b5ae6e010170b4b64c8038` through preserved first delivery
`ba034c8813911844ccf27caf38e0a4636243bd7e`, is independently accepted and
frozen. Only `scripts/validate_project_status.py` and
`tests/test_g0_project_status.py` changed. The repair caches only strict
full-SHA Git object/history reads inside one synchronous `validate()` context;
remote URL, visible refs, worktree status, HEAD/ref verification and unknown
Git command shapes remain live and fail closed. The unsafe whole-history
aggregate cache from the first delivery was removed.

Owner verification passed ten focused cache/live-state/canonical tests in 1.77
seconds and the repository-aware canonical test in 39.58 seconds, plus
compilation, diff, two-file scope, clean-worktree and secret checks. Independent
code/security review returned `APPROVE`; independent architecture/route review
returned `CLEAR` for the frozen synchronous, single-repository execution model.
Future asynchronous validation or concurrent Git object mutation is only a
non-blocking observation and is not authorized for speculative work here. This
acceptance is not the complete validation, candidate, upload, hosted CI, merge,
G1 closure, G2 or product authority. The exact acceptance/integration child
gets Generation 12's one complete local validation opportunity under the
unchanged 870-second deadline.

### Generation 12 terminal validation result

Generation 12 used its sole complete local validation on exact acceptance and
integration head `5ff60af5dff9bf03b1a2ccf735423463112fd75c`. Canonical project status and
mandatory Transport collection/execution 6/6 passed. The unchanged complete
backend suite passed 644 tests with two platform-only skips in 265.37 seconds,
and Python dependency integrity passed. This confirms that the accepted
validator-performance repair removed the prior multi-minute canonical
bottleneck without changing the backend result set.

The next offline frontend dependency check failed because this isolated
Generation 12 worktree did not contain `frontend/node_modules`; npm reported
all ten exact frontend dependencies as unmet. Frontend tests/build, compilation
and final diff checks were therefore not reached and are not claimed. A
read-only check confirmed the dependency tree is absent in this worktree while
older isolated G1 worktrees contain their own installed trees. This is a new
validation-environment root, not the frozen repeated-Git-history performance
root and not evidence of a product or frontend source defect.

The exact SHA will not be rerun. Generation 12 stops as `blocked` with no
automatic Generation 13, candidate, upload, hosted CI, merge or G1 closure.
G2 remains `not_authorized`, P1 is inactive and Signal V1 product code may not
start. Further action requires an explicit product-owner decision authorizing
a clean pinned frontend dependency bootstrap before a new exact-head complete
validation opportunity; no timeout, test, workflow, governance, product,
credential or trading expansion is implied.

## Generation 11 final timing exception

The product owner explicitly authorized one final, bounded repair after
Generation 10 exhausted the two automatic repairs for the same local complete-
validation timing root. This authorization is the exact two-parent record whose
first parent is authoritative close
`94c87f28436e2ea8899c9a407e1f1413de893603` and whose second parent is the
immutable Generation 10 blocked record
`078bb26e30e8fd8f01eb18d026c24bdde77f4540`.

Exact two-parent authorization
`c7528d458292d40deeae7e04652d29109a14f6d7` passed canonical validation. Its
strict child activates only this final timing exception and dispatches it back
to the original trend-signal and strategy engineer.

The trend-signal and strategy engineer may change only
`scripts/verify_full_ci.py` and `tests/test_verify_full_ci.py` to increase the
single shared internal deadline from 840 to 870 seconds and add direct
regression coverage. The hosted verification step remains 15 minutes, the job
remains 20 minutes, the complete test and command set remains unchanged, and
the four-shard assignment, strict UTF-8/CRLF behavior, egress isolation and
process-tree cleanup may not be weakened. After focused owner verification and
independent read-only review, the new integrated SHA receives exactly one
complete local validation. A further timeout or any new independent root cause
blocks the card without another automatic repair. This grants no G2 or Signal
V1 product write before G1 legally closes and the owner freezes the P1 shared
contracts.

### Generation 11 timing delivery acceptance

The trend-signal and strategy engineer's exact delivery
`4c4c02d2e7d8191b38dfb2b71be40eb37cc73daa`, directly based on the verified
Generation 11 start `4afeb52da87fa66f9b0d503d4e85f76b95d07c16`, is independently accepted and
frozen. Its diff changes only `scripts/verify_full_ci.py` and
`tests/test_verify_full_ci.py`: the one shared verifier deadline is now exactly
870 seconds and a direct regression proves the initial budget, monotonic
deadline and fail-closed exact-cutoff behavior. No existing test is removed,
skipped or weakened; four-shard behavior, strict UTF-8/CRLF handling, egress
isolation and process-tree cleanup are unchanged. The hosted verifier steps
remain 15 minutes and the matrix job remains 20 minutes.

Owner verification passed 45 focused tests with one existing Windows-only Job
Object test skipped on macOS, compilation, exact-parent/scope/diff checks,
clean-worktree inspection and secret scan. Independent read-only review
returned `APPROVE` after 12 focused passes with 34 deselected, compilation,
workflow timeout inspection and the same scope/security checks. This is
accepted implementation evidence only. The owner must now create one unique
integrated SHA and run its single permitted complete local validation; a
timeout or new independent root blocks the card. Nothing here is upload,
hosted CI, merge, G1 closure, G2 activation or product authority.

### Generation 11 terminal validation result

The sole complete local validation of exact integrated head
`5e1dad5a1f3750fdb4b6d2406d7cf243c8adfb29` passed canonical project status
and mandatory Transport collection/execution 6/6. The unchanged complete
backend suite then exceeded the one shared 870-second deadline under eight
local workers and failed closed. The verifier reaped its process tree and the
worktree remained clean. Python dependency, frontend test/build, compilation
and final diff stages were not reached, so none is claimed for this run.

This was the one complete-validation opportunity explicitly authorized for
Generation 11. It will not be rerun, the deadline will not be increased again,
and no candidate, upload or remote CI will be created from this SHA. G1-T01 is
`blocked`; G2 remains `not_authorized`, P1 is not active, and no Signal V1
product code may start. Further action requires a new product-owner decision
because the bounded final timing exception has been exhausted.

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

## Generation 4 returned evidence

Generation-4 delivery `19b8e7250e7fc1032ab490f86721fa80c6574311`
passed its complete local acceptance and was pushed to PR #39. Hosted run
`33740584116` was reported green by GitHub, but the raw logs from all four
Windows shards contain `FULL_CI_FAILED: fixture digest drifted:
fixtures/g0/adversarial_mutations.json`. The PowerShell step did not preserve
the native verifier's nonzero exit status across firewall restoration, so the
job and aggregate result were false green. The fixture verifier also hashes
raw checkout bytes and therefore rejects a clean Windows CRLF checkout.
Independent review bound to the exact candidate returned code/security
`REQUEST_CHANGES` and architecture/route `BLOCK`. Generation 4 is returned;
closure and merge are prohibited. Any next repair remains limited to these two
existing Windows fail-closed and clean-CRLF defects.

## Generation 5 minimal false-green repair

Generation 5 starts through the legal `returned -> in_progress` transition and
atomically clears all generation-4 active implementation, candidate, CI and
review identities while preserving the immutable candidate and raw-log failure
above. This repair is limited to exactly two already-authorized defects:

- preserve and explicitly propagate native Python and Node nonzero exit codes
  through the Windows PowerShell firewall-restoration `finally` path; and
- make frozen text-fixture digests newline-neutral under clean LF and CRLF
  checkouts while strict UTF-8 decoding and real content-tamper rejection stay
  fail closed.

The two fixes may proceed in isolated paths and be reviewed independently.
They may add only direct regression coverage proving a failing native verifier
fails the Windows job, firewall restoration still runs, LF and CRLF are
equivalent, and real fixture mutation is rejected. No additional root cause,
test weakening, product behavior, G2 capability or governance mechanism is in
scope.

### Generation 5 independent-lane acceptance

- The Windows native-exit repair was independently accepted at delivery
  `d21cbb5bfbef880c0ecf4a2d60034d14d751d13e` after commit identity, two-file
  scope, clean worktree, diff, secret scan, static workflow contract, and the
  local `1 passed, 1 skipped` PowerShell regression result were verified. The
  skip is the real PowerShell runtime check and remains a Windows hosted-CI
  obligation. Its isolated branch upload failed because GitHub port 443 was
  unreachable, so the exact delivery is frozen in the pending-upload queue.
- The newline-neutral strict-UTF-8 fixture repair was independently accepted at
  delivery `bbb60d4ad517e09cbf1ab3d6ab3a56df88ab5fe9` after commit identity,
  two-file scope, clean worktree, diff, project-status validation, secret scan,
  and `27 passed` focused regressions were verified. It is waiting for the same
  upload channel; no duplicate upload was attempted after the channel failure.
- Both accepted repairs are now combined locally, without conflict, as
  integration commits `0aa2018` and `a5c666c`. This is an in-progress local
  integration checkpoint only: the one complete acceptance run, a new frozen
  candidate SHA, hosted Windows CI, independent candidate reviews, merge, G1
  closure and G2 authorization are all still pending.
- The upload channel later recovered through a one-shot HTTP/1.1 Git transport
  retry. Remote branch readback now binds the two independent deliveries to
  exact `d21cbb5bfbef880c0ecf4a2d60034d14d751d13e` and
  `bbb60d4ad517e09cbf1ab3d6ab3a56df88ab5fe9`, and PR #39 temporarily binds the
  in-progress integration record `e6ab2a3214b76aed11fcb140d4462970dc2ff390`.
  This clears only the upload backlog; it does not establish a Generation-5
  candidate or count any resulting workflow run as candidate CI.

### Generation 5 terminal stop

PR #39 run `33746059061` bound exact in-progress subject
`1d0cccbb667a872f2d52592be1a614c74cc3702c`. All four Linux shards passed and
all four Windows shards failed; aggregate `G0 / exact-head` failed. Windows
logs show that the offline socket guard directly accesses `socket.AF_UNIX`,
which is unavailable on that runner, and therefore breaks loopback socket
creation used by the transport tests. The repaired PowerShell path correctly
propagated the verifier's nonzero status, so this is a real red result rather
than another false green.

This Windows socket-guard portability defect is independent of the only two
Generation-5 repairs and is outside their authorized boundary. Under the
explicit fourth-root stop rule, G1-T01 is now `blocked`; no additional repair,
candidate, review, merge, G2 implementation, product code or trading capability
is authorized without a new user decision.

## Generation 6 owner-authorized socket-guard repair

The product owner explicitly authorized continuation after reviewing the
generation-5 terminal stop. Generation 6 is a new two-parent authorization
record rooted at authoritative G0 close
`94c87f28436e2ea8899c9a407e1f1413de893603` and exact terminal blocked record
`887160354c655de2a6806083febfc4c094c770cc`; generation 5 remains immutable.

This repair may change only `scripts/verify_full_ci.py` and its direct test
coverage. It must make the offline socket guard portable when `socket.AF_UNIX`
is unavailable while preserving loopback connections and rejecting external
network connections. It must not weaken egress isolation, change product
behavior, modify strategy/API/UI/data code, or introduce any further governance
mechanism. Stop after focused regression and clean delivery; any additional
root cause returns to the product owner.

The exact two-parent authorization record is
`eedbf129e4b69720bae95905114cdc56be87e7f2`. Generation 6 is now in progress;
all implementation, candidate, review and CI identities remain clear until a
new delivery is actually verified.

The fixed trend-signal and strategy engineer independently delivered the
bounded compatibility repair from exact base
`173a7ab33a0a1f0dac7612d633c3612ecfe72e5e` as
`44a6303b872c5aa09c6d77f3139fecf82f007d13`. Owner review accepted that exact
delivery: only `scripts/verify_full_ci.py` and
`tests/test_verify_full_ci.py` changed, the complete focused test file passed
29/29, status validation and Python compilation passed, the worktree and diff
were clean, and the secret scan found nothing. The repair uses a guarded
`getattr` for optional `AF_UNIX`, retains the existing loopback allowlist, and
continues to reject external addresses. Its isolated branch upload timed out
against GitHub port 443, so the delivery SHA is frozen as locally accepted and
pending remote readback; no rewrite or duplicate candidate is allowed. The
same exact change is integrated locally as `b658f4d`, pending the one complete
Generation-6 candidate validation. This acceptance is not candidate CI, merge,
closure, G2 authorization, or product completion.

Generation 6 has now completed its local delivery acceptance. Under exact
Python 3.12.10 and Node 24.14.0, the raw backend suite passed 620 tests with one
platform-only PowerShell skip in 3452.90 seconds; the mandatory transport suite
passed 6/6. The unified fail-closed offline entrypoint then collected and passed
all six transport tests, passed the complete four-worker suite with 620 passed
and one platform-only skip in 1120.68 seconds, reported no broken Python
requirements, accepted the exact offline npm tree, passed frontend 10/10 and
the production build, compiled scripts/tests, passed diff, fixture, secret and
forbidden-scope checks, and returned `FULL_CI_OK`. The independently listed
frontend 10/10 and production build also passed. A first preflight used the
host Python without locked API dependencies, and the first unified invocation
stopped after its already-green four-worker suite because the fresh worktree
lacked ignored `node_modules`; neither was a code failure. The exact locked
Python/Node runtimes and lock-identical local frontend dependencies were then
used for the successful acceptance above. The task advances only to
`awaiting_review`; exact remote CI, independent dual review, merge, closure,
G2 authorization and product work remain pending.

Generation-6 candidate `1cafee1bbbac41f4e69e9d90b38b6ec5891525cb`
is returned without rewrite. PR #40 run `33759026032` failed all eight platform
shards and aggregate `G0 / exact-head` at canonical-status validation before
installing dependencies or running product tests. The exact diagnostic is
`CURRENT_TASK state conflicts with canonical status`: this file's top-level
mirror remained `in_progress` while `PROJECT_STATUS.yaml` correctly declared
`awaiting_review`. Independent code/security returned `REQUEST_CHANGES`; the
technical architecture review remained clear on the `AF_UNIX` change, but the
candidate is route-blocked because its governed-document mirror is invalid.
The engineering repair, focused tests and full local acceptance remain valid.
Only the owner-maintained status mirror may be repaired next; no engineering,
strategy, API, UI, data, dependency, workflow or governance-rule change is
allowed.

## Generation 7 status-mirror-only repair

Generation 7 starts through the ordinary `returned -> in_progress` transition
from exact generation-6 return `358a8e195bcab9c4990630130acdf8fc7f33c0ec`.
It may only make the canonical current-state mirror in this document agree with
`PROJECT_STATUS.yaml` at delivery and record the resulting evidence. The
accepted `AF_UNIX` implementation and every code/test/dependency/workflow file
are frozen. Because no executable code changes, the already-green complete
local acceptance remains applicable; only canonical status validation,
document/diff scope, clean-worktree and secret checks are required before a new
delivery. Any other failure stops and returns this card.

Generation 7 delivery keeps every executable blob unchanged from the locally
accepted generation-6 implementation. The canonical status and this
document's top-level mirror now both declare `awaiting_review`. Targeted
validation is limited to the canonical validator, the exact changed-path set,
diff cleanliness, clean worktree and secret scan; the complete 620-test local
evidence remains bound to the unchanged executable tree. Remote exact-head CI
and both independent reviews must bind the new delivery before acceptance.

Generation-7 candidate `5c6ec94301713917dc27c58baab1ba702209beb9`
is returned unchanged. PR #40 run `33760692448` passed all four Ubuntu shards,
failed all four Windows shards, and correctly failed aggregate
`G0 / exact-head`. Windows shard 1 and shard 2 exposed remaining strict UTF-8
Git-output and LF/CRLF test-fixture call sites; shard 2 also proved that a
filesystem `chmod` cannot construct a Git executable-bit fixture on Windows.
Windows shard 0 and shard 3 exceeded the 15-minute verification-step limit,
showing that the real four-shard split remains unbalanced by execution cost.
Independent code/security returned `REQUEST_CHANGES` and architecture/route
returned `BLOCK`. The user has explicitly authorized a bounded continuation
that must not affect product behavior or expand governance. The failed
candidate, run, reviews, local acceptance, and successful Linux evidence remain
immutable; G2 and Signal V1 stay unauthorized.

## Generation 8 bounded Windows portability repair

Generation 8 starts through the ordinary `returned -> in_progress` transition
from exact return `74e685d15224f926f3cc04569618a55e16861af7`.
The product owner explicitly authorized continuation provided it remains
product-neutral and avoids governance expansion. This repair is therefore
limited to the remote evidence already bound by run `33760692448`:

- strict UTF-8 decoding at the remaining test Git subprocess boundary;
- deterministic UTF-8/LF schema and receipt fixtures, plus Git-index executable
  mode construction on Windows;
- deterministic redistribution or bounded parallelism for the existing four
  disjoint shards so each Windows job stays within the frozen time budget.

The first lane may change only `tests/test_g0_project_status.py`. The sharding
lane may change only `scripts/verify_full_ci.py`,
`tests/test_verify_full_ci.py`, and, only if a runner parameter is necessary,
`.github/workflows/g0-exact-head.yml`. No test may be deleted, skipped, weakened
or hidden; the total suite, strict UTF-8 failure, offline egress guard,
PowerShell exit propagation and four-shard completeness must remain fail
closed. No validator architecture, dependency, product, strategy, market, API,
UI, credential, order, deployment, release or G2 change is authorized.

### Generation 8 independent lane status

- `G1-G8-A` is independently accepted at exact delivery
  `250e09351d7d65a7640813dfd34b078f146f08e2`, based on exact start
  `53916bc751ff17e9d17ab4f2a43a9a24621809cb`. Only
  `tests/test_g0_project_status.py` changed. Owner verification passed six
  focused regressions, Python compilation, diff, scope, clean-worktree and
  secret checks. The first normal upload and a separate HTTP/1.1 remote
  readback both remained unresponsive and were stopped without rewriting the
  commit. This lane is frozen as locally accepted and pending upload; it does
  not block the independent sharding lane or local integration.
- `G1-G8-B` is independently accepted at exact delivery
  `50467f25e33c067e51fdda16007b9fff29dcd3f9`, also based on exact start
  `53916bc751ff17e9d17ab4f2a43a9a24621809cb`. Only
  `scripts/verify_full_ci.py` and `tests/test_verify_full_ci.py` changed. The
  four-way selection now sorts the complete node-ID collection and assigns it
  round-robin, producing actual counts `154/154/154/153` instead of
  `153/140/159/163` while remaining deterministic, disjoint and complete.
  Owner verification passed the full verifier test file 32/32, seven focused
  sharding tests, compilation, diff, scope, clean-worktree and secret checks.
  It did not modify the workflow or time limits. Because the GitHub upload
  channel is already known unavailable, this delivery is frozen in its own
  pending-upload record without a redundant attempt; Windows wall-clock proof
  remains a hosted-CI obligation.

### Generation 8 integrated delivery

The two independently accepted lanes are integrated without conflict at exact
implementation head `57595ef185e93e5c886144f17281f722b070f9dc`.
The one complete local acceptance under exact Python 3.12.10 and Node 24.14.0
passed the raw backend suite with 626 passed and one platform-only PowerShell
skip in 3321.73 seconds, mandatory transport 6/6, and the unified offline
entrypoint with the real four-worker suite at 626 passed and one platform-only
skip in 1037.64 seconds. Dependency integrity, frontend 10/10, production
build, compilation, canonical status, diff, fixture, secret and forbidden-scope
checks all passed, and the verifier returned `FULL_CI_OK`. The task advances
only to a clean local `awaiting_review` delivery. Exact hosted Windows CI,
independent candidate reviews, merge, G1 closure, G2 authorization and Signal
V1 product work remain unestablished.

Generation-8 candidate `549c7c51b5f1f27f261e053e49e9d39f0130a41f`
is returned without rewrite. PR #40 run `33774046518` passed Ubuntu 4/4,
failed Windows shard 0 with 7 failures and 150 passes, shard 2 with 8 failures
and 149 passes, shard 3 with 7 failures and 149 passes, cancelled Windows shard
1 after the fixed time envelope, and failed aggregate `G0 / exact-head`.
Remote logs bind the failures to a remaining default-locale `Path.read_text()`
call, inherited Windows `core.autocrlf` in temporary repositories, and
node-count rather than execution-cost shard balancing. Independent
code/security returned `REQUEST_CHANGES`; architecture/route returned `BLOCK`.
Both reviews classify the evidence within the already-authorized strict UTF-8,
clean CRLF fixture, and real four-shard categories, not a fourth root cause.
Only one minimal same-card repair may follow; product behavior and G2 remain
unauthorized.

## Generation 9 final same-card repair

Generation 9 starts through the ordinary `returned -> in_progress` transition
from exact generation-8 return
`3ac81d070d38b28c655c8eaaa825c672eaec3865`. Both independent reviews found no
fourth root cause. This final repair may only close the three remaining call
sites and mechanisms already evidenced by run `33774046518`:

- explicitly decode and write UTF-8/LF at the failing test-file boundary;
- explicitly set temporary Git repositories to `core.autocrlf=false`, except
  the dedicated clean-CRLF test that intentionally enables it;
- deterministically spread the identified slow governance tests across four
  complete, disjoint shards within the unchanged time budget.

Only `tests/test_g0_project_status.py`, `scripts/verify_full_ci.py`, and
`tests/test_verify_full_ci.py` may change. The workflow may change only if an
existing shard parameter must be passed; timeout increases are forbidden.
Tests may not be skipped, deleted, hidden or weakened. No dependency, validator
architecture, product, strategy, market, API, UI, credential, trading,
deployment, release or G2 change is authorized. Any fourth independent cause
or failure outside these three categories stops immediately.

### Conditional G2 product authorization

The product owner has conditionally authorized `G2-T01-C` for the signal
product and obsidian UI engineer. It activates only after G1 is legally closed
and the owner-maintained P1 Public DTO, Signal/Event, and PostgreSQL read
contracts are frozen. Its scope is Binance-only long-trend read-only Public
API, first-version REST polling, duration and history presentation, S/A lists,
load-more behavior, and responsive obsidian desktop/mobile UI. It may not
change strategy logic, shared contracts, database migrations or dependency
locks, and it may not add accounts, credentials, balances, leverage, orders or
real trading. Until both prerequisites are satisfied,
`PROJECT_STATUS.yaml.next_authorization` truthfully remains
`not_authorized`, and C may perform preparation only without product writes.

### Generation 9 independent lane acceptance

- `G1-G9-A` is independently accepted and frozen at delivery
  `cbab5695300ae7304bd55d45f65f376214334d3b`, based on
  `84142b88280ef76470981df6fcfb8796e67505b3`. Its only changed path is
  `tests/test_g0_project_status.py`. Owner review verified the exact parent and
  commit identity, clean worktree, strict UTF-8/LF repair, explicit temporary
  repository `core.autocrlf` behavior, intentional clean-CRLF exception,
  receipt-byte regression, scope, compilation and secret scan. The owner
  rerun passed 24 focused tests with 459 deselected. This acceptance does not
  establish integration, upload, hosted Windows CI, candidate acceptance or G1
  closure; the delivery remains frozen pending the independent cost-balanced
  four-shard lane.
- `G1-G9-B` is independently accepted and frozen at delivery
  `f4b377ed515d025fdc6693039dc200bfaa3596f3`, based on the same exact
  `84142b88280ef76470981df6fcfb8796e67505b3`. It changes only
  `scripts/verify_full_ci.py` and `tests/test_verify_full_ci.py`. Owner review
  verified deterministic weighted assignment, complete and disjoint real
  collection coverage, unchanged four-shard/time/security gates, commit and
  parent identity, compilation, scope, secrets and clean worktree. The owner
  rerun passed the verifier tests 33/33 and eight focused shard tests. This
  acceptance does not establish integration, upload, hosted Windows CI,
  candidate acceptance or G1 closure.

### Generation 9 terminal stop

The first integrated complete-validation attempt at exact head
`d3ed5fe5b1184b2b97762732bad3d084dcafc2cc` passed canonical status, the raw
backend suite with 628 passed and one platform-only skip, and Transport 6/6,
but the real four-worker suite had not finished after the fixed 15-minute
boundary and was stopped without a duplicate full-suite run. The original
four-shard lane then reported bounded repair
`557bc97598cedfa417b7df21e59171c9cef749ba`, based directly on that integrated
head. Owner review passed its 35 focused tests, exact two-file scope,
compilation, diff, clean-worktree and secret checks; architecture returned
`WATCH` because its internal 900-second budget lacks outer-step cleanup margin.

Independent code/security returned `REQUEST_CHANGES`: the timeout kills only
the direct subprocess and does not establish termination and reaping of
pytest-xdist or npm descendant process trees before the workflow restores its
OS egress policy. That is a new independent security root cause outside the
three final Generation-9 categories. The fourth-root rule therefore stops
G1-T01 as `blocked`. The delivery is not accepted or integrated, no formal
candidate was formed, no upload was attempted, and no further repair, G2 or
Signal V1 product write is authorized without a new product-owner decision.

## Generation 10 owner-autonomous process-tree repair authorization

The owner applied the approved autonomous-authorization rule after a read-only
diligence review of exact blocked record
`43b3d2b1a208237ab490c58f1a387ef4501c5e8f`. The ordered authorization parents
are authoritative close `94c87f28436e2ea8899c9a407e1f1413de893603`
and that exact blocked record. Exact two-parent authorization
`7286439386ba63080fa7aa1232b62591966b0bea` passed canonical validation; its
strict child starts only this bounded repair. This is a non-destructive, reversible,
product-neutral G1 repair within the existing Binance-only long/read-only
boundary and therefore does not require another user decision.

The original trend-signal and strategy engineer may change only
`scripts/verify_full_ci.py` and `tests/test_verify_full_ci.py` to:

- apply one unified deadline to the complete verifier entrypoint;
- terminate and reap the full descendant process tree, cross-platform, before
  OS egress policy restoration;
- decode captured subprocess output with explicit strict UTF-8 semantics; and
- add direct regressions proving the deadline, descendant cleanup/reaping and
  strict output-decoding behavior.

Timeout increases, skipped/deleted/weakened tests, dependency or workflow
changes, governance expansion, product/strategy/market/API/UI/database work,
credentials, accounts, orders, trading, deployment, release and G2 writes are
forbidden. Delivery must stop after focused tests, compilation, exact scope and
diff checks, secret scan and a clean worktree, then report for independent
review. Any further independent root cause outside this exact boundary stops
for owner reclassification under the same autonomous-authorization rule.

### Generation 10 independent repair acceptance

The trend-signal and strategy engineer's final second-repair delivery
`0ad96687386cc20676af4fca6446c9c6ca9e0671` is independently accepted and
frozen. It is based on exact Generation-10 start
`dae5d5f115560967ff2314af1462acfe117f2500` through preserved, non-rewritten
repair commits `95089106c44c6f2413263b9a1318fa6cbd18b59c` and
`0710d66c7ef1e35a1701768aa6404af8b4d1693b`. Only
`scripts/verify_full_ci.py` and `tests/test_verify_full_ci.py` changed.

Owner verification passed 43 focused tests with one Windows-only Job Object
test skipped on macOS, compilation, canonical status, exact scope, diff,
clean-worktree and secret checks. Independent code/security review returned
`APPROVE` after separately passing 10 focused tests with that same platform-only
skip. The accepted implementation gives the whole verifier one 14-minute
deadline, uses strict UTF-8 command output, keeps POSIX process-group cleanup,
and binds Windows commands to a kill-on-close Job Object before opening a gate
that can launch real descendants. Real Win32 and hosted-runner nested-Job
behavior remain mandatory hosted-Windows evidence; acceptance is not
integration, candidate CI, merge, closure, G2 or product authority.

### Generation 10 local-capacity repair acceptance

The trend-signal and strategy engineer's bounded performance delivery
`94c95c22aa9d484b7b873584be4414ae5eea6746`, directly based on accepted
process-tree delivery `0ad96687386cc20676af4fca6446c9c6ca9e0671`, is independently
accepted and frozen. Only `scripts/verify_full_ci.py` and
`tests/test_verify_full_ci.py` changed. An unsharded local complete validation
now defaults to the existing allowed maximum of eight workers, while explicit
worker settings remain authoritative and hosted four-shard CI continues to use
four workers per shard. The 14-minute deadline, test collection, shard count,
offline guard and process-tree cleanup are unchanged.

Owner verification passed 44 focused tests with one Windows-only Job Object
test skipped on macOS, compilation, diff, exact scope, clean-worktree and
secret checks. Independent review separately returned `APPROVE` after 11
focused passes with 34 deselected. This acceptance does not prove that the new
integrated SHA finishes the complete suite within the fixed deadline; exactly
one complete validation on that new SHA remains required. It is not upload,
hosted CI, merge, G1 closure, G2 or product authority.

### Generation 10 local-capacity repair 1 result and repair 2 authorization

The one complete validation of exact integrated head
`cf070357034000b0f46081e39af268c60471c4c4` passed canonical status and
Transport collection/execution 6/6, then failed closed because the unchanged
complete backend suite still exceeded the shared 14-minute deadline with eight
local workers. The verifier reaped its process tree, the worktree is clean,
and the same SHA will not be rerun. Dependency integrity, frontend tests/build,
compilation and final diff checks were not reached.

This is the first failed repair of the already-classified local-capacity/timing
root. Under the owner-autonomous authorization rule, a second and final
minimum-scope repair is authorized to the original trend-signal and strategy
engineer. It may change only `scripts/verify_full_ci.py` and
`tests/test_verify_full_ci.py`, must first bind the exact timing/resource cause,
and may improve only local complete-suite scheduling within the existing
2..8-worker, unchanged-test and 14-minute limits. Timeout increases, test
selection/skip/weakening, workflow/dependency changes, product/strategy work,
credentials, trading and governance expansion are forbidden. Delivery stops
after focused tests, scope/diff/secret/clean checks and must not run the full
suite. A second failure of this same root exhausts automatic repair and is
reported to the product owner rather than expanded again.

### Generation 10 local-capacity repair 2 acceptance

The trend-signal and strategy engineer's final same-root delivery
`7cf86242b6517ba0a8c2a7290e6f00a7e1de0e37`, directly based on
`94c95c22aa9d484b7b873584be4414ae5eea6746`, is independently accepted and
frozen. Only `scripts/verify_full_ci.py` and `tests/test_verify_full_ci.py`
changed. For the local unsharded complete run only, the plugin deterministically
orders the unchanged complete node set by descending historical cost and
nodeid so high-cost governance cases start first. Hosted multi-shard selection,
per-shard source order, cost hints, worker bounds, 14-minute deadline, command
set and cleanup/security gates remain unchanged.

Owner verification passed 44 focused tests with one Windows-only skip,
compilation, exact scope, diff, clean-worktree and secret checks. Independent
review returned `APPROVE` after 12 focused passes with 33 deselected. This is
accepted implementation evidence only; the next exact integrated SHA gets one
complete validation. If it fails for the same timing root, automatic repair is
exhausted and no further scheduling or timeout expansion is authorized.

### Generation 10 terminal timing result

The sole complete validation of exact integrated head
`743c8e4f2b8d422060784104c827af435f6fc4c5` passed canonical status,
Transport 6/6, the complete backend suite with 639 passed and two
platform-only skips in 677.74 seconds, Python dependency integrity, the exact
offline npm tree and frontend tests 10/10. The shared 14-minute deadline then
expired during the frontend production build and failed closed. The process
tree was reaped and the worktree remained clean; compilation and final diff
checks were not reached.

This is the second failed repair of the same local complete-validation timing
root, so automatic repair is exhausted. G1-T01 is `blocked`; no third timing
repair, timeout increase, candidate, upload, CI, G2 or Signal V1 product write
is authorized without a product-owner decision. All independently accepted
sub-deliveries and the successful portions of this run remain valid evidence.

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

Generation-4 implementation `fcaa7874ac7177949aaf08b53ce18a58d2cd3701`
closes only those three hosted-CI defects. The exact Python 3.12.10 raw suite
passed 611/611 in 3095.51 seconds; Transport passed 6/6; the unified offline
entrypoint passed canonical validation, Transport 6/6, the complete four-worker
suite 611/611 in 986.47 seconds, dependency integrity, frontend 10/10,
production build, compilation and diff checks. Delivery stops at
`awaiting_review`; hosted CI, independent reviews, merge, G2 and every product
capability remain unclaimed.

## Generation 13 hosted-CI stop

Frozen candidate `d0e7c9b494f67d5663f4eb3878ea0dd295106216` was uploaded by a
normal fast-forward to the existing PR #40 branch and exact remote readback
matched. Exact-head run `33837192832` passed all four Ubuntu shards and failed
all four Windows shards. Every Windows log contains the same fail-closed error
before test execution: the complete verifier attempted to emit Git diff output
containing Unicode character U+7684 through the runner's locale-dependent
`charmap` codec. Aggregate `G0 / exact-head` consequently failed.

This is a new hosted-Windows output-encoding root outside Generation 13's
environment-only retry. The explicit stop condition applies: no CI rerun,
repair, Generation 14, merge, G1 closure, P1 contract work, G2 Signal V1 or UI
implementation is authorized by this card. Local `FULL_CI_OK`, independent
code/security `APPROVE`, architecture/route `CLEAR`, successful upload and PR
identity remain valid but do not substitute for remote Windows CI.
