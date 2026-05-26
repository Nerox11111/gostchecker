from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult, clamp_score
from app.models import Issue


def _effective_size_pt(run, paragraph) -> float | None:
    size = run.font.size or paragraph.style.font.size
    return float(size.pt) if size is not None else None


def _effective_font_name(run, paragraph) -> str | None:
    return run.font.name or paragraph.style.font.name


def check_font(document, context: CheckContext) -> CheckResult:
    issues: list[Issue] = []
    checked = 0
    violations = 0

    for index, paragraph in enumerate(document.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue
        checked += 4
        paragraph_bad = False

        names = {
            name
            for run in paragraph.runs
            if run.text.strip()
            for name in [_effective_font_name(run, paragraph)]
            if name
        }
        if names and any(name.lower() != "times new roman" for name in names):
            violations += 1
            paragraph_bad = True
            issues.append(Issue(
                rule_id="FONT_NAME",
                paragraph_index=index,
                description="Шрифт отличается от Times New Roman",
                severity="error",
                current_value=", ".join(sorted(names)),
                expected_value="Times New Roman",
                auto_fixable=True,
            ))

        sizes = [
            size
            for run in paragraph.runs
            if run.text.strip()
            for size in [_effective_size_pt(run, paragraph)]
            if size is not None
        ]
        if sizes and min(sizes) < 12:
            violations += 1
            paragraph_bad = True
            issues.append(Issue(
                rule_id="FONT_SIZE",
                paragraph_index=index,
                description="Размер шрифта меньше 12pt",
                severity="error",
                current_value=f"{min(sizes):.1f}pt",
                expected_value=">=12pt",
                auto_fixable=True,
            ))

        if paragraph.alignment not in (None, WD_ALIGN_PARAGRAPH.JUSTIFY):
            violations += 1
            paragraph_bad = True
            issues.append(Issue(
                rule_id="ALIGNMENT",
                paragraph_index=index,
                description="Абзац не выровнен по ширине",
                severity="warning",
                current_value=str(paragraph.alignment),
                expected_value="justify",
                auto_fixable=True,
            ))

        line_spacing = paragraph.paragraph_format.line_spacing
        if line_spacing is not None and abs(float(line_spacing) - 1.5) > 0.05:
            violations += 1
            paragraph_bad = True
            issues.append(Issue(
                rule_id="LINE_SPACING",
                paragraph_index=index,
                description="Межстрочный интервал отличается от полуторного",
                severity="warning",
                current_value=str(line_spacing),
                expected_value="1.5",
                auto_fixable=True,
            ))

        if paragraph_bad and len(issues) >= 25:
            break

    score = 1.0 if checked == 0 else clamp_score(1 - violations / checked)
    return CheckResult("font_check", score, WEIGHTS["font_check"], issues)


def check_indent(document, context: CheckContext) -> CheckResult:
    issues: list[Issue] = []
    checked = 0
    violations = 0
    expected = Cm(1.25)

    for index, paragraph in enumerate(document.paragraphs):
        if not paragraph.text.strip():
            continue
        checked += 1
        indent = paragraph.paragraph_format.first_line_indent
        if indent is None:
            continue
        if abs(indent - expected) > Cm(0.2):
            violations += 1
            issues.append(Issue(
                rule_id="INDENT",
                paragraph_index=index,
                description="Абзацный отступ отличается от 1,25 см",
                severity="warning",
                current_value=f"{indent.cm:.2f} cm",
                expected_value="1.25 cm",
                auto_fixable=True,
            ))
            if len(issues) >= 20:
                break

    score = 1.0 if checked == 0 else clamp_score(1 - violations / checked)
    return CheckResult("indent_check", score, WEIGHTS["indent_check"], issues)

