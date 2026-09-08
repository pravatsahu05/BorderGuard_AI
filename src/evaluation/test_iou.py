import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from evaluation.iou import calculate_iou
except ImportError:
    from src.evaluation.iou import calculate_iou


box_a = (10, 10, 50, 50)
box_b = (20, 20, 60, 60)

iou = calculate_iou(box_a, box_b)

print("IoU:", round(iou, 3))
