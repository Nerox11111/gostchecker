from pathlib import Path
import csv
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.ml.features import FEATURES, extract_features


RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/dataset.csv")


def main() -> None:
    if not RAW_DIR.exists():
        raise SystemExit(f"{RAW_DIR} does not exist")

    rows = []
    for class_dir in sorted(path for path in RAW_DIR.iterdir() if path.is_dir()):
        for docx_path in sorted(class_dir.glob("*.docx")):
            features = extract_features(docx_path)
            rows.append({
                "filepath": str(docx_path),
                "doc_type": class_dir.name,
                "is_gost_compliant": "",
                **features,
            })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["filepath", "doc_type", "is_gost_compliant", *FEATURES],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved {len(rows)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
