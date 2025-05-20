from pydantic import BaseModel, Field, constr
from typing import List

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