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


def workflow_data():
    return {"schema_version": "0.1", "name": "example", "stages": [
        {"id": "draft", "instruction": "Draft a report", "outputs": ["draft.md"]}
    ]}


@pytest.mark.parametrize("field", ["schema_version", "name", "stages"])
def test_required_workflow_fields(field):
    data = workflow_data()
    del data[field]
    with pytest.raises(ValidationError):
        Workflow.model_validate(data)


@pytest.mark.parametrize("change", [
    {"instruction": "  "}, {"outputs": []}, {"outputs": [" "]},
    {"inputs": [""]}, {"id": "Invalid ID"}, {"unexpected": True},
])
def test_incomplete_stage_contract(change):
    data = workflow_data()
    data["stages"][0].update(change)
    with pytest.raises(ValidationError):
        Workflow.model_validate(data)


def test_duplicate_stage_ids():
    data = workflow_data()
    data["stages"].append(dict(data["stages"][0]))
    with pytest.raises(ValidationError, match="stage IDs must be unique"):
        Workflow.model_validate(data)


def test_self_dependency():
    data = workflow_data()
    data["stages"][0]["depends_on"] = ["draft"]
    with pytest.raises(ValidationError, match="cannot depend on itself"):
        Workflow.model_validate(data)


def test_duplicate_dependencies():
    data = workflow_data()
    data["stages"].append({"id": "review", "instruction": "Review", "outputs": ["review.md"], "depends_on": ["draft", "draft"]})
    with pytest.raises(ValidationError, match="duplicate dependencies"):
        Workflow.model_validate(data)


def test_dependencies_can_reference_later_stages():
    data = workflow_data()
    data["stages"].insert(0, {"id": "review", "instruction": "Review", "outputs": ["review.md"], "depends_on": ["draft"]})
    assert len(Workflow.model_validate(data).stages) == 2


@pytest.mark.parametrize("command", ["validate", "inspect"])
@pytest.mark.parametrize("content", ["stages: [", "[]", "", "!!python/object:builtins.object {}"])
def test_cli_rejects_invalid_yaml_without_traceback(tmp_path, command, content):
    target = tmp_path / "bad.yaml"
    target.write_text(content, encoding="utf-8")
    result = runner.invoke(app, [command, str(target)])
    assert result.exit_code == 1
    assert "workflow:" in result.output
    assert "Traceback" not in result.output


@pytest.mark.parametrize("command", ["validate", "inspect"])
def test_cli_missing_file(tmp_path, command):
    result = runner.invoke(app, [command, str(tmp_path / "missing.yaml")])
    assert result.exit_code == 1
    assert "workflow:" in result.output


def test_cli_inspect_example():
    example = Path(__file__).resolve().parents[1] / "examples" / "workflow.yaml"
    result = runner.invoke(app, ["inspect", str(example)])
    assert result.exit_code == 0
    assert "content-review" in result.output
    assert "depends on: draft" in result.output
    assert "approval: yes" in result.output


def test_init_preserves_existing_file(tmp_path):
    target = tmp_path / "existing.yaml"
    target.write_text("keep this", encoding="utf-8")
    assert runner.invoke(app, ["init", str(target)]).exit_code == 1
    assert target.read_text() == "keep this"


def test_init_default_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert load_workflow(tmp_path / "workflow.yaml").name == "example-workflow"


def test_init_missing_parent(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path / "absent" / "workflow.yaml")])
    assert result.exit_code == 1
    assert "Directory does not exist" in result.output


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("init", "inspect", "validate"):
        assert command in result.output


def test_save_is_exclusive(tmp_path):
    from expelify.io import save_workflow
    target = tmp_path / "workflow.yaml"
    workflow = Workflow.model_validate(workflow_data())
    save_workflow(target, workflow)
    with pytest.raises(FileExistsError):
        save_workflow(target, workflow)
    assert load_workflow(target) == workflow
