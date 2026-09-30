"""Respuestas compartidas. Page[T] se agrega con los listados."""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
