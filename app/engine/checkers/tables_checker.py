import re

from app.engine.rules_config import WEIGHTS
from app.engine.types import CheckContext, CheckResult, clamp_score
from app.models import Issue


TABLE_CAPTION_RE = re.compile(r"^\s*Таблица\s+(\d+(?:\.\d+)*)\s+[—-]\s+\S+", re.IGNORECASE)


def _table_caption_numbers(document) -> list[tuple[int, str]]:
    values = []
    for index, paragraph in enumerate(document.paragraphs):
        match = TABLE_CAPTION_RE.match(paragraph.text.strip())
        if match:
            values.append((index, match.group(1)))
    return values


def check_tables_basic(document, context: CheckContext) -> CheckResult:
    table_count = len(document.tables)
    captions = _table_caption_numbers(document)
    issues = []
    if table_count > len(captions):
        issues.append(Issue(
            rule_id="TABLE_CAPTION",
            description="Количество таблиц больше количества подписей 'Таблица N - Название'",
            severity="error",
            current_value=f"tables={table_count}, captions={len(captions)}",
            expected_value="Подпись над каждой таблицей слева",
            auto_fixable=False,
        ))
    score = 1.0 if table_count == 0 else clamp_score(len(captions) / table_count)
    return CheckResult("tables_basic", score, WEIGHTS["tables_basic"], issues)


def check_tables_full(document, context: CheckContext) -> CheckResult:
    captions = _table_caption_numbers(document)
    issues = []
    numeric = []
    for paragraph_index, value in captions:
        if "." not in value:
            numeric.append((paragraph_index, int(value)))
    if numeric:
        expected = list(range(1, len(numeric) + 1))
        actual = [number for _, number in numeric]
        if actual != expected:
            issues.append(Issue(
                rule_id="TABLE_SEQUENCE",
                description="Нумерация таблиц не является последовательной",
                severity="warning",
                current_value=", ".join(map(str, actual)),
                expected_value=", ".join(map(str, expected)),
                auto_fixable=False,
            ))

    for table_index, table in enumerate(document.tables):
        if len(table.rows) > 1 and all(not cell.text.strip() for cell in table.rows[0].cells):
            issues.append(Issue(
                rule_id="TABLE_HEADER",
                description="В первой строке таблицы не обнаружены заголовки колонок",
                severity="warning",
                current_value=f"table {table_index + 1}",
                expected_value="Строка заголовков/номеров колонок",
                auto_fixable=False,
            ))
    return CheckResult("tables_full", 1.0 if not issues else 0.65, WEIGHTS["tables_full"], issues)

