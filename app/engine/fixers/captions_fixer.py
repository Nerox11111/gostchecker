import re


def _renumber(document, label: str) -> list[dict]:
    patches = []
    pattern = re.compile(rf"^(\s*{label}\s+)(\d+)(\s+[—-]\s+\S+.*)$", re.IGNORECASE)
    number = 1
    for index, paragraph in enumerate(document.paragraphs):
        text = paragraph.text
        match = pattern.match(text)
        if not match:
            continue
        new_text = f"{match.group(1)}{number}{match.group(3)}"
        if new_text != text:
            paragraph.text = new_text
            patches.append({
                "rule_id": "captions_full",
                "paragraph_index": index,
                "before": text,
                "after": new_text,
            })
        number += 1
    return patches


def fix(document) -> list[dict]:
    return _renumber(document, "Таблица") + _renumber(document, "Рисунок")

