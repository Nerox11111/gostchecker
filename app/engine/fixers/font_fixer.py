from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt


def fix(document) -> list[dict]:
    patches = []
    normal_style = document.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(14)

    for index, paragraph in enumerate(document.paragraphs):
        if not paragraph.text.strip():
            continue
        before = {
            "alignment": str(paragraph.alignment),
            "line_spacing": str(paragraph.paragraph_format.line_spacing),
            "first_line_indent": str(paragraph.paragraph_format.first_line_indent),
        }
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.line_spacing = 1.5
        paragraph.paragraph_format.first_line_indent = Cm(1.25)
        for run in paragraph.runs:
            if run.text.strip():
                run.font.name = "Times New Roman"
                if run.font.size is None or run.font.size.pt < 12:
                    run.font.size = Pt(14)
        patches.append({
            "rule_id": "font_check",
            "paragraph_index": index,
            "before": before,
            "after": "Times New Roman, >=12pt, justify, 1.5 spacing, 1.25 cm indent",
        })
    return patches

