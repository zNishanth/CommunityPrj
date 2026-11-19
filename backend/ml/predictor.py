"""
ML Predictor — loads the trained model once and exposes `predict(url)`.
Supports both .pkl (pickle) and .joblib model formats.
"""
import os
import pickle
import logging
from pathlib import Path
from typing import Tuple

import numpy as np

from .feature_extraction import extract_features, FEATURE_NAMES

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "phishing_rf_model.pkl"   # default; override via env
_CACHED_MODEL = None


def _load_model():
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    model_path = Path(os.getenv("PHISH_MODEL_PATH", str(MODEL_PATH)))
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Train the model using the Colab notebook and place the .pkl file here."
        )

    suffix = model_path.suffix.lower()
    if suffix == ".joblib":
        from joblib import load as joblib_load
        _CACHED_MODEL = joblib_load(model_path)
    else:
        with open(model_path, "rb") as f:
            _CACHED_MODEL = pickle.load(f)

    logger.info("Phishing model loaded from %s", model_path)
    return _CACHED_MODEL


def predict(url: str) -> dict:
    """
    Extract features from `url` and run ML inference.

    Returns:
        {
          "verdict": "Phishing" | "Legitimate",
          "confidence": float (0-1),
          "features": {name: value, ...}
        }
    """
    try:
        model = _load_model()
    except FileNotFoundError as e:
        logger.warning(str(e))
        return {
            "verdict": "Unknown",
            "confidence": 0.0,
            "features": {},
            "error": str(e),
        }

    raw_features = extract_features(url)
    X = np.array(raw_features).reshape(1, -1)

    prediction = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]

    # Convention: label 1 = phishing, 0 = legitimate
    confidence = float(proba[prediction])
    verdict = "Phishing" if prediction == 1 else "Legitimate"

    return {
        "verdict": verdict,
        "confidence": round(confidence, 4),
        "features": dict(zip(FEATURE_NAMES, raw_features)),
    }
