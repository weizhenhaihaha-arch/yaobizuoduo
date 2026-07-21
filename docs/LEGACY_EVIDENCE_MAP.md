# Legacy M0-M7 evidence map

## Scope and maturity ceiling

This map preserves reviewed historical evidence without upgrading it. Every entry
below is capped at `OFFLINE_EVIDENCE_ACCEPTED`. It is not evidence of remote
exact-HEAD CI, live exchange integration, continuous Paper validation, branch
protection, production monitoring, or release readiness.

| Legacy work | Traceable repository evidence | Preserved conclusion | Maturity |
| --- | --- | --- | --- |
| M0 | `M0_BOUNDARY_PROPOSAL.md`, `PRODUCT_SPEC.md`, evidence SHA `5582236139fa1e4f40b6c5d95967588a1d993aa4` | Product and strategy boundaries | `OFFLINE_EVIDENCE_ACCEPTED` |
| M1 | `contracts/M1_DATA_CONTRACT.md`, `fixtures/m1/`, `scripts/validate_m1_fixtures.ps1`, evidence SHA `e8a86524c827b2cc662850b94de8d6fadf299d6c` | Deterministic data contract and fixtures | `OFFLINE_EVIDENCE_ACCEPTED` |
| M2 | `adapters/read_only_market.py`, `tests/test_m2_adapters.py`, evidence SHA `33cf109522b1be9077dc2cd5c9041939ef15808b` | Pure read-only payload mapping boundary | `OFFLINE_EVIDENCE_ACCEPTED` |
| M3 | `strategy/lifecycle.py`, `tests/test_m3_lifecycle.py`, evidence SHA `75373269dc4e6d893d075db9674235ebe5be8735` | Deterministic provisional lifecycle | `OFFLINE_EVIDENCE_ACCEPTED` |
| M4 | `evaluation/replay.py`, `tests/test_m4_replay.py`, evidence SHA `d14e9c9f641b1a0873e2fe1c8d57ca503afcfd2b` | Availability-safe offline replay | `OFFLINE_EVIDENCE_ACCEPTED` |
| M5 | `api/`, `persistence/postgres_read_model.py`, `db/migrations/001_m5_read_model.sql`, M5 tests, evidence SHAs `4e64ab354afeb45b7e8bfd1387731abc4f49612e` and `fffc6f84ec497f69ee84c402e6f99ed19dc611ce` | Injected read-only API/storage boundaries | `OFFLINE_EVIDENCE_ACCEPTED` |
| M6 | `frontend/`, reviewed frontend tests, evidence SHA `d35045df65cb6011658a9c0f93a86ae212fccce5` | Deterministic fixture-backed beginner UI | `OFFLINE_EVIDENCE_ACCEPTED` |
| M7-T01 | `notifications/policy.py`, `tests/test_m7_notifications.py`, evidence SHA `db327b6e59cfd4edc23c22c308d01dfc59beab83` | Pure station-notification policy | `OFFLINE_EVIDENCE_ACCEPTED` |
| M7-T02 / L0 | `observability/health.py`, `tests/test_m7_operational_health.py`, candidate `c3a56bafb936d7e304ff87ae29174a14c998d919`, L0 closure `e2e0b489e1fbf555c4405f58ec1ab8d20f77199f` | Accepted under legacy local review | `OFFLINE_EVIDENCE_ACCEPTED` |

Historical wording such as “approved” means only the bounded local review recorded
at that time. G2 must certify each reusable item against its exact SHA and current
HEAD; this table does not perform that future certification.
