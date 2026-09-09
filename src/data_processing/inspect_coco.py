import json
import sys
from pathlib import Path

DEFAULT_ANNOTATION_PATHS = [
    "data/raw/FLIR/images_thermal_train/coco.json",
    "data/raw/FLIR/images_rgb_train/coco.json",
]

if len(sys.argv) > 1:
    annotation_path = Path(sys.argv[1])
else:
    annotation_path = None
    for default_p in DEFAULT_ANNOTATION_PATHS:
        p = Path(default_p)
        if p.exists():
            annotation_path = p
            print(f"No annotation file specified. Defaulting to: {annotation_path}\n")
            break

if annotation_path is None or not annotation_path.exists():
    print("Error: Annotation file not found.")
    print("Usage: python src/data_processing/inspect_coco.py <path_to_coco_json>")
    sys.exit(1)

with open(
    annotation_path,
    "r",
    encoding="utf-8",
) as file:
    data = json.load(file)



print("=" * 60)
print("CATEGORIES")
print("=" * 60)


for category in data.get(
    "categories",
    [],
):

    print(f"ID: {category['id']} | " f"Name: {category['name']}")


print()
print(
    "Images:",
    len(
        data.get(
            "images",
            [],
        )
    ),
)

print(
    "Annotations:",
    len(
        data.get(
            "annotations",
            [],
        )
    ),
)
