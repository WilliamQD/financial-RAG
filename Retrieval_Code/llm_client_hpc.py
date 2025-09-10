# llm_client.py  hpc version

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError
from openai import OpenAI
import re

# ── Configure your local server here ───────────────────────────────────────────
BASE_URL = "http://localhost:8000/v1"   # transformers serve endpoint
API_KEY  = "not-needed"                  # server ignores it; SDK needs a string
MODEL_ID = "openai/gpt-oss-20b"         # default model; override per-call if needed
# ───────────────────────────────────────────────────────────────────────────────

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def responses_create_text(
    *,
    model: str = MODEL_ID,
    messages: List[Dict[str, Any]],
    temperature: float = 0.0,
    max_output_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, Any]] = None,
    reasoning: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Call /v1/responses and return the model's output_text.
    """
    resp = client.responses.create(
        model=model,
        input=messages,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_format=response_format,
        reasoning=reasoning,
    )
    return resp.output_text.strip()

def responses_parse_local(
    *,
    model: str = MODEL_ID,
    messages: List[Dict[str, Any]],
    schema_model: Type[BaseModel],
    temperature: float = 0.0,
    max_output_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, Any]] = None,
    reasoning: Optional[Dict[str, Any]] = None,
) -> BaseModel:
    """
    Drop-in replacement for client.responses.parse(..., text_format=schema_model)
    using /v1/responses and client-side Pydantic validation.
    """
    text = responses_create_text(
        model=model,
        messages=messages,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_format=response_format,   # e.g., your json_schema helper
        reasoning=reasoning,
    )

    # Try strict parse first
    try:
        return schema_model.model_validate_json(text)
    except Exception:
        # Fallback: extract first JSON object if the model wrapped it
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            raise ValidationError([f"Model did not return JSON:\n{text[:600]}"], schema_model)
        return schema_model.model_validate_json(m.group(0))
