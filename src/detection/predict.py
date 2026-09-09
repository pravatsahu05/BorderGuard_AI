import sys
from pathlib import Path
import cv2

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from detection.yolo_detector import YOLODetector
    from detection.yolo_visualizer import draw_detections
except ImportError:
    from src.detection.yolo_detector import YOLODetector
    from src.detection.yolo_visualizer import draw_detections


def predict_image(image_path=None, conf_threshold=0.25):
    if image_path is None:
        # Default test images from dataset
        test_images = list((BASE_DIR / "data" / "borderguard" / "images" / "test").glob("*.jpg"))
        if not test_images:
            test_images = list((BASE_DIR / "data" / "borderguard" / "images" / "test").glob("*.png"))
        if test_images:
            image_path = str(test_images[0])
        else:
            image_path = str(BASE_DIR / "data" / "simulation" / "image..jpg")

    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image {path} not found.")
        return

    print(f"Running detection on: {path}")
    detector = YOLODetector(confidence=conf_threshold)

    image = cv2.imread(str(path))
    if image is None:
        print(f"Error: Unable to read image at {path}")
        return

    detections = detector.detect(image)
    output = draw_detections(image, detections)

    out_dir = BASE_DIR / "outputs" / "predictions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"pred_{path.stem}.jpg"
    cv2.imwrite(str(out_path), output)

    print("=" * 50)
    print("DETECTION RESULTS")
    print("=" * 50)
    print(f"Total Detections Found: {len(detections)}")
    for i, det in enumerate(detections, 1):
        box = [round(b, 1) for b in det['box']]
        print(f" {i}. [{det['class_name'].upper()}] Confidence: {det['confidence']*100:.1f}% | Box: {box}")

    print(f"\nAnnotated image saved to: {out_path}")
    print("=" * 50)


if __name__ == "__main__":
    img_arg = sys.argv[1] if len(sys.argv) > 1 else None
    conf_arg = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    predict_image(img_arg, conf_arg)
