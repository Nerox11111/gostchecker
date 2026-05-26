import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult, clamp_score
from app.models import Issue


def _texts(document) -> list[str]:
    return [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]


def check_title_page(document, context: CheckContext) -> CheckResult:
    first = "\n".join(_texts(document)[:12]).upper()
    signals = ["МИНИСТЕР", "УНИВЕРСИТЕТ", "КАФЕДРА", "РАБОТА", "СТУДЕНТ", "ПРЕПОДАВАТЕЛЬ"]
    hits = sum(1 for signal in signals if signal in first)
    issues = []
    if hits < 2:
        issues.append(Issue(
            rule_id="TITLE_PAGE",
            description="Титульный лист не распознан по типовым реквизитам",
            severity="warning",
            current_value=f"{hits} реквизита(ов)",
            expected_value="Вуз, кафедра, вид работы, студент/преподаватель",
            auto_fixable=False,
        ))
    return CheckResult("title_page", clamp_score(hits / 4), WEIGHTS["title_page"], issues)


def check_required_structure(document, context: CheckContext) -> CheckResult:
    upper = "\n".join(_texts(document)).upper()
    required = {
        "СОДЕРЖАНИЕ": "Содержание",
        "ВВЕДЕНИЕ": "Введение",
        "ЗАКЛЮЧЕНИЕ": "Заключение",
        "СПИСОК": "Список источников/литературы",
    }
    issues = []
    found = 0
    for marker, label in required.items():
        if marker in upper:
            found += 1
        else:
            issues.append(Issue(
                rule_id="STRUCTURE",
                description=f"Отсутствует обязательный раздел: {label}",
                severity="error",
                expected_value=label,
                auto_fixable=False,
            ))
    return CheckResult("structure_check", found / len(required), WEIGHTS["structure_check"], issues)


def check_abbreviations(document, context: CheckContext) -> CheckResult:
    text = "\n".join(_texts(document))
    abbreviations = sorted(set(re.findall(r"\b[А-ЯA-Z]{2,}\b", text)))
    has_section = "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ" in text.upper() or "СОКРАЩЕНИЯ" in text.upper()
    issues = []
    if len(abbreviations) >= 3 and not has_section:
        issues.append(Issue(
            rule_id="ABBREVIATIONS",
            description="Найдено 3+ сокращения, но не обнаружен перечень сокращений",
            severity="warning",
            current_value=", ".join(abbreviations[:10]),
            expected_value="Алфавитный перечень сокращений",
            auto_fixable=False,
        ))
        return CheckResult("abbreviations_check", 0.5, WEIGHTS["abbreviations_check"], issues)
    return CheckResult("abbreviations_check", 1.0, WEIGHTS["abbreviations_check"], issues)


def check_pdf_convertible(document, context: CheckContext) -> CheckResult:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return CheckResult("pdf_validation", 1.0, WEIGHTS["pdf_validation"], [
            Issue(
                rule_id="PDF_VALIDATION",
                description="LibreOffice CLI не найден, PDF-проверка пропущена",
                severity="info",
                current_value="missing soffice/libreoffice",
                expected_value="LibreOffice CLI",
                auto_fixable=False,
            )
        ])
    return CheckResult("pdf_validation", 1.0, WEIGHTS["pdf_validation"], [])


def check_appendices(document, context: CheckContext) -> CheckResult:
    texts = _texts(document)
    upper = [text.upper() for text in texts]
    appendix_indexes = [idx for idx, text in enumerate(upper) if text.startswith("ПРИЛОЖЕНИЕ")]
    if not appendix_indexes:
        return CheckResult("appendix_check", 1.0, WEIGHTS["appendix_check"], [])

    source_index = next((idx for idx, text in enumerate(upper) if "СПИСОК" in text and ("ИСТОЧ" in text or "ЛИТЕРАТ" in text)), None)
    issues = []
    if source_index is not None and any(idx < source_index for idx in appendix_indexes):
        issues.append(Issue(
            rule_id="APPENDIX_ORDER",
            description="Приложения должны располагаться после списка источников",
            severity="error",
            expected_value="После списка источников",
            auto_fixable=False,
        ))

    allowed = set("АБВГДЕЖИКЛМНПРСТУФХЦШЩЭЮЯ")
    for idx in appendix_indexes:
        match = re.match(r"ПРИЛОЖЕНИЕ\s+([А-Я])", upper[idx])
        if match and match.group(1) not in allowed:
            issues.append(Issue(
                rule_id="APPENDIX_LETTER",
                paragraph_index=idx,
                description="Приложение обозначено недопустимой буквой",
                severity="warning",
                current_value=match.group(1),
                expected_value="А-Я, кроме Ё, З, Й, О, Ч, Ъ, Ы, Ь",
                auto_fixable=False,
            ))

    return CheckResult("appendix_check", 0.6 if issues else 1.0, WEIGHTS["appendix_check"], issues)

