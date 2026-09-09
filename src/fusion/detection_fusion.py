



class DetectionFusion:
    """
    Combines detections from RGB and thermal sensors.

    This is a decision-level fusion component.
    """

    def __init__(
        self,
        iou_threshold=0.50,
        confidence_threshold=0.25,
    ):
        self.iou_threshold = iou_threshold
        self.confidence_threshold = confidence_threshold

    @staticmethod
    def calculate_iou(box_a, box_b):
        """
        Calculate Intersection over Union.
        """

        ax1, ay1, ax2, ay2 = box_a
        bx1, by1, bx2, by2 = box_b

        intersection_x1 = max(ax1, bx1)
        intersection_y1 = max(ay1, by1)
        intersection_x2 = min(ax2, bx2)
        intersection_y2 = min(ay2, by2)

        intersection_width = max(
            0.0,
            intersection_x2 - intersection_x1,
        )

        intersection_height = max(
            0.0,
            intersection_y2 - intersection_y1,
        )

        intersection_area = intersection_width * intersection_height

        area_a = max(
            0.0,
            ax2 - ax1,
        ) * max(
            0.0,
            ay2 - ay1,
        )

        area_b = max(
            0.0,
            bx2 - bx1,
        ) * max(
            0.0,
            by2 - by1,
        )

        union_area = area_a + area_b - intersection_area

        if union_area <= 0:
            return 0.0

        return intersection_area / union_area

    @staticmethod
    def weighted_box(
        box_a,
        confidence_a,
        box_b,
        confidence_b,
    ):
        """
        Calculate confidence-weighted bounding box.
        """

        total_confidence = confidence_a + confidence_b

        if total_confidence <= 0:
            return box_a

        return tuple(
            (a * confidence_a + b * confidence_b) / total_confidence
            for a, b in zip(
                box_a,
                box_b,
            )
        )

    def fuse(
        self,
        rgb_detections,
        thermal_detections,
    ):
        """
        Fuse RGB and thermal detections.

        Returns a list of final detections.
        """

        final_detections = []

        used_thermal = set()

        for rgb_detection in rgb_detections:

            best_match = None
            best_iou = 0.0
            best_index = None

            for index, thermal_detection in enumerate(thermal_detections):

                if index in used_thermal:
                    continue

                if rgb_detection["class_id"] != thermal_detection["class_id"]:
                    continue

                iou = self.calculate_iou(
                    rgb_detection["box"],
                    thermal_detection["box"],
                )

                if iou > best_iou:
                    best_iou = iou
                    best_match = thermal_detection
                    best_index = index

            # --------------------------------------------------
            # Matching detection from both sensors.
            # --------------------------------------------------

            if best_match is not None and best_iou >= self.iou_threshold:

                rgb_confidence = rgb_detection["confidence"]

                thermal_confidence = best_match["confidence"]

                fused_confidence = max(
                    rgb_confidence,
                    thermal_confidence,
                )

                fused_box = self.weighted_box(
                    rgb_detection["box"],
                    rgb_confidence,
                    best_match["box"],
                    thermal_confidence,
                )

                final_detections.append(
                    {
                        "class_id": rgb_detection["class_id"],
                        "class_name": rgb_detection["class_name"],
                        "confidence": fused_confidence,
                        "box": fused_box,
                        "source": "rgb+thermal",
                        "iou": best_iou,
                    }
                )

                used_thermal.add(best_index)

            # --------------------------------------------------
            # RGB-only detection.
            # --------------------------------------------------

            else:

                final_detections.append(
                    {
                        **rgb_detection,
                        "source": "rgb",
                        "iou": 0.0,
                    }
                )

        # ------------------------------------------------------
        # Add thermal-only detections.
        # ------------------------------------------------------

        for index, thermal_detection in enumerate(thermal_detections):

            if index in used_thermal:
                continue

            final_detections.append(
                {
                    **thermal_detection,
                    "source": "thermal",
                    "iou": 0.0,
                }
            )

        return [
            detection
            for detection in final_detections
            if detection["confidence"] >= self.confidence_threshold
        ]
