# Architecture decision records

An ADR records context, decision, consequences and implementation status. An
accepted decision defines the intended design, not proof that it is implemented.
Proposed decisions require confirmation or implementation-stage refinement.
Supersede accepted decisions with linked records when changing them.

| ADR | Decision | Status |
| --- | --- | --- |
| [0001](0001-system-architecture.md) | Application and native engine boundaries | Accepted direction; backend refined by 0006–0008 |
| [0002](0002-native-engine-integration.md) | JSON CLI v1 subprocess integration | Accepted boundary |
| [0003](0003-persistence-strategy.md) | Relational persistence and immutable revisions | Accepted principles; database resolved by 0006 |
| [0004](0004-background-processing.md) | Background experiment execution | Accepted direction; broker and recovery design proposed |
| [0005](0005-experiment-reproducibility.md) | Reproducibility, examples and publication | Accepted principles; implementation details proposed |
| [0006](0006-backend-stack.md) | Backend technology, PostgreSQL and Django upgrade policy | Accepted; implementation pending |
| [0007](0007-identity-and-authentication.md) | Custom identity, public registration and session authentication | Accepted; implementation pending |
| [0008](0008-rest-api.md) | RESTful API, OpenAPI and same-origin routing | Accepted; implementation pending |

Acceptance refers to the architectural direction established during project
planning. Unresolved decisions are explicitly marked and should not be treated
as finalized solely because they appear in these documents.
