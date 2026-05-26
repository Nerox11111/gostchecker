from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np

from app.ml.features import FEATURES, guess_doc_type


MODE_MAP = {
    "lab_work": "LIGHT",
    "practice": "LIGHT",
    "internship": "MEDIUM",
    "coursework": "MEDIUM",
    "thesis_bachelor": "HARD",
    "thesis_master": "HARD",
    "scientific_rpt": "HARD",
    "rnd_nir": "HARD",
}


@dataclass
class ClassificationResult:
    doc_type: str
    mode: str
    confidence: float
    needs_confirmation: bool


class DocumentClassifier:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.model = None
        self.le = None
        self.feats = FEATURES
        self.loaded = False
        if self.path.exists():
            data = joblib.load(self.path)
            self.model = data["model"]
            self.le = data["label_encoder"]
            self.feats = data["features"]
            self.loaded = True

    def predict(self, fvec: dict) -> ClassificationResult:
        if self.loaded and self.model is not None and self.le is not None:
            x = np.array([[fvec.get(feature, 0) for feature in self.feats]])
            proba = self.model.predict_proba(x)[0]
            idx = int(proba.argmax())
            confidence = float(proba[idx])
            doc_type = str(self.le.inverse_transform([idx])[0])
        else:
            doc_type = guess_doc_type(fvec)
            confidence = 0.6

        mode = MODE_MAP.get(doc_type, "LIGHT")
        return ClassificationResult(
            doc_type=doc_type,
            mode=mode,
            confidence=round(confidence, 3),
            needs_confirmation=confidence < 0.75,
        )

