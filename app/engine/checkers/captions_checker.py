import re

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult
from app.models import Issue


CAPTION_PATTERNS = {
    "TABLE": re.compile(r"^\s*Таблица\s+(\d+)\s+[—-]\s+\S+", re.IGNORECASE),
    "FIGURE": re.compile(r"^\s*Рисунок\s+(\d+)\s+[—-]\s+\S+", re.IGNORECASE),
}


def check_captions_sequence(document, context: CheckContext) -> CheckResult:
    issues = []
    for label, pattern in CAPTION_PATTERNS.items():
        numbers = []
        for index, paragraph in enumerate(document.paragraphs):
            match = pattern.match(paragraph.text.strip())
            if match:
                numbers.append((index, int(match.group(1))))
        if numbers:
            actual = [number for _, number in numbers]
            expected = list(range(1, len(numbers) + 1))
            if actual != expected:
                issues.append(Issue(
                    rule_id=f"{label}_CAPTION_SEQUENCE",
                    description="Нумерация подписей имеет пропуски или повторы",
                    severity="warning",
                    current_value=", ".join(map(str, actual)),
                    expected_value=", ".join(map(str, expected)),
                    auto_fixable=True,
                ))
    return CheckResult("captions_full", 1.0 if not issues else 0.75, WEIGHTS["captions_full"], issues)

