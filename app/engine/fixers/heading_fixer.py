import re


HEADING_RE = re.compile(r"^(\s*\d+(?:\.\d+){0,2})\.\s+")


def fix(document) -> list[dict]:
    patches = []
    for index, paragraph in enumerate(document.paragraphs):
        text = paragraph.text
        if not text.strip():
            continue
        before = text
        if HEADING_RE.match(text):
            paragraph.text = HEADING_RE.sub(r"\1 ", text)
            for run in paragraph.runs:
                run.bold = True
            patches.append({
                "rule_id": "headings_numbering",
                "paragraph_index": index,
                "before": before,
                "after": paragraph.text,
            })
        elif re.match(r"^\s*\d+(?:\.\d+){0,2}\s+\S+", text):
            for run in paragraph.runs:
                run.bold = True
            patches.append({
                "rule_id": "headings_numbering",
                "paragraph_index": index,
                "before": "not bold",
                "after": "bold",
            })
    return patches

