from pathlib import Path

from ultralytics import YOLO


class YOLODetector:

    def __init__(
        self,
        model_path=None,
        confidence=0.25,
        device=None,
    ):

        if model_path is None:
            custom_model = Path(__file__).resolve().parent.parent.parent / "models" / "best.pt"
            if custom_model.exists():
                model_path = str(custom_model)
            else:
                model_path = "yolo11n.pt"

        self.model_path = Path(model_path)

        self.confidence = confidence

        self.device = device

        self.model = YOLO(str(self.model_path))


    def detect(
        self,
        frame,
    ):

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            device=self.device,
            verbose=False,
        )

        return self._parse_results(results)

    def _parse_results(
        self,
        results,
    ):

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()

            confidences = result.boxes.conf.cpu().numpy()

            classes = result.boxes.cls.cpu().numpy()

            names = result.names

            for box, confidence, class_id in zip(
                boxes,
                confidences,
                classes,
            ):

                class_id = int(class_id)

                x1, y1, x2, y2 = box.tolist()

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": names[class_id],
                        "confidence": float(confidence),
                        "box": (
                            float(x1),
                            float(y1),
                            float(x2),
                            float(y2),
                        ),
                    }
                )

        return detections
