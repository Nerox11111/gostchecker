from docx.shared import Mm

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult, clamp_score
from app.models import Issue


EXPECTED = {
    "left": Mm(30),
    "right": Mm(15),
    "top": Mm(20),
    "bottom": Mm(20),
}


def _mm(value) -> float:
    return round(value.mm, 1)


def check_margins(document, context: CheckContext) -> CheckResult:
    issues: list[Issue] = []
    violations = 0

    for section_index, section in enumerate(document.sections):
        actual = {
            "left": section.left_margin,
            "right": section.right_margin,
            "top": section.top_margin,
            "bottom": section.bottom_margin,
        }
        for name, expected in EXPECTED.items():
            if abs(actual[name] - expected) > Mm(3):
                violations += 1
                issues.append(Issue(
                    rule_id="MARGINS",
                    paragraph_index=None,
                    description=f"Поле страницы '{name}' не соответствует ГОСТ",
                    severity="error",
                    current_value=f"section {section_index + 1}: {_mm(actual[name])} mm",
                    expected_value=f"{_mm(expected)} mm",
                    auto_fixable=True,
                ))

    total = max(1, len(document.sections) * 4)
    score = clamp_score(1 - violations / total)
    return CheckResult("margins_check", score, WEIGHTS["margins_check"], issues)

