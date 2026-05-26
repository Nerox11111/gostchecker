from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult
from app.models import Issue


def _footer_has_page_field(section) -> bool:
    xml = section.footer._element.xml
    text = "\n".join(p.text for p in section.footer.paragraphs)
    return "PAGE" in xml or any(char.isdigit() for char in text)


def check_page_numbering(document, context: CheckContext) -> CheckResult:
    issues: list[Issue] = []
    if not any(_footer_has_page_field(section) for section in document.sections):
        issues.append(Issue(
            rule_id="PAGE_NUMBERING",
            description="Не обнаружена нумерация страниц в нижнем колонтитуле",
            severity="warning",
            current_value="not found",
            expected_value="Арабские цифры в центре нижней части листа",
            auto_fixable=True,
        ))
        return CheckResult("page_numbering", 0.35, WEIGHTS["page_numbering"], issues)

    return CheckResult("page_numbering", 1.0, WEIGHTS["page_numbering"], issues)

