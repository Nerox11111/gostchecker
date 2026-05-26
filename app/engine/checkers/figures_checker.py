import re

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult, clamp_score
from app.models import Issue


FIGURE_CAPTION_RE = re.compile(r"^\s*Рисунок\s+(\d+(?:\.\d+)*)\s+[—-]\s+\S+", re.IGNORECASE)


def _figure_numbers(document) -> list[tuple[int, str]]:
    values = []
    for index, paragraph in enumerate(document.paragraphs):
        match = FIGURE_CAPTION_RE.match(paragraph.text.strip())
        if match:
            values.append((index, match.group(1)))
    return values


def _inline_shapes_count(document) -> int:
    return len(document.inline_shapes)


def check_images_basic(document, context: CheckContext) -> CheckResult:
    shapes = _inline_shapes_count(document)
    captions = _figure_numbers(document)
    issues = []
    if shapes > len(captions):
        issues.append(Issue(
            rule_id="FIGURE_CAPTION",
            description="Количество рисунков больше количества подписей 'Рисунок N - Название'",
            severity="error",
            current_value=f"figures={shapes}, captions={len(captions)}",
            expected_value="Подпись под каждым рисунком",
            auto_fixable=False,
        ))
    score = 1.0 if shapes == 0 else clamp_score(len(captions) / shapes)
    return CheckResult("images_basic", score, WEIGHTS["images_basic"], issues)


def check_images_full(document, context: CheckContext) -> CheckResult:
    captions = _figure_numbers(document)
    issues = []
    numeric = [(index, int(value)) for index, value in captions if "." not in value]
    if numeric:
        actual = [number for _, number in numeric]
        expected = list(range(1, len(numeric) + 1))
        if actual != expected:
            issues.append(Issue(
                rule_id="FIGURE_SEQUENCE",
                description="Нумерация рисунков не является последовательной",
                severity="warning",
                current_value=", ".join(map(str, actual)),
                expected_value=", ".join(map(str, expected)),
                auto_fixable=False,
            ))
    full_text = "\n".join(p.text for p in document.paragraphs)
    for _, number in captions:
        if not re.search(rf"\bрис(унок|\.)?\s*{re.escape(number)}\b", full_text, re.IGNORECASE):
            issues.append(Issue(
                rule_id="FIGURE_REFERENCE",
                description=f"Не найдена ссылка в тексте на рисунок {number}",
                severity="warning",
                expected_value=f"Ссылка на рисунок {number}",
                auto_fixable=False,
            ))
    return CheckResult("images_full", 1.0 if not issues else 0.7, WEIGHTS["images_full"], issues[:20])

