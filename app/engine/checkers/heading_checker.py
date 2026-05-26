import re

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult, clamp_score
from app.models import Issue


HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+){0,2})(\.?)\s+\S+")


def _is_heading(paragraph) -> bool:
    style = (paragraph.style.name or "").lower()
    return "heading" in style or "заголов" in style or bool(HEADING_RE.match(paragraph.text.strip()))


def check_headings_numbering(document, context: CheckContext) -> CheckResult:
    issues = []
    heading_count = 0
    violations = 0

    for index, paragraph in enumerate(document.paragraphs):
        text = paragraph.text.strip()
        if not text or not _is_heading(paragraph):
            continue
        heading_count += 1
        match = HEADING_RE.match(text)
        if not match:
            violations += 1
            issues.append(Issue(
                rule_id="HEADING_NUMBERING",
                paragraph_index=index,
                description="Заголовок не имеет нумерации арабскими цифрами",
                severity="warning",
                current_value=text[:80],
                expected_value="1, 1.1 или 1.1.1 без точки в конце номера",
                auto_fixable=False,
            ))
            continue
        if match.group(2):
            violations += 1
            issues.append(Issue(
                rule_id="HEADING_NUMBERING",
                paragraph_index=index,
                description="После номера заголовка не должно быть точки",
                severity="error",
                current_value=match.group(0).split()[0],
                expected_value=match.group(1),
                auto_fixable=True,
            ))
        if paragraph.runs and not any(run.bold for run in paragraph.runs if run.text.strip()):
            violations += 1
            issues.append(Issue(
                rule_id="HEADING_BOLD",
                paragraph_index=index,
                description="Заголовок должен быть выделен полужирным",
                severity="warning",
                expected_value="bold",
                auto_fixable=True,
            ))

    score = 1.0 if heading_count == 0 else clamp_score(1 - violations / max(1, heading_count * 2))
    return CheckResult("headings_numbering", score, WEIGHTS["headings_numbering"], issues)


def check_bold_only_headings(document, context: CheckContext) -> CheckResult:
    issues = []
    bold_paragraphs = 0
    violations = 0
    for index, paragraph in enumerate(document.paragraphs):
        if not paragraph.text.strip():
            continue
        if any(run.bold for run in paragraph.runs if run.text.strip()):
            bold_paragraphs += 1
            if not _is_heading(paragraph):
                violations += 1
                issues.append(Issue(
                    rule_id="BOLD_ONLY_HEADINGS",
                    paragraph_index=index,
                    description="Полужирное начертание применено вне заголовка",
                    severity="warning",
                    current_value=paragraph.text[:80],
                    expected_value="Полужирный только для заголовков",
                    auto_fixable=False,
                ))
                if len(issues) >= 15:
                    break
    score = 1.0 if bold_paragraphs == 0 else clamp_score(1 - violations / bold_paragraphs)
    return CheckResult("bold_only_headings", score, WEIGHTS["bold_only_headings"], issues)

