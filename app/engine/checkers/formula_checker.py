import re

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult
from app.models import Issue


FORMULA_RE = re.compile(r"\(\d+(?:\.\d+)*\)\s*$")


def check_formulas(document, context: CheckContext) -> CheckResult:
    issues = []
    formula_indexes = [
        index
        for index, paragraph in enumerate(document.paragraphs)
        if FORMULA_RE.search(paragraph.text.strip())
    ]
    if not formula_indexes:
        return CheckResult("formula_check", 1.0, WEIGHTS["formula_check"], issues)

    full_text = "\n".join(p.text for p in document.paragraphs)
    for index in formula_indexes:
        paragraph = document.paragraphs[index].text.strip()
        number = FORMULA_RE.search(paragraph).group(0).strip("()")
        if not re.search(rf"\bформул[аеуы]?\s*\(?{re.escape(number)}\)?", full_text, re.IGNORECASE):
            issues.append(Issue(
                rule_id="FORMULA_REFERENCE",
                paragraph_index=index,
                description=f"Не найдена ссылка в тексте на формулу ({number})",
                severity="warning",
                expected_value=f"Ссылка на формулу ({number})",
                auto_fixable=False,
            ))
        next_text = document.paragraphs[index + 1].text.strip().lower() if index + 1 < len(document.paragraphs) else ""
        if "где" not in next_text and any(symbol in paragraph for symbol in ("=", "+", "-", "·", "*")):
            issues.append(Issue(
                rule_id="FORMULA_WHERE",
                paragraph_index=index,
                description="После формулы не обнаружен блок 'где'",
                severity="warning",
                expected_value="Пояснение обозначений через блок 'где'",
                auto_fixable=False,
            ))
    return CheckResult("formula_check", 1.0 if not issues else 0.7, WEIGHTS["formula_check"], issues[:20])

