from pydantic import BaseModel, Field, constr
from typing import List
from openai.lib._pydantic import to_strict_json_schema

class Firm(BaseModel):
    name: str
    ticker: constr(strip_whitespace=True, to_upper=True) # type: ignore

class Project(BaseModel):
    project: str
    description: str
    market_value: float
    implementation_cost: float
    reasoning: str
    confidence: int
    similar_firms: List[Firm]
    priority: int
    priority_reasoning: str

class ProjectsPayload(BaseModel):
    projects: List[Project]


def create_response_format() -> dict:
    schema = to_strict_json_schema(ProjectsPayload)
    response_format = dict(
        type="json_schema",
        json_schema=dict(
            name=ProjectsPayload.__name__,
            strict=True,
            schema=schema
        )
    )
    return response_format

def create_json_schema() -> dict:
    """
    Create a JSON schema for the ProjectsPayload model.
    """
    return ProjectsPayload.model_json_schema()