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


class CrossSensorMatcher:
    """
    Matches detections across RGB and Thermal sensors using Bounding Box IoU.
    """

    def __init__(self, iou_threshold: float = 0.40):
        self.iou_threshold = iou_threshold

    def match(self, rgb_detections: list, thermal_detections: list):
        """
        Pairs detections from RGB and Thermal streams.

        Returns:
            matched_pairs: list of dicts {"rgb": det, "thermal": det, "iou": float}
            unmatched_rgb: list of rgb detections
            unmatched_thermal: list of thermal detections
        """
        matched_pairs = []
        unmatched_rgb = list(rgb_detections)
        unmatched_thermal = list(thermal_detections)

        used_thermal_indices = set()

        for rgb_idx, rgb_det in enumerate(rgb_detections):
            best_iou = 0.0
            best_thermal_idx = None

            rgb_box = rgb_det.get("box") or rgb_det.get("bbox")

            for t_idx, t_det in enumerate(thermal_detections):
                if t_idx in used_thermal_indices:
                    continue

                t_box = t_det.get("box") or t_det.get("bbox")
                iou = calculate_iou(rgb_box, t_box)

                if iou > best_iou:
                    best_iou = iou
                    best_thermal_idx = t_idx

            if best_iou >= self.iou_threshold and best_thermal_idx is not None:
                matched_pairs.append({
                    "rgb": rgb_det,
                    "thermal": thermal_detections[best_thermal_idx],
                    "iou": best_iou
                })
                used_thermal_indices.add(best_thermal_idx)
                if rgb_det in unmatched_rgb:
                    unmatched_rgb.remove(rgb_det)

        unmatched_thermal = [
            t_det for idx, t_det in enumerate(thermal_detections)
            if idx not in used_thermal_indices
        ]

        return {
            "matched_pairs": matched_pairs,
            "unmatched_rgb": unmatched_rgb,
            "unmatched_thermal": unmatched_thermal,
        }


def main():
    print("Testing CrossSensorMatcher...")
    matcher = CrossSensorMatcher(iou_threshold=0.40)
    rgb_dets = [{"class_name": "person", "confidence": 0.85, "box": (100, 100, 200, 300)}]
    thermal_dets = [{"class_name": "person", "confidence": 0.90, "box": (105, 95, 205, 295)}]

    result = matcher.match(rgb_dets, thermal_dets)
    print("Matched pairs:", len(result["matched_pairs"]))
    print("Unmatched RGB:", len(result["unmatched_rgb"]))
    print("Unmatched Thermal:", len(result["unmatched_thermal"]))
    print("CrossSensorMatcher working cleanly.")


if __name__ == "__main__":
    main()
