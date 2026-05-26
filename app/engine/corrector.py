from pathlib import Path

from docx import Document

from app.engine.fixers import captions_fixer, font_fixer, heading_fixer, margins_fixer, page_numbering_fixer, toc_rebuilder


FIXERS = {
    "font_check": font_fixer.fix,
    "FONT_NAME": font_fixer.fix,
    "FONT_SIZE": font_fixer.fix,
    "ALIGNMENT": font_fixer.fix,
    "LINE_SPACING": font_fixer.fix,
    "indent_check": font_fixer.fix,
    "INDENT": font_fixer.fix,
    "margins_check": margins_fixer.fix,
    "MARGINS": margins_fixer.fix,
    "page_numbering": page_numbering_fixer.fix,
    "PAGE_NUMBERING": page_numbering_fixer.fix,
    "headings_numbering": heading_fixer.fix,
    "HEADING_NUMBERING": heading_fixer.fix,
    "HEADING_BOLD": heading_fixer.fix,
    "toc_rebuild": toc_rebuilder.fix,
    "TOC": toc_rebuilder.fix,
    "TOC_PAGE_NUMBERS": toc_rebuilder.fix,
    "TOC_DOT_LEADERS": toc_rebuilder.fix,
    "captions_full": captions_fixer.fix,
    "TABLE_CAPTION_SEQUENCE": captions_fixer.fix,
    "FIGURE_CAPTION_SEQUENCE": captions_fixer.fix,
}


class DocumentCorrector:
    def apply(self, orig_path: Path, fixed_path: Path, apply_rules: list[str]) -> list[dict]:
        document = Document(str(orig_path))
        patches: list[dict] = []
        seen_fixers = set()
        for rule_id in apply_rules:
            fixer = FIXERS.get(rule_id)
            if fixer is None or fixer in seen_fixers:
                continue
            seen_fixers.add(fixer)
            patches.extend(fixer(document))
        fixed_path.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(fixed_path))
        return patches

