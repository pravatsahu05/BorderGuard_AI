import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

import cv2

try:
    from detection.yolo_detector import (
        YOLODetector,
    )
except ImportError:
    from src.detection.yolo_detector import (
        YOLODetector,
    )


IMAGE_PATH = "data/simulation/image..jpg"
if not Path(IMAGE_PATH).exists():
    IMAGE_PATH = "data/simulation/background.jpg"

detector = YOLODetector(confidence=0.25)

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise FileNotFoundError(f"Could not load: {IMAGE_PATH}")

detections = detector.detect(image)

print(f"Detections: {len(detections)}")

for detection in detections:
    print(detection)
