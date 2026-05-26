from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.ml.features import FEATURES


DATASET_PATH = Path("data/dataset.csv")
MODEL_PATH = Path("data/models/classifier.joblib")


def main() -> None:
    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=["doc_type"])
    if len(df) < 16:
        raise SystemExit("Need at least 16 labeled rows to train a useful model")

    x = df[FEATURES].fillna(0).values
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["doc_type"])

    stratify = y if min(pd.Series(y).value_counts()) >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    print(classification_report(y_test, model.predict(x_test), target_names=label_encoder.classes_))

    if min(pd.Series(y).value_counts()) >= 5:
        scores = cross_val_score(model, x, y, cv=5, scoring="f1_macro", n_jobs=-1)
        print(f"5-fold macro F1: mean={scores.mean():.3f}, std={scores.std():.3f}")
    else:
        print("5-fold macro F1 skipped: each class needs at least 5 examples")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "label_encoder": label_encoder, "features": FEATURES}, MODEL_PATH)
    print(f"saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
