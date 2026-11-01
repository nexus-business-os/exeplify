"""Canonical workflow data contracts (v0.1)."""
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Stage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_-]*$")
    instruction: str = Field(min_length=1)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(min_length=1)
    depends_on: list[str] = Field(default_factory=list)
    approval_required: bool = False


class Workflow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field(pattern=r"^0\.1$")
    name: str = Field(min_length=1)
    description: str = ""
    stages: list[Stage] = Field(min_length=1)

    @model_validator(mode="after")
    def check_dependencies(self):
        ids = [stage.id for stage in self.stages]
        if len(ids) != len(set(ids)):
            raise ValueError("stage IDs must be unique")
        known = set(ids)
        graph = {stage.id: stage.depends_on for stage in self.stages}
        for stage in self.stages:
            if len(stage.depends_on) != len(set(stage.depends_on)):
                raise ValueError(f"duplicate dependencies in stage '{stage.id}'")
            for dependency in stage.depends_on:
                if dependency not in known:
                    raise ValueError(f"unknown dependency '{dependency}' in stage '{stage.id}'")
                if dependency == stage.id:
                    raise ValueError(f"stage '{stage.id}' cannot depend on itself")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str):
            if node in visiting:
                raise ValueError("workflow contains a dependency cycle")
            if node in visited:
                return
            visiting.add(node)
            for parent in graph[node]:
                visit(parent)
            visiting.remove(node)
            visited.add(node)

        for node in ids:
            visit(node)
        return self
