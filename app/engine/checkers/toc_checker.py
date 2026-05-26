from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult
from app.models import Issue


def check_toc(document, context: CheckContext) -> CheckResult:
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    toc_indexes = [i for i, text in enumerate(paragraphs) if text.upper() == "СОДЕРЖАНИЕ"]
    if not toc_indexes:
        return CheckResult("toc_rebuild", 0.0, WEIGHTS["toc_rebuild"], [
            Issue(
                rule_id="TOC",
                description="Не найден раздел 'Содержание'",
                severity="error",
                expected_value="Содержание с отточиями и номерами страниц",
                auto_fixable=True,
            )
        ])
    start = toc_indexes[0]
    toc_block = paragraphs[start + 1:start + 12]
    has_page_numbers = any(text.rstrip().split(" ")[-1].isdigit() for text in toc_block)
    has_dot_leaders = any("..." in text or "…" in text for text in toc_block)
    issues = []
    if toc_block and not has_page_numbers:
        issues.append(Issue(
            rule_id="TOC_PAGE_NUMBERS",
            paragraph_index=start,
            description="В содержании не обнаружены номера страниц",
            severity="warning",
            expected_value="Номера страниц",
            auto_fixable=True,
        ))
    if toc_block and not has_dot_leaders:
        issues.append(Issue(
            rule_id="TOC_DOT_LEADERS",
            paragraph_index=start,
            description="В содержании не обнаружены отточия",
            severity="warning",
            expected_value="Отточия между заголовком и номером страницы",
            auto_fixable=True,
        ))
    return CheckResult("toc_rebuild", 1.0 if not issues else 0.6, WEIGHTS["toc_rebuild"], issues)

