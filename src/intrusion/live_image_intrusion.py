import argparse
import sys
import time
from pathlib import Path
import cv2
from ultralytics import YOLO

# Add src subdirectories to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from src.zones.zone_manager import ZoneManager
    from src.zones.border_config import ZONES
    from src.core.event_orchestrator import EventOrchestrator
    from src.database.database_service import DatabaseService
    from src.dashboard.dashboard_config import DATABASE_PATH
except ImportError:
    from zones.zone_manager import ZoneManager
    from zones.border_config import ZONES
    from core.event_orchestrator import EventOrchestrator
    from database.database_service import DatabaseService
    from dashboard.dashboard_config import DATABASE_PATH


DEFAULT_MODEL = "models/best.pt" if Path("models/best.pt").exists() else "yolo11n.pt"
DEFAULT_IMAGE = "data/simulation/image..jpg"


def run_image_intrusion(
    image_path: str = DEFAULT_IMAGE,
    model_path: str = DEFAULT_MODEL,
    output_path: str = "outputs/real_world_image_detection.jpg",
    conf_threshold: float = 0.25,
):
    print("=" * 70)
    print("       BORDERGUARD AI - REAL WORLD IMAGE INTRUSION PIPELINE")
    print("=" * 70)
    print(f"Input Image Source : {image_path}")
    print(f"Model Weights      : {model_path}")
    print(f"Confidence Cutoff  : {conf_threshold:.2f}")

    # Load YOLO Model
    model = YOLO(model_path)
    zone_manager = ZoneManager(ZONES)

    # Initialize Database Persistence & Orchestrator
    db_service = DatabaseService(database_path=DATABASE_PATH)
    orchestrator = EventOrchestrator(
        camera_id="CAM-IMG-01",
        db_service=db_service,
        minimum_alert_severity="MEDIUM",
    )

    image = cv2.imread(image_path)
    if image is None:
        raise RuntimeError(f"Could not read image from: {image_path}")

    # Resize image to standard resolution 960x540 if different
    height, width = image.shape[:2]
    if width != 960 or height != 540:
        image = cv2.resize(image, (960, 540))
        height, width = 540, 960

    # Run YOLO Inference on clean un-annotated image FIRST
    results = model(image, conf=conf_threshold, verbose=False)

    # Draw Zone Map AFTER inference to prevent on-screen text from confusing YOLO
    zone_manager.draw_zones(image)
    
    detected_objects = []
    active_threats = []
    event_count = 0

    if results and len(results) > 0:
        result = results[0]
        boxes = result.boxes

        for idx, box in enumerate(boxes, start=1):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            box_w = x2 - x1
            box_h = y2 - y1

            # Filter out tiny noise / text artifact boxes (e.g. text letters with w < 10 or h < 15 or area < 150)
            if box_w < 10 or box_h < 15 or (box_w * box_h) < 150:
                continue

            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            confidence = float(box.conf[0])
            cls_id = int(box.cls[0])
            class_name = model.names.get(cls_id, "person")

            # Determine Zone
            zone = zone_manager.get_zone((center_x, center_y))
            current_zone = zone.name if zone else "NONE"

            # Evaluate Intrusion Event
            res = orchestrator.process(
                track_id=idx,
                object_type=class_name,
                confidence=confidence,
                previous_zone="SAFE" if current_zone == "WARNING" else ("WARNING" if current_zone == "RESTRICTED" else "SAFE"),
                current_zone=current_zone,
                direction="DOWN" if current_zone in ["WARNING", "RESTRICTED"] else "STATIONARY",
                speed=45.0 if current_zone in ["WARNING", "RESTRICTED"] else 0.0,
                dwell_time=1.5 if current_zone == "RESTRICTED" else 0.5,
                timestamp=time.time(),
            )

            if current_zone in ["WARNING", "RESTRICTED"]:
                active_threats.append({
                    "id": idx,
                    "type": class_name,
                    "zone": current_zone,
                    "confidence": confidence,
                })

            if res and res.get("event"):
                event_count += 1
                evt = res["event"]
                print(f"🚨 ALERT [{evt.severity}]: Target #{idx} ({class_name}) in {current_zone} Zone!")

            # Box color styling
            box_color = (0, 0, 255) if current_zone == "RESTRICTED" else ((0, 255, 255) if current_zone == "WARNING" else (0, 255, 0))
            cv2.rectangle(image, (x1, y1), (x2, y2), box_color, 2)
            cv2.putText(
                image,
                f"#{idx} {class_name.upper()} ({confidence*100:.0f}%) | {current_zone}",
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                box_color,
                2,
            )

            detected_objects.append({
                "ID": f"#{idx}",
                "Type": class_name,
                "Zone": current_zone,
                "Confidence": f"{confidence*100:.1f}%",
            })

    # Header Overlay Bar at top
    cv2.rectangle(image, (0, 0), (960, 32), (30, 30, 30), -1)
    cv2.putText(
        image,
        f"BORDERGUARD AI | REAL IMAGE DETECTION | TARGETS: {len(detected_objects)} | THREATS: {len(active_threats)}",
        (15, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2,
    )

    # Save Output Image
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, image)

    # Encode Image to Bytes for Streamlit
    success, buffer = cv2.imencode(".jpg", image)
    image_bytes = buffer.tobytes() if success else None

    orchestrator.close()

    print("=" * 70)
    print("Real-World Image Processing Completed Successfully!")
    print(f"Total Objects Detected : {len(detected_objects)}")
    print(f"Active Threat Targets  : {len(active_threats)}")
    print(f"Events Logged          : {event_count}")
    print(f"Output Image Saved To  : {output_path}")
    print("=" * 70)

    return {
        "detections": len(detected_objects),
        "events_count": event_count,
        "threats_count": len(active_threats),
        "output_path": output_path,
        "image_bytes": image_bytes,
        "detected_objects": detected_objects,
    }


def main():
    parser = argparse.ArgumentParser(description="BorderGuard AI Real World Image Intrusion Pipeline")
    parser.add_argument("--image", type=str, default=DEFAULT_IMAGE, help="Path to input image file")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Path to trained YOLO model weights")
    parser.add_argument("--output", type=str, default="outputs/real_world_image_detection.jpg", help="Path to output image file")

    args = parser.parse_args()
    run_image_intrusion(
        image_path=args.image,
        model_path=args.model,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
