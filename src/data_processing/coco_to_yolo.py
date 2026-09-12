import json
from pathlib import Path


def convert_bbox(
    bbox,
    image_width,
    image_height,
):

    x, y, width, height = bbox

    x_center = (
        x + width / 2
    ) / image_width

    y_center = (
        y + height / 2
    ) / image_height

    normalized_width = (
        width / image_width
    )

    normalized_height = (
        height / image_height
    )

    return (
        x_center,
        y_center,
        normalized_width,
        normalized_height,
    )


def convert_coco_to_yolo(
    annotation_file,
    output_label_dir,
    target_category_ids,
):

    annotation_file = Path(
        annotation_file
    )

    output_label_dir = Path(
        output_label_dir
    )

    output_label_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with annotation_file.open(
        "r",
        encoding="utf-8",
    ) as file:

        coco = json.load(file)

    images = {
        image["id"]: image
        for image in coco["images"]
    }

    labels_by_image = {}

    for annotation in coco[
        "annotations"
    ]:

        category_id = annotation[
            "category_id"
        ]

        if (
            category_id
            not in target_category_ids
        ):
            continue

        image_id = annotation[
            "image_id"
        ]

        image_info = images.get(
            image_id
        )

        if image_info is None:
            continue

        bbox = annotation.get(
            "bbox"
        )

        if (
            not bbox
            or len(bbox) != 4
        ):
            continue

        (
            x_center,
            y_center,
            width,
            height,
        ) = convert_bbox(
            bbox,
            image_info["width"],
            image_info["height"],
        )

        line = (
            f"0 "
            f"{x_center:.6f} "
            f"{y_center:.6f} "
            f"{width:.6f} "
            f"{height:.6f}"
        )

        labels_by_image.setdefault(
            image_id,
            [],
        ).append(line)

    for image_id, labels in (
        labels_by_image.items()
    ):

        image_info = images[
            image_id
        ]

        image_name = Path(
            image_info["file_name"]
        ).stem

        output_file = (
            output_label_dir
            / f"{image_name}.txt"
        )

        output_file.write_text(
            "\n".join(labels),
            encoding="utf-8",
        )

    return len(
        labels_by_image
    )