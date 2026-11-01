"""Safe YAML workflow loading and writing."""
from pathlib import Path
import yaml
from .models import Workflow


def load_workflow(path: Path) -> Workflow:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Workflow.model_validate(data)


def save_workflow(path: Path, workflow: Workflow) -> None:
    path.write_text(yaml.safe_dump(workflow.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
