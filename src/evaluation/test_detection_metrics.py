import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from evaluation.detection_metrics import (
        precision,
        recall,
        f1_score,
    )
except ImportError:
    from src.evaluation.detection_metrics import (
        precision,
        recall,
        f1_score,
    )


tp = 8
fp = 2
fn = 2


p = precision(
    tp,
    fp,
)

r = recall(
    tp,
    fn,
)

f1 = f1_score(
    p,
    r,
)


print(
    "Precision:",
    round(p, 3),
)

print(
    "Recall:",
    round(r, 3),
)

print(
    "F1 Score:",
    round(f1, 3),
)
