from pathlib import Path

try:
    from evaluation.yolo_labels import (
        yolo_to_xyxy,
    )
except ImportError:
    from src.evaluation.yolo_labels import (
        yolo_to_xyxy,
    )


def load_yolo_labels(
    label_path,
    image_width,
    image_height,
):

    label_path = Path(label_path)

    ground_truth = []

    if not label_path.exists():

        return ground_truth

    with label_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:

                continue

            parts = line.split()

            if len(parts) != 5:

                continue

            (
                class_id,
                x_center,
                y_center,
                width,
                height,
            ) = map(
                float,
                parts,
            )

            annotation = yolo_to_xyxy(
                class_id,
                x_center,
                y_center,
                width,
                height,
                image_width,
                image_height,
            )

            ground_truth.append(annotation)

    return ground_truth

