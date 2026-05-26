from pathlib import Path
import random
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.ml.features import FEATURES


MODEL_PATH = Path("data/models/classifier.joblib")


TEMPLATES = {
    "lab_work": [5, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 8000, 120, 3],
    "practice": [7, 1, 0, 1, 0, 0, 1, 1, 1, 0, 2, 0, 1, 12000, 150, 3],
    "coursework": [25, 2, 1, 1, 0, 1, 1, 5, 4, 1, 18, 1, 1, 45000, 260, 4],
    "internship": [22, 2, 1, 1, 0, 1, 1, 8, 2, 0, 12, 2, 1, 38000, 230, 4],
    "thesis_bachelor": [60, 3, 1, 1, 1, 1, 1, 10, 8, 8, 45, 4, 1, 120000, 330, 5],
    "thesis_master": [75, 3, 1, 1, 1, 1, 1, 12, 10, 12, 60, 5, 1, 160000, 360, 5],
    "scientific_rpt": [45, 3, 1, 1, 1, 1, 1, 6, 6, 6, 35, 2, 1, 95000, 300, 5],
    "rnd_nir": [55, 3, 1, 1, 1, 1, 1, 8, 7, 10, 40, 3, 1, 110000, 320, 5],
}


def jitter(value, index):
    if index in {2, 3, 4, 5, 6, 12}:
        return value
    if isinstance(value, int):
        return max(0, value + random.randint(-max(1, value // 8), max(1, value // 8)))
    return max(0.0, value + random.uniform(-value * 0.08, value * 0.08))


def main() -> None:
    random.seed(42)
    rows = []
    labels = []
    for label, vector in TEMPLATES.items():
        for _ in range(40):
            rows.append([jitter(value, idx) for idx, value in enumerate(vector)])
            labels.append(label)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)
    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(pd.DataFrame(rows, columns=FEATURES).values, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "label_encoder": label_encoder, "features": FEATURES}, MODEL_PATH)
    print(f"bootstrap model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
