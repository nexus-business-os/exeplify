# Expelify

**Expelify** is a local-first Python project for transforming processes into structured, portable workflow specifications that compatible LLM harnesses can execute.

The long-term design supports both creating workflows from descriptions and converting existing automation workflows. It separates workflow structure and validation from model invocation, and aims to support structured knowledge through Google's Open Knowledge Format (OKF).

## Current status

**Early foundation (v0.1).** The current implementation provides a YAML workflow schema, stage contracts, dependency validation, and a command-line interface. Transformation, OKF integration, and harness execution are planned, **not yet implemented**.

## Requirements

- Python 3.12+

## Installation

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\\Scripts\\Activate.ps1
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

## Workflow format

A workflow is a YAML document containing a schema version, name, and stages. Each stage specifies an instruction, output artifacts, optional input artifacts, dependencies, and whether human approval is required. Stage dependencies must refer to existing stages and cannot contain cycles. See [`examples/workflow.yaml`](examples/workflow.yaml).

## Roadmap

1. Canonical workflow specification and validation (initial foundation)
2. Natural-language process transformation and compilation
3. OKF-compatible knowledge references
4. External LLM harness adapters and execution control
5. Existing-workflow conversion adapters
6. Approvals, history, reliability, and developer tooling

## Design principles

Local-first, inspectable files, explicit stage contracts, independent harness integrations, and human oversight. Expelify is not a model training project or a proprietary model runtime.

## License

MIT. See [LICENSE](LICENSE).
