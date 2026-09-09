import sys
from pathlib import Path
import time

import cv2

from ultralytics import YOLO

# Add src subdirectories to sys.path so modules can be imported directly
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "tracking"))
sys.path.append(str(BASE_DIR / "zones"))
sys.path.append(str(BASE_DIR))

try:
    from tracker import ObjectTracker
    from zone_manager import ZoneManager
    from border_config import ZONES
    from zone_state import ZoneStateManager
    from intrusion_engine import IntrusionEngine
except ImportError:
    from src.tracking.tracker import ObjectTracker
    from src.zones.zone_manager import ZoneManager
    from src.zones.border_config import ZONES
    from src.zones.zone_state import ZoneStateManager
    from src.intrusion.intrusion_engine import IntrusionEngine



import argparse
import sys
from pathlib import Path
import time

import cv2
from ultralytics import YOLO

# Add src subdirectories to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from src.tracking.tracker import ObjectTracker
    from src.zones.zone_manager import ZoneManager
    from src.zones.border_config import ZONES
    from src.zones.zone_state import ZoneStateManager
    from src.intrusion.intrusion_engine import IntrusionEngine
    from src.core.event_orchestrator import EventOrchestrator
    from src.database.database_service import DatabaseService
    from src.dashboard.dashboard_config import DATABASE_PATH
except ImportError:
    from tracking.tracker import ObjectTracker
    from zones.zone_manager import ZoneManager
    from zones.border_config import ZONES
    from zones.zone_state import ZoneStateManager
    from intrusion.intrusion_engine import IntrusionEngine
    from core.event_orchestrator import EventOrchestrator
    from database.database_service import DatabaseService
    from dashboard.dashboard_config import DATABASE_PATH


DEFAULT_MODEL = "models/best.pt" if Path("models/best.pt").exists() else "yolo11n.pt"
DEFAULT_VIDEO = "data/simulation/sample.mp4"


def run_live_intrusion(video_path: str = DEFAULT_VIDEO, model_path: str = DEFAULT_MODEL, show_gui: bool = True, output_path: str = "outputs/real_world_detection.mp4"):
    print("=" * 70)
    print("       BORDERGUARD AI - REAL WORLD VIDEO INTRUSION PIPELINE")
    print("=" * 70)
    print(f"Input Video Source : {video_path}")
    print(f"Model Path         : {model_path}")

    # Load YOLO Model
    model = YOLO(model_path)

    # Initialize Tracking & Security Components
    tracker = ObjectTracker()
    zone_manager = ZoneManager(ZONES)
    zone_states = ZoneStateManager()
    
    # Initialize Database Persistence
    db_service = DatabaseService(database_path=DATABASE_PATH)
    orchestrator = EventOrchestrator(
        camera_id="CAM-REAL-01",
        db_service=db_service,
        minimum_alert_severity="MEDIUM",
    )

    cap = cv2.VideoCapture(0 if video_path == "0" else video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source: {video_path}")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    frame_count = 0
    event_count = 0
    previous_positions = {}
    previous_time = time.time()

    print(f"Processing Resolution : {frame_width} x {frame_height} @ {fps:.1f} FPS")
    print(f"Output Saved To       : {output_path}")
    print("=" * 70)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            frame_count += 1
            current_time = time.time()
            delta_time = current_time - previous_time
            previous_time = current_time

            # Run YOLO Tracking on clean raw frame FIRST (prevents zone text from being detected as objects)
            results = model.track(
                source=frame,
                tracker="bytetrack.yaml",
                conf=0.35,
                persist=True,
                verbose=False,
            )

            # Draw zone boundaries on frame AFTER inference
            zone_manager.draw_zones(frame)

            if results:
                result = results[0]
                tracked_objects = tracker.update(result, model.names)

                for tracked_obj in tracked_objects:
                    track_id = tracked_obj["track_id"]
                    center = tracked_obj["center"]
                    class_name = tracked_obj["class_name"]
                    confidence = tracked_obj["confidence"]

                    # Zone determination
                    zone = zone_manager.get_zone(center)
                    current_zone = zone.name if zone else "NONE"

                    # Zone state & dwell time
                    state = zone_states.update(track_id, current_zone, current_time)
                    previous_zone = state.previous_zone
                    dwell_time = zone_states.get_dwell_time(track_id, current_time)

                    # Movement vector
                    direction = "STATIONARY"
                    speed = 0.0
                    if track_id in previous_positions:
                        prev = previous_positions[track_id]
                        dx = center[0] - prev[0]
                        dy = center[1] - prev[1]
                        if abs(dx) > abs(dy):
                            direction = "RIGHT" if dx > 0 else "LEFT"
                        elif abs(dy) > 3:
                            direction = "DOWN" if dy > 0 else "UP"
                        if delta_time > 0:
                            speed = ((dx**2 + dy**2) ** 0.5) / delta_time

                    previous_positions[track_id] = center

                    # Process intrusion event orchestrator
                    res = orchestrator.process(
                        track_id=track_id,
                        object_type=class_name,
                        confidence=confidence,
                        previous_zone=previous_zone,
                        current_zone=current_zone,
                        direction=direction,
                        speed=speed,
                        dwell_time=dwell_time,
                        timestamp=current_time,
                    )
                    if res and res.get("event"):
                        event_count += 1
                        evt = res["event"]
                        print(f"🚨 ALERT [{evt.severity}]: Track #{track_id} ({class_name}) - {evt.event_type} in {current_zone} Zone!")

                    # Draw Bounding Boxes & Labels
                    x1, y1, x2, y2 = tracked_obj["bbox"]
                    box_color = (0, 0, 255) if current_zone == "RESTRICTED" else ((0, 255, 255) if current_zone == "WARNING" else (0, 255, 0))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                    cv2.putText(
                        frame,
                        f"TRK-{track_id} ({class_name.upper()}) | {current_zone}",
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        box_color,
                        2,
                    )

            # Footer status
            cv2.putText(
                frame,
                f"BORDERGUARD AI | FRAMES: {frame_count} | EVENTS: {event_count}",
                (20, frame_height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            writer.write(frame)

            if show_gui:
                cv2.imshow("BorderGuard AI - Real World Feed", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("Stopped by user.")
                    break
    finally:
        cap.release()
        writer.release()
        if show_gui:
            cv2.destroyAllWindows()
        orchestrator.close()

    # Convert to HTML5 web-compatible H.264 MP4 format using imageio_ffmpeg
    h264_output_path = output_path.replace(".mp4", "_h264.mp4")
    final_output = output_path
    video_bytes = None

    try:
        import subprocess
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [ffmpeg_exe, "-y", "-i", output_path, "-vcodec", "libx264", "-pix_fmt", "yuv420p", h264_output_path]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        final_output = h264_output_path
    except Exception as conv_err:
        print(f"Warning: Video H264 conversion note: {conv_err}")
        final_output = output_path

    try:
        if Path(final_output).exists():
            with open(final_output, "rb") as vf:
                video_bytes = vf.read()
    except Exception:
        video_bytes = None

    print("=" * 70)
    print("Real-World Video Processing Completed Successfully!")
    print(f"Total Frames Processed : {frame_count}")
    print(f"Total Events Logged    : {event_count}")
    print(f"Annotated Video Output : {final_output}")
    print("=" * 70)

    return {
        "frame_count": frame_count,
        "event_count": event_count,
        "output_path": final_output,
        "video_bytes": video_bytes,
    }


def main():
    parser = argparse.ArgumentParser(description="BorderGuard AI Real World Video Intrusion Pipeline")
    parser.add_argument("--video", type=str, default=DEFAULT_VIDEO, help="Path to input video file or 0 for webcam")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Path to trained YOLO model weights")
    parser.add_argument("--no-display", action="store_true", help="Disable OpenCV GUI window display")
    parser.add_argument("--output", type=str, default="outputs/real_world_detection.mp4", help="Path to output video file")

    args = parser.parse_args()
    run_live_intrusion(
        video_path=args.video,
        model_path=args.model,
        show_gui=not args.no_display,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()

