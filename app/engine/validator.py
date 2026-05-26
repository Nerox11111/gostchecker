from docx import Document

from app.engine.rules_config import RULES_CONFIG, WEIGHTS
from app.engine.score import ScoreAggregator
from app.engine.types import CheckContext, CheckResult
from app.engine.checkers import (
    captions_checker,
    figures_checker,
    font_checker,
    formula_checker,
    heading_checker,
    margins_checker,
    page_numbering_checker,
    structure_checker,
    tables_checker,
    toc_checker,
)
from app.models import Issue


CHECKERS = {
    "font_check": font_checker.check_font,
    "margins_check": margins_checker.check_margins,
    "indent_check": font_checker.check_indent,
    "page_numbering": page_numbering_checker.check_page_numbering,
    "title_page": structure_checker.check_title_page,
    "tables_basic": tables_checker.check_tables_basic,
    "images_basic": figures_checker.check_images_basic,
    "structure_check": structure_checker.check_required_structure,
    "headings_numbering": heading_checker.check_headings_numbering,
    "toc_rebuild": toc_checker.check_toc,
    "captions_full": captions_checker.check_captions_sequence,
    "tables_full": tables_checker.check_tables_full,
    "images_full": figures_checker.check_images_full,
    "bold_only_headings": heading_checker.check_bold_only_headings,
    "formula_check": formula_checker.check_formulas,
    "abbreviations_check": structure_checker.check_abbreviations,
    "pdf_validation": structure_checker.check_pdf_convertible,
    "appendix_check": structure_checker.check_appendices,
}


class DocumentValidator:
    def __init__(self) -> None:
        self.aggregator = ScoreAggregator()

    def validate(self, docx_path: str, features: dict, mode: str) -> tuple[float, list[Issue], list[CheckResult]]:
        mode = mode.upper()
        document = Document(docx_path)
        context = CheckContext(features=features, mode=mode)
        config = RULES_CONFIG.get(mode, RULES_CONFIG["LIGHT"])
        results: list[CheckResult] = []

        for rule_name, enabled in config.items():
            if not enabled:
                continue
            checker = CHECKERS.get(rule_name)
            if checker is None:
                continue
            result = checker(document, context)
            result.weight = WEIGHTS.get(rule_name, result.weight)
            results.append(result)

        issues = [issue for result in results for issue in result.issues]
        return self.aggregator.aggregate(results), issues, results

