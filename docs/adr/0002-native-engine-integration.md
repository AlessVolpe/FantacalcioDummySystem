# ADR 0002: Versioned JSON subprocess integration

**Status:** Accepted boundary; adapter implementation pending.

## Context

CRD supplies `crd-json` independently of the static C library. Direct bindings
would introduce native ABI, ownership and crash-handling concerns into Python.

## Decision

Use the [JSON CLI v1 contract](https://github.com/AlessVolpe/CentralRankingDogma/blob/master/docs/integration/json-cli-v1.md)
as the sole initial computation boundary. Invoke an explicitly configured,
trusted executable with an argument vector (no shell), one request per process,
UTF-8 JSON on stdin and one final response on stdout. Drain stderr independently
for optional progress. Enforce timeouts, size limits, process cleanup and trusted
output paths. Check exit codes, response schemas, request correlation and native
engine identity before persisting a result. Keep wire version `1.0` distinct
from the native package version and build ID.

## Consequences

Process isolation reduces ABI coupling but requires serialization, timeout and
error handling. Treat native structured errors and transport failures separately.
Replay generated calendars via the native effective generator recipe and sample
ordinal; arbitrary saved fixture lists are not accepted as alternative calendar
inputs. Pin an exact supported CRD artifact when integration begins, and verify
against real executable contract tests on Linux and Windows. The upstream
latest-release badge does not establish this pin.
