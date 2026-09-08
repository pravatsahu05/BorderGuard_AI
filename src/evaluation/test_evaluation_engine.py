import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from evaluation.evaluation_engine import (
        DetectionEvaluationEngine,
    )
except ImportError:
    from src.evaluation.evaluation_engine import (
        DetectionEvaluationEngine,
    )


ground_truth = [
    {
        "class": "person",
        "box": (
            10,
            10,
            50,
            50,
        ),
    },
    {
        "class": "person",
        "box": (
            100,
            100,
            150,
            150,
        ),
    },
]


predictions = [
    {
        "class": "person",
        "box": (
            12,
            12,
            48,
            48,
        ),
    },
    {
        "class": "person",
        "box": (
            102,
            102,
            148,
            148,
        ),
    },
]


engine = DetectionEvaluationEngine()


result = engine.evaluate(
    predictions=predictions,
    ground_truth=ground_truth,
    iou_threshold=0.5,
)


print(
    "Precision:",
    round(
        result.precision,
        3,
    ),
)

print(
    "Recall:",
    round(
        result.recall,
        3,
    ),
)

print(
    "F1:",
    round(
        result.f1_score,
        3,
    ),
)

print(
    "Mean IoU:",
    round(
        result.mean_iou,
        3,
    ),
)
