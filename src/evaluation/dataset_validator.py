from pathlib import Path


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
}


def get_images(directory):

    directory = Path(directory)

    return [
        path for path in directory.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def validate_split(
    image_directory,
    label_directory,
):

    images = get_images(image_directory)

    label_directory = Path(label_directory)

    image_without_labels = []

    invalid_labels = []

    for image_path in images:

        label_path = label_directory / f"{image_path.stem}.txt"

        if not label_path.exists():

            image_without_labels.append(image_path)

            continue

        with label_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1,
            ):

                line = line.strip()

                if not line:

                    continue

                parts = line.split()

                if len(parts) != 5:

                    invalid_labels.append(
                        (
                            label_path,
                            line_number,
                            "Expected 5 values",
                        )
                    )

                    continue

                try:

                    values = [float(value) for value in parts]

                except ValueError:

                    invalid_labels.append(
                        (
                            label_path,
                            line_number,
                            "Non-numeric value",
                        )
                    )

                    continue

                _, x, y, width, height = values

                if not (
                    0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1
                ):

                    invalid_labels.append(
                        (
                            label_path,
                            line_number,
                            "Invalid normalized coordinates",
                        )
                    )

    return {
        "images": len(images),
        "images_without_labels": (image_without_labels),
        "invalid_labels": (invalid_labels),
    }
