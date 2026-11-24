# ADR 0005: Experiment reproducibility and publication

**Status:** Accepted principles; retention and publication details proposed.

## Context

Counterfactual results are meaningful only with known historical inputs, rules,
engine identity, generator settings and sampling limits. Reproducibility does
not imply representativeness.

## Decision

Persist immutable input revision, wire schema, exact native version/build ID,
requested and effective parameters (including seed), scope, requested/accepted
samples, attempts, native completion reason, baseline and aggregate results.
Retain enough metadata to replay a result under the same engine identity;
do not guarantee cross-build replay. Store null estimates for zero accepted
samples and mark incomplete seasons and partial batches explicitly.

Retain bounded individual calendar examples with their standings and origin.
The proposed initial cap is 20. Record whether examples are separately generated
or obtained from the actual batch via a verified selection contract. CLI v1's
`simulate` does not expose the complete sampled fixture lists; do not invent
sample provenance or infer it from a seed alone.

Published experiments expose authorized, consistently anonymized projections of
aggregates, examples and exports, not private source revisions. Define exact
anonymization rules, publication permissions, revocation and retention before
exposing real data. A public view must distinguish observed frequencies from
population probabilities and report limitations of the configured sampler.

## Consequences

Store results independently of the lifetime of queue messages or temporary files.
Preserve engine artifacts or record their availability limits. Do not overwrite
prior results on rerun, or change provenance when redacting a public projection.
Statistical interpretation follows the [CRD research methodology](https://github.com/AlessVolpe/CentralRankingDogma/blob/master/docs/research/methodology.md).
