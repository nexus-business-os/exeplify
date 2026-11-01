# Expelify

**Turn complex workflows into structured, executable intelligence.**

Expelify is an independently owned, local-first workflow transformation and execution platform in early development. It is designed to convert complex, unstructured, or existing workflows into portable, human-readable specifications that compatible LLMs can execute through existing harnesses.

The core idea is to separate workflow definition and control from the intelligence used to perform individual tasks. Expelify defines the structure, contracts, context boundaries, dependencies, handoffs, validation, and approval process. An external harness supplies model invocation, tools, and execution permissions.

The long-term goal is to let organizations define a process once, inspect and version its specification, and execute it through compatible systems without coupling the process to one model provider or agent framework.

## The problem

Business logic, context, prompts, integrations, and execution rules are often tightly coupled inside automation systems. This makes processes difficult to inspect, change, and move between tools. Context can be scattered, dependencies implicit, and intermediate results difficult to review or correct.

Expelify aims to make those boundaries explicit through readable files, scoped context, declared inputs and outputs, and human review at important stages. Initial work prioritizes sequential, reviewable business processes.

## Current status

**Early foundation (v0.1).** This repository currently provides:

- A Python CLI with `init`, `inspect`, and `validate` commands.
- A YAML workflow schema with explicit stage instructions, inputs, outputs, dependencies, and approval metadata.
- Validation of required fields, nonblank contracts, unique stage identifiers, dependency references, and dependency cycles.
- Safe initialization, a document review example, regression tests, and GitHub Actions CI.

Workflow transformation, compilation, OKF integration, harness execution, enforced approval gates, and execution records are **planned, not implemented**. The current schema is an initial foundation for the fuller workflow specification.

## Intended workflow lifecycle

The planned product supports both **workflow creation** from natural-language descriptions and documents, and **workflow conversion** from supported automation or agent configurations.

1. **Ingest:** accept a process description, documented procedure, or supported workflow configuration.
2. **Transform:** identify objectives, stages, inputs, outputs, dependencies, decision points, and human intervention requirements.
3. **Compile:** produce readable workflow files, explicit stage contracts, knowledge references, and OKF-compatible knowledge bundles.
4. **Validate:** check completeness, contracts, dependencies, declared execution requirements, and expected outputs before execution.
5. **Execute through a harness:** provide each stage with scoped context and coordinate execution through a compatible external LLM harness.
6. **Review and record:** validate outputs, pause for approvals, and preserve artifacts, provenance, decisions, and execution history.

Transformation must flag ambiguous, unsupported, or underspecified steps for human clarification. It must not invent missing requirements or assume every arbitrary workflow can be converted automatically.

## Architectural direction

Transformation and execution are separate concerns. A generated workflow should be inspectable, editable, versionable, exportable, and validatable before it is executed. The architecture is intended to remain local-first, filesystem-based, modular, and provider-independent.

The planned architecture has seven subsystems; these are responsibilities to develop rather than a list of existing packages.

| Subsystem | Responsibility |
| --- | --- |
| Workflow ingestion | Accept and normalize supported workflow sources. |
| Transformation engine | Decompose processes and compile explicit workflow definitions. |
| Workflow specification | Define portable stage contracts, metadata, references, dependencies, and output conventions. |
| Knowledge layer | Organize and reference reusable OKF-compatible knowledge separately from working artifacts. |
| Validation engine | Check workflow structure, contracts, dependencies, and execution constraints. |
| Execution control | Coordinate external harnesses, scoped context, stage state, output checks, and approval checkpoints. |
| Traceability engine | Record decisions, provenance, configuration, artifact hashes, and execution history. |

### Methodological inspiration and knowledge compatibility

Interpretable Context Methodology (ICM) and Model Workspace Protocol (MWP) inform the filesystem-based direction: explicit stage contracts, scoped context, file-based handoffs, inspectable intermediate results, and separation of stable reference material from changing working artifacts. These principles do not require a separate agent for every stage.

Google's Open Knowledge Format (OKF) is the intended compatibility target for reusable knowledge documents, metadata, relationships, and provenance. Expelify's workflow specification will remain separate and reference knowledge bundles rather than redefine their format. Compatibility will follow the published OKF specification, with Expelify-specific extensions versioned separately. No OKF compatibility is claimed for the current implementation.

Expelify is an independent implementation. Its initial execution direction uses external harnesses; a native execution runtime is outside the current foundation.

## Requirements

- Python 3.12+

## Installation

From the repository root:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
```

## Quick start

```bash
expelify init workflow.yaml
expelify inspect workflow.yaml
expelify validate workflow.yaml
expelify validate examples/workflow.yaml
python -m pytest -q
```

`init` defaults to `workflow.yaml`, refuses to overwrite any existing file, and requires the destination directory to exist. `validate` and `inspect` return exit code 1 with an error message for invalid or unreadable files. Approval flags are metadata; this milestone does not execute stages or enforce approval gates.

## Workflow format

A workflow is a YAML document containing a schema version, name, and stages. Each stage specifies an instruction, output artifacts, optional input artifacts, dependencies, and whether human approval is required. Stage dependencies must refer to existing stages and cannot contain cycles. See [`examples/workflow.yaml`](examples/workflow.yaml).

```yaml
schema_version: '0.1'
name: content-review
description: Draft and review a document from a business brief.
stages:
  - id: draft
    instruction: Write a first draft based on the supplied brief.
    inputs: [brief.md]
    outputs: [draft.md]
  - id: review
    instruction: Review the draft for clarity and completeness.
    inputs: [draft.md]
    outputs: [review.md]
    depends_on: [draft]
    approval_required: true
```

Instructions, workflow names, and artifact references must be nonblank. Each stage needs at least one output. Artifact names declare contracts; validation does not require those files to exist. Dependencies can reference stages anywhere in the document; inspection displays document order rather than an execution schedule.

## Development and architecture

Run `python -m pytest -q` after installing the development dependencies. CI runs the tests and CLI smoke checks on Python 3.12, 3.13, and 3.14.

- `src/expelify/models.py`: canonical Pydantic contracts and dependency graph validation.
- `src/expelify/io.py`: safe YAML parsing and exclusive file creation.
- `src/expelify/cli.py`: file-oriented commands and user-facing errors.
- `tests/`: model, parsing, and CLI regression coverage.
- `examples/`: a portable document review workflow.

Future transformation and harness adapters should consume the canonical workflow models, keeping parsing and validation independent of model invocation. Knowledge references and execution records will be designed in later milestones.

## Implementation roadmap

The existing v0.1 foundation establishes packaging, a basic schema, parsing, validation, and CLI commands. The next milestones develop that foundation toward a complete workflow lifecycle:

1. **Workflow specification:** document workflow structure, stage contracts, metadata, knowledge references, dependencies, and output conventions. Deliver a written specification and example bundles.
2. **Filesystem parser and validator:** evolve the current parser and validator against the documented specification, including contract checks and dependency resolution.
3. **Workflow transformation:** convert documented processes into structured workflow files through an initial compiler with human review.
4. **Harness integration:** define a generic execution interface and execute a validated workflow through the first compatible external harness.
5. **Traceability and reliability:** add enforced approval gates, execution records, provenance, artifact hashing, recovery, and end-to-end verification.

### Target MVP

The intended MVP demonstrates one carefully selected business process from documentation to reviewed results: transform it into structured files, reference reusable OKF-compatible knowledge, validate its contracts and execution order, execute through a compatible harness, validate outputs, pause for human approval, and record the resulting artifacts.

This end-to-end lifecycle is a development target, not a capability of the current release. Broad source connectors and highly concurrent autonomous orchestration are outside the initial MVP.

## Commercial direction

Expelify targets enterprise organizations, beginning with a local-first Python CLI and a longer-term hybrid product direction. The following are planned capabilities, not available editions or committed offerings:

| Direction | Intended capabilities |
| --- | --- |
| Local | Workflow transformation, validation, filesystem-based execution, knowledge bundles, harness integrations, and local history. |
| Hosted / Professional | Visual workflow management, centralized storage, hosted execution, sharing, and team collaboration. |
| Enterprise | Organizational governance, role-based permissions, auditability, managed deployment, private infrastructure, and enterprise integrations. |

## Copyright and licensing

Copyright © 2026. All rights reserved.

Expelify is an independently owned, proprietary software project and is not open-source. The source code is publicly viewable, but no license to copy, modify, redistribute, or commercially use it is granted. Future commercial offerings may be made available under separate terms.
