# Expelify

**Expelify** is a local-first Python project for transforming processes into structured, portable workflow specifications that compatible LLM harnesses can execute.

The long-term design supports both creating workflows from descriptions and converting existing automation workflows. It separates workflow structure and validation from model invocation, and aims to support structured knowledge through Google's Open Knowledge Format (OKF).

Manual processes and automation tools often mix instructions, dependencies, and runtime details. Expelify aims to make those contracts explicit in files that can be reviewed and reused across compatible harnesses.

## Current status

**Early foundation (v0.1).** The current implementation provides a YAML workflow schema, stage contracts, dependency validation, and a command-line interface. Transformation, OKF integration, and harness execution are planned, **not yet implemented**.

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

## Roadmap

1. Canonical workflow specification and validation (initial foundation)
2. Natural-language process transformation and compilation
3. OKF-compatible knowledge references
4. External LLM harness adapters and execution control
5. Existing-workflow conversion adapters
6. Approvals, history, reliability, and developer tooling

## Design principles

Local-first, inspectable files, explicit stage contracts, independent harness integrations, and human oversight. Expelify is not a model training project or a proprietary model runtime.

## Copyright and licensing

Copyright © 2026. All rights reserved.

Expelify is an independently owned, proprietary software project and is not open-source. The source code is publicly viewable, but no license to copy, modify, redistribute, or commercially use it is granted. Future commercial offerings may be made available under separate terms.
