# Documentation

This documentation describes Fantacalcio Dummy System (FDS), the application
layer of the Fantacalcio counterfactual research project. It is the canonical
application reference; the native mathematical and algorithmic contracts remain
in [Central Ranking Dogma (CRD)](https://github.com/AlessVolpe/CentralRankingDogma/blob/master/docs/index.md).

**Status:** repository foundations complete (0.1.1); backend foundations (0.2.0)
are in progress. Django initialization and PostgreSQL persistence infrastructure
are present; public application features remain pending. The diagrams and
module names below describe the target design, not an inventory of existing
Python modules.

## Reading paths

| Audience | Documents |
| --- | --- |
| Developers | [System architecture](architecture/system.md), [backend foundations](architecture/backend.md), [module boundaries and logical data model](architecture/modules.md), [data flow](architecture/data-flow.md), [contributing](../CONTRIBUTING.md) |
| Researchers | [Research workflow and lifecycle](architecture/data-flow.md), [reproducibility](adr/0005-experiment-reproducibility.md), [CRD methodology](https://github.com/AlessVolpe/CentralRankingDogma/blob/master/docs/research/methodology.md) |
| Maintainers | [Architecture decision records](adr/README.md), [roadmap and milestone exit criteria](roadmap.md), [security policy](../SECURITY.md), [changelog](../CHANGELOG.md) |

## Documentation conventions

Separate established contracts, proposed design and implemented behavior. Update
current references and the roadmap together when a milestone changes. Record
significant architectural choices in ADRs; supersede rather than silently rewrite
accepted decisions. Link to the upstream native specification instead of copying
its mathematics or schemas into an independently drifting application reference.
