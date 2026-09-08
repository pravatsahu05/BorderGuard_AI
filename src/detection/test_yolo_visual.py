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
    from detection.yolo_visualizer import (
        draw_detections,
    )
except ImportError:
    from src.detection.yolo_detector import (
        YOLODetector,
    )
    from src.detection.yolo_visualizer import (
        draw_detections,
    )


IMAGE_PATH = Path("data/sample/test_image.jpg")
if not IMAGE_PATH.exists():
    IMAGE_PATH = Path("data/simulation/image..jpg")
if not IMAGE_PATH.exists():
    IMAGE_PATH = Path("data/simulation/background.jpg")

detector = YOLODetector(confidence=0.25)

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise FileNotFoundError(f"Could not load image at {IMAGE_PATH}")

detections = detector.detect(image)

output = draw_detections(
    image,
    detections,
)

output_dir = Path("data/sample")
output_dir.mkdir(parents=True, exist_ok=True)

out_path = output_dir / "yolo_result.jpg"
cv2.imwrite(
    str(out_path),
    output,
)

print(f"Saved YOLO result to {out_path}.")
