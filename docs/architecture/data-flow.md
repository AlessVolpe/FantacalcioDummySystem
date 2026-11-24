# Research data flow and experiment lifecycle

**Status:** intended application behavior. Native operations are documented in
[CRD JSON CLI v1](https://github.com/AlessVolpe/CentralRankingDogma/blob/master/docs/integration/json-cli-v1.md).

```mermaid
sequenceDiagram
    participant U as User
    participant A as Application API
    participant D as Database
    participant W as Worker
    participant C as crd-json
    U->>A: Submit competition data
    A->>D: Persist editable competition
    U->>A: Request experiment
    A->>D: Freeze revision and create queued job
    A-->>U: Experiment identifier
    A->>W: Dispatch after transaction commits (via broker)
    W->>D: Claim attempt and read revision
    W->>C: validate / resolve / simulate as required
    C-->>W: Progress on stderr; final envelope on stdout
    W->>D: Atomically persist validated outcome
    U->>A: Read status and results
    A->>D: Authorized read
    A-->>U: Baseline, aggregates, retained examples
```

The native `simulate` response already contains an independently resolved
historical baseline; a separate `resolve` call is useful for baseline inspection,
not mandatory for every simulation. Native validation may accept original
resolution while rejecting alternative generation as unsupported.

## Proposed application states

| State | Meaning |
| --- | --- |
| `queued` | Persistent experiment exists and is eligible for dispatch |
| `running` | A worker owns an active attempt |
| `cancelling` | A cancellation request is recorded; worker must cooperate or terminate |
| `completed` | Valid native result with completed sampling |
| `partial` | Valid result with a non-completed native completion reason |
| `cancelled` | Cancelled without a usable native result |
| `failed` | No valid result was produced or persisted |

The application state is distinct from native `completion` (`completed`,
`attempt_limit`, `cancelled`, `uniqueness_memory_limit`). A cancellation that
returns a validated partial native result is `partial` with the native reason
preserved. A killed process without a response is not a successful zero-sample
simulation. A valid zero-accepted result retains null statistical estimates.

Publication is orthogonal to execution state. Publishing must not implicitly
rerun a simulation or expose a private revision. Retry creates another attempt
under the same immutable input; it must not overwrite a committed result.

## Research outputs

Basic results expose the baseline, observed first-place frequency, mean rank and
mean championship points. Advanced results expose rank counts and additional
native diagnostics where requested and available. Preserve the distinction
between requested and accepted samples; use the latter as the frequency
denominator. Provisional finalized-prefix results must remain labeled as such.

Retain aggregate statistics for the whole batch and a bounded selection of
individual calendars for inspection. The initial suggested maximum is 20 examples
per experiment, subject to review. CLI v1 does not return the simulated fixture
lists from `simulate`. A separately generated `generate`/`resolve` example must
be labeled as such, not described as a draw from the accepted simulation batch.
An actual sampled example requires a verified selection/retention contract.

The application must preserve replay metadata, enforce publication authorization,
and avoid inferring uniformity or independent draws from deterministic replay.
See [ADR 0004](../adr/0004-background-processing.md) and
[ADR 0005](../adr/0005-experiment-reproducibility.md).
