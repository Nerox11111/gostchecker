from dataclasses import dataclass, field
from typing import Any

from app.models import Issue


@dataclass
class CheckContext:
    features: dict[str, Any]
    mode: str


@dataclass
class CheckResult:
    rule_name: str
    score: float
    weight: float
    issues: list[Issue] = field(default_factory=list)


def clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))

