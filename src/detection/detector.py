from pathlib import Path

from ultralytics import YOLO


class ObjectDetector:
    """
    Wrapper around the YOLO object detection model.
    """

    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        confidence_threshold: float = 0.40,
    ):
        """
        Initialize the object detector.

        Parameters:
            model_path:
                Path/name of the YOLO model.

            confidence_threshold:
                Minimum confidence required for a detection.
        """

        self.model_path = model_path
        self.confidence_threshold = confidence_threshold

        # Load the YOLO model.
        self.model = YOLO(model_path)

    def detect(self, frame):
        """
        Detect objects in a single frame.

        Parameters:
            frame:
                OpenCV image/frame.

        Returns:
            List of detected objects.
        """

        results = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            verbose=False,
        )

        detections = []

        # YOLO returns a collection of results.
        for result in results:

            # If there are no detected boxes,
            # move to the next result.
            if result.boxes is None:
                continue

            for box in result.boxes:

                # Bounding box coordinates.
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Confidence score.
                confidence = float(box.conf[0])

                # Class ID.
                class_id = int(box.cls[0])

                # Class name.
                class_name = self.model.names[class_id]

                detection = {
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": (
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2),
                    ),
                }

                detections.append(detection)

        return detections
