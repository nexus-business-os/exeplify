"""Command-line interface for the workflow specification foundation."""
from pathlib import Path
import typer
from pydantic import ValidationError
from .io import load_workflow, save_workflow
from .models import Stage, Workflow

app = typer.Typer(help="Expelify — structured, portable workflows.")


@app.command()
def init(path: Path = typer.Argument(Path("workflow.yaml"), help="New workflow file")):
    """Create an example workflow file without overwriting existing work."""
    if path.exists():
        typer.echo(f"File already exists: {path}", err=True)
        raise typer.Exit(1)
    if not path.parent.exists():
        typer.echo(f"Directory does not exist: {path.parent}", err=True)
        raise typer.Exit(1)
    workflow = Workflow(schema_version="0.1", name="example-workflow", description="A starter workflow", stages=[Stage(id="draft", instruction="Draft a short summary.", outputs=["summary.md"])])
    save_workflow(path, workflow)
    typer.echo(f"Created {path}")


@app.command()
def validate(path: Path = typer.Argument(..., help="Workflow YAML file")):
    """Validate schema and stage dependency graph."""
    try:
        workflow = load_workflow(path)
    except (OSError, ValueError, ValidationError) as exc:
        typer.echo(f"Invalid workflow: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Valid workflow: {workflow.name} ({len(workflow.stages)} stages)")


@app.command()
def inspect(path: Path = typer.Argument(..., help="Workflow YAML file")):
    """Display workflow stages and dependencies."""
    try:
        workflow = load_workflow(path)
    except (OSError, ValueError, ValidationError) as exc:
        typer.echo(f"Cannot inspect workflow: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"{workflow.name}: {workflow.description}")
    for stage in workflow.stages:
        typer.echo(f"- {stage.id} | depends on: {', '.join(stage.depends_on) or 'none'} | approval: {'yes' if stage.approval_required else 'no'}")


if __name__ == "__main__":
    app()
