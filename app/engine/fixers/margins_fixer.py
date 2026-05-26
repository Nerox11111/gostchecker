from docx.shared import Mm


def fix(document) -> list[dict]:
    patches = []
    for index, section in enumerate(document.sections):
        before = {
            "left": round(section.left_margin.mm, 1),
            "right": round(section.right_margin.mm, 1),
            "top": round(section.top_margin.mm, 1),
            "bottom": round(section.bottom_margin.mm, 1),
        }
        section.left_margin = Mm(30)
        section.right_margin = Mm(15)
        section.top_margin = Mm(20)
        section.bottom_margin = Mm(20)
        patches.append({
            "rule_id": "margins_check",
            "section_index": index,
            "before": before,
            "after": {"left": 30, "right": 15, "top": 20, "bottom": 20},
        })
    return patches

