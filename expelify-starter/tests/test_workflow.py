from pathlib import Path
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner
from expelify.cli import app
from expelify.io import load_workflow
from expelify.models import Workflow

runner = CliRunner()


def test_example_loads():
    workflow = load_workflow(Path(__file__).resolve().parents[1] / "examples" / "workflow.yaml")
    assert [stage.id for stage in workflow.stages] == ["draft", "review"]


def test_rejects_unknown_dependency():
    with pytest.raises(ValidationError, match="unknown dependency"):
        Workflow.model_validate({"schema_version": "0.1", "name": "bad", "stages": [{"id": "a", "instruction": "Do it", "outputs": ["x"], "depends_on": ["missing"]}]})


def test_rejects_cycle():
    with pytest.raises(ValidationError, match="dependency cycle"):
        Workflow.model_validate({"schema_version": "0.1", "name": "bad", "stages": [{"id": "a", "instruction": "A", "outputs": ["x"], "depends_on": ["b"]}, {"id": "b", "instruction": "B", "outputs": ["y"], "depends_on": ["a"]}]})


def test_cli_init_and_validate(tmp_path):
    target = tmp_path / "workflow.yaml"
    assert runner.invoke(app, ["init", str(target)]).exit_code == 0
    assert runner.invoke(app, ["validate", str(target)]).exit_code == 0
    assert runner.invoke(app, ["init", str(target)]).exit_code != 0


def test_cli_invalid(tmp_path):
    target = tmp_path / "invalid.yaml"
    target.write_text("stages: []", encoding="utf-8")
    assert runner.invoke(app, ["validate", str(target)]).exit_code != 0
